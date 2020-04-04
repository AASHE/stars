from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.views.generic import (FormView, CreateView, TemplateView,
                                  RedirectView)
from django.template.response import TemplateResponse

from extra_views import CreateWithInlinesView
from logical_rules.mixins import RulesMixin

from stars.apps.credits.models import Category, Subcategory, Credit
from stars.apps.credits.views import StructureMixin
from stars.apps.institutions.forms import (SubmissionSelectForm,
                                           SubmissionInquiryForm,
                                           CreditSubmissionInquiryFormSet,
                                           DataCorrectionRequestForm)
from stars.apps.institutions.models import Institution, Subscription
from stars.apps.notifications.models import EmailTemplate
from stars.apps.submissions.models import (DataCorrectionRequest,
                                           SubmissionInquiry,
                                           SUBMISSION_STATUSES)
from stars.apps.submissions.views import SubmissionStructureMixin
from stars.apps.submissions.tasks import (
    build_excel_export, build_pdf_export, build_certificate_export)
from stars.apps.download_async_task.views import (StartExportView,
                                                  DownloadExportView)


class InstitutionStructureMixin(StructureMixin):
    """
        Extends the StructureMixin to work with Institutions
    """

    def __init__(self, *args, **kwargs):
        super(InstitutionStructureMixin, self).__init__(*args, **kwargs)

    def update_context_callbacks(self):
        super(InstitutionStructureMixin, self).update_context_callbacks()
        self.add_context_callback("get_institution")
        self.add_context_callback("get_subscription")
        self.add_context_callback("get_payment")

    def get_institution(self, use_cache=True):
        """
            Attempts to get an institution.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        return self.get_obj_or_call(
            cache_key='institution',
            kwargs_key='institution_slug',
            klass=Institution,
            property="slug",
            use_cache=use_cache
        )

    def get_subscription(self, use_cache=True):
        """
            Attempts to get an institution's subscription.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_institution():
            return self.get_obj_or_call(
                cache_key='subscription',
                kwargs_key='subscription_id',
                klass=self.get_institution().subscription_set.all(),
                property="id",
                use_cache=use_cache)
        return None

    def get_payment(self, use_cache=True):
        """
            Attempts to get an institution's subscription.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_subscription():
            return self.get_obj_or_call(
                cache_key='payment',
                kwargs_key='payment_id',
                klass=self.get_subscription().subscriptionpayment_set.all(),
                property="id",
                use_cache=use_cache)
        return None


class SortableTableView(TemplateView):
    """
        A class-based view for displaying a sortable list of objects
        The extending class should set two property variables:
            `columns` and `default_key`
        And override the `get_queryset` method
    """

    columns = None  # This is coupled to the template :(
    default_key = None  # The default column to sort on

    def __init__(self, *args, **kwargs):

        return super(SortableTableView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """ Add/update any context variables """
        _context = super(SortableTableView, self).get_context_data(**kwargs)

        _context.update({'sort_columns': self.columns,
                         'default_key': self.default_key})

        (_context['sort_key'],
         _context['rev'],
         _context['object_list']) = self.get_object_list()

        return _context

    def get_queryset(self):
        """ Gets the base queryset for the object_list """
        raise NotImplementedError, "Please override this method"

    def get_object_list(self):
        """
            Returns a queryset based on the GET Parameters
            Also returns the selected `sort_key`
            and `rev`, a "-" or empty string indicating the reverse sort order
        """

        sort_key = None
        asc = ""
        rev = ""
        queryset = self.get_queryset()

        if 'sort' in self.request.GET:
            if self.request.GET['sort'][0] == '-':
                asc = '-'
                rev = ''
                sort_key = self.request.GET['sort'][1:]
            else:
                asc = ''
                rev = '-'
                sort_key = self.request.GET['sort']
        else:
            sort_key = self.default_key
            rev = self.default_rev
            if rev == '':
                asc = '-'

        for col in self.columns:
            if col['key'] == sort_key:
                if col['key'] == 'country':
                    queryset = queryset.order_by(
                        "%s%s" %
                        (asc, col['sort_field']),
                        'ms_institution__state',
                        self.secondary_order_field)
                else:
                    queryset = queryset.order_by(
                        "%s%s" %
                        (asc, col['sort_field']),
                        self.secondary_order_field)
                break

        return (sort_key, rev, queryset)


class SortableTableViewWithInstProps(SortableTableView):
    """
        Extends SortableTableView to include institutional
        properties from the list
    """

    def get_context_data(self, **kwargs):
        """
            update the context with the # of members and charter participants
        """

        _context = super(SortableTableViewWithInstProps,
                         self).get_context_data(**kwargs)

        inst_list = []
        inst_count = 0
        member_count = 0
        charter_count = 0
        pilot_count = 0
        international_count = 0
        for i in self.get_queryset():
            if i.id not in inst_list:
                inst_list.append(i.id)
                inst_count += 1
                if i.charter_participant:
                    charter_count += 1
                if i.is_member:
                    member_count += 1
                if i.is_pilot_participant:
                    pilot_count += 1
                if i.international:
                    international_count += 1

        _context['inst_count'] = inst_count
        _context['member_count'] = member_count
        _context['charter_count'] = charter_count
        _context['pilot_count'] = pilot_count
        _context['international_count'] = international_count
        _context['display_version'] = "2.0"
        return _context


class ActiveInstitutions(SortableTableViewWithInstProps):
    """
        Extending SortableTableView to show a sortable list
        of all active participants
    """

    template_name = "institutions/institution_list_active.html"
    default_key = 'name'
    default_rev = '-'
    secondary_order_field = 'name'
    columns = [{'key': 'name',
                'sort_field': 'name',
                'title': 'Institution'},
               {'key': 'rating',
                'sort_field': 'current_rating',
                'title': 'Current Rating'}]

    def get_queryset(self):
        """
            Get the submission sets for all institutions

            Institutions shouldn't show up twice
                - rated institutions show their rating
                - unrated institutions show their next due date
        """
        return Institution.objects.filter(is_participant=True)


class RatedInstitutions(SortableTableViewWithInstProps):
    """
        Extending SortableTableView to show a sortable list
        of all active submissionsets
    """

    template_name = "institutions/institution_list_rated.html"
    default_key = 'name'
    default_rev = '-'
    secondary_order_field = 'name'
    columns = [{'key': 'name',
                'sort_field': 'name',
                'title': 'Institution'},
               {'key': 'version',
                'sort_field': 'rated_submission__creditset__version',
                'title': 'Version'},
               {'key': 'rating',
                'sort_field': 'current_rating',
                'title': 'Rating'},
               {'key': 'date_submitted',
                'sort_field': 'rated_submission__date_submitted',
                'title': 'Submission Date'}]

    def get_queryset(self):
        return Institution.objects.get_rated().select_related(
            'rated_submission').select_related('rated_submission__creditset')


class ParticipantReportsView(SortableTableViewWithInstProps):
    """
        Extending SortableTableView to show a sortable list
        of all participants and reports.
    """

    template_name = "institutions/institution_participant_reports_list.html"
    default_key = 'date_submitted'
    default_rev = ''
    secondary_order_field = 'name'
    columns = [{'key': 'name',
                'sort_field': 'name',
                'title': 'Institution'},
               {'key': 'country',
                'sort_field': 'country',
                'title': 'Location'},
               {'key': 'version',
                'sort_field': 'rated_submission__creditset__version',
                'title': 'Version'},
               {'key': 'rating',
                'sort_field': 'current_rating',
                'title': 'Rating'},
               {'key': 'date_submitted',
                'sort_field': 'rated_submission__date_submitted',
                'title': 'Submission Date'}]

    def get_queryset(self):
        qs = Institution.objects.get_participants_and_reports()
        qs = qs.select_related('rated_submission')
        qs = qs.select_related('rated_submission__creditset')
        qs = qs.select_related('ms_institution__state')
        return qs


class InstitutionScorecards(InstitutionStructureMixin, TemplateView):
    """
    Provides a list of available reports for an institution.

    Show all rated reports, and if the user has privileges with that
    institution, they can see the preview of the current submission too

    see submissions/rules.py: user_can_preview_submission
    """
    template_name = 'institutions/scorecards/list.html'

    def get_context_data(self, **kwargs):
        _context = super(InstitutionScorecards,
                         self).get_context_data(**kwargs)

        institution = self.get_institution()

        qs = institution.submissionset_set.filter(is_visible=True)
        qs = qs.filter(status='r').order_by("-date_submitted")

        if qs.count() < 1:
            raise Http404

        _context.update({'submission_sets': qs,
                         'institution': institution})

        return _context

    def render_to_response(self, context, **response_kwargs):
        """
        If there's only one submission set to show, just jump
        to its scorecard rather than show a list with it as
        the only item in it.
        """
        if len(context['submission_sets']) is 1:
            return HttpResponseRedirect(
                context['submission_sets'][0].get_scorecard_url())
        else:
            return super(InstitutionScorecards, self).render_to_response(
                context, **response_kwargs)


def get_submissions_for_scorecards(institution):
    """
    Scorecards are only shown for pending, rated submissions and submissions
    under review.
    """
    return (
        institution.submissionset_set.filter(
            status=SUBMISSION_STATUSES["PENDING"]) |
        institution.submissionset_set.filter(
            status=SUBMISSION_STATUSES["RATED"]) |
        institution.submissionset_set.filter(
            status=SUBMISSION_STATUSES["REVIEW"]))


class RedirectOldScorecardCreditURLsView(InstitutionStructureMixin,
                                         SubmissionStructureMixin,
                                         RedirectView):
    """
    Redirects old Scorecard Credit URLs to their new equivalent.

    Old Scorecard Credit URLs are made like this:

        /<institution.slug>
        /<submissionset.[date_submitted|id]>
        /<category.id>
        /<subcategory.id>
        /<credit.id>

    New Scorecard Credit URLs look like this:

        /<institution.slug>
        /<submissionset.[date_submitted|id]>
        /<category.abbreviation>
        /<subcategory.slug>
        /<credit.identifier>
    """

    def get_redirect_url(self, **kwargs):
        institution = self.get_institution()
        submissionset = self.get_submissionset()
        category = get_object_or_404(Category, id=kwargs['category_id'])
        subcategory = get_object_or_404(Subcategory,
                                        id=kwargs['subcategory_id'])
        credit = get_object_or_404(Credit, id=kwargs['credit_id'])
        return reverse(
            'institutions:scorecard-credit',
            kwargs={
                'institution_slug': institution.slug,
                'submissionset': submissionset.date_submitted,
                'category_abbreviation': category.abbreviation,
                'subcategory_slug': subcategory.slug,
                'credit_identifier': credit.identifier
            }
        )

    def get_object_list(self):
        return get_submissions_for_scorecards(
            institution=self.get_institution())


class ScorecardView(RulesMixin,
                    InstitutionStructureMixin,
                    SubmissionStructureMixin,
                    TemplateView):
    """
        Browse credits according to submission in the credit browsing view
    """
    http_method_names = ['get']

    def get_object_list(self):
        return get_submissions_for_scorecards(
            institution=self.get_institution())

    def update_logical_rules(self):

        super(ScorecardView, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'user_can_view_submission',
            'param_callbacks':
            [
                ('user', "get_request_user"),
                ('submission', "get_submissionset")
            ],
        })

    def get_context_data(self, **kwargs):
        """ Expects arguments for category_id/subcategory_id/credit_id """
        _context = super(ScorecardView, self).get_context_data(**kwargs)

        ss = self.get_submissionset()

        url_prefix = ss.get_scorecard_url()

        _context['outline'] = self.get_creditset_nav(url_prefix=url_prefix)

        _context['score'] = ss.get_STARS_score()

        rating = ss.get_STARS_rating()
        _context['rating'] = rating

        _context['preview'] = False
        if not ss.status == 'r':
            _context['preview'] = True

        _context['show_column_charts'] = self.show_column_charts_or_not(ss)

        return _context

    def show_column_charts_or_not(self, submissionset):
        """Should we show the column charts for this SubmissionSet?

        Only for rated reports and for folks with FULL_ACCESS."""
        if (submissionset.creditset.has_basic_benchmarking_feature and
            submissionset.institution.access_level == Subscription.FULL_ACCESS and
            submissionset.rating != 'Reporter'):
            return True
        return False

    def get_category_url(self, category, url_prefix):
        """ The default link for a category. """
        return "%s%s" % (url_prefix, category.get_browse_url())

    def get_subcategory_url(self, subcategory, url_prefix):
        """ The default link for a category. """
        return "%s%s" % (url_prefix, subcategory.get_browse_url())

    def get_credit_url(self, credit, url_prefix):
        """ The default credit link. """
        return "%s%s" % (url_prefix, credit.get_browse_url())


class ScorecardSummary(ScorecardView):
    template_name = 'institutions/scorecards/summary.html'


class ScorecardCredit(ScorecardView):
    template_name = 'institutions/scorecards/credit.html'


class ScorecardCreditDocumentation(ScorecardView):
    template_name = 'institutions/scorecards/credit_documentation.html'


class ExportRules(RulesMixin):

    def update_logical_rules(self):

        super(ExportRules, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'user_can_view_export',
            'param_callbacks': [('user', "get_request_user"),
                                ('submission', "get_submissionset")]})

    def get_object_list(self):
        """
            Prevents snapshots from being returned
        """
        return self.get_institution().submissionset_set.exclude(status='f')


class ExcelExportView(ExportRules,
                      InstitutionStructureMixin,
                      SubmissionStructureMixin,
                      StartExportView):

    export_method = build_excel_export
    url_prefix = "excel/"

    def get_task_params(self):
        return self.get_submissionset().id


class ExcelDownloadView(ExportRules,
                        InstitutionStructureMixin,
                        SubmissionStructureMixin,
                        DownloadExportView):
    content_type = 'application/vnd.ms-excel'
    extension = "xls"

    def get_filename(self):
        return self.get_submissionset().institution.slug[:64]


class PDFExportView(ExportRules,
                    InstitutionStructureMixin,
                    SubmissionStructureMixin,
                    StartExportView):
    """
        Displays an exported PDF version of the selected report.
    """

    export_method = build_pdf_export
    url_prefix = "pdf/"

    def get_task_params(self):
        return self.get_submissionset().id


class PDFDownloadView(ExportRules,
                      InstitutionStructureMixin,
                      SubmissionStructureMixin,
                      DownloadExportView):
    content_type = 'application/pdf'
    extension = "pdf"

    def get_filename(self):
        return self.get_submissionset().institution.slug[:64]


class CertificateExportView(InstitutionStructureMixin,
                            SubmissionStructureMixin,
                            StartExportView):
    """
        Displays an exported Certificate version of the selected report.
    """

    export_method = build_certificate_export
    url_prefix = "cert/"

    def get_task_params(self):
        ss = self.get_submissionset()
        print "Param: %d" % ss.id
        return ss.id

    def get_object_list(self):
        ss_list = super(CertificateExportView, self).get_object_list()
        return ss_list.filter(status="r")


class ScorecardCertPreview(ScorecardView):
    template_name = 'institutions/pdf/certificate.html'

    def get_context_data(self, **kwargs):
        """ Expects arguments for category_id/subcategory_id/credit_id """
        _context = super(ScorecardCertPreview,
                         self).get_context_data(**kwargs)

        from django.conf import settings

        return {
            'ss': self.get_submissionset(),
            'project_path': settings.PROJECT_PATH,
            'preview': True
        }


class CertificateDownloadView(InstitutionStructureMixin,
                              SubmissionStructureMixin,
                              DownloadExportView):
    content_type = 'application/pdf'
    extension = "pdf"

    def get_filename(self):
        # @TODO - get the date of submission into the filename
        return "%s" % (self.get_submissionset().rating)

    def get_object_list(self):
        ss_list = super(CertificateDownloadView, self).get_object_list()
        return ss_list.filter(status="r")


class ScorecardInternalNotesView(ScorecardView):
    """
        An extension of the scorecard view that requires permission
        on the selected institution.
    """

    def update_logical_rules(self):

        super(ScorecardInternalNotesView, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'user_has_view_access',
                    'param_callbacks':
                        [
                            ('user', "get_request_user"),
                            ('submission', "get_institution")
                        ],
        })

    template_name = 'institutions/scorecards/internal_notes.html'


class DataCorrectionView(RulesMixin,
                         InstitutionStructureMixin,
                         SubmissionStructureMixin,
                         CreateView):
    """
        Provides a form for institutions to request a data correction
    """
    template_name = "institutions/data_correction_request/new.html"
    form_class = DataCorrectionRequestForm

    def get_object_list(self):
        return get_submissions_for_scorecards(
            institution=self.get_institution())

    def update_logical_rules(self):
        super(DataCorrectionView, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'user_is_institution_admin',
                    'param_callbacks':
                        [
                            ('user', "get_request_user"),
                            ('submission', "get_institution")
                        ],
        })

    def form_valid(self, form):
        self.object = form.save()

        et = EmailTemplate.objects.get(slug="data_correction_request")
        context = {
            "correction": self.object,
            "submissionset": self.get_submissionset()
        }
        et.send_email(["stars@aashe.org"], context)

        _context = self.get_context_data()
        _context.update(context)

        return TemplateResponse(
            self.request,
            "institutions/data_correction_request/success.html",
            _context)

    def get_form_kwargs(self):
        kwargs = super(DataCorrectionView, self).get_form_kwargs()
        kwargs['instance'] = DataCorrectionRequest(
            user=self.request.user,
            reporting_field=self.get_fieldsubmission())
        return kwargs


class SubmissionInquirySelectView(FormView):
    """
        Provides a form for people to dispute the submission
        for a particular institution.
    """

    template_name = "institutions/inquiries/select_submission.html"
    form_class = SubmissionSelectForm

    def form_valid(self, form):
        ss = form.cleaned_data['institution']
        return HttpResponseRedirect("%sinquiry/" % ss.get_scorecard_url())


class SubmissionInquiryView(InstitutionStructureMixin,
                            SubmissionStructureMixin,
                            CreateWithInlinesView):
    """
        Allows a visitor to submit disputes for several credits at once
    """
    model = SubmissionInquiry
    form_class = SubmissionInquiryForm
    inlines = [CreditSubmissionInquiryFormSet]
    template_name = "institutions/inquiries/new.html"

    def get_object_list(self):
        return get_submissions_for_scorecards(
            institution=self.get_institution())

    def get_context_data(self, **kwargs):
        _c = super(SubmissionInquiryView, self).get_context_data(**kwargs)
        return _c

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(SubmissionInquiryView, self).get_form_kwargs()
        ss = self.get_submissionset()
        kwargs.update({'instance': SubmissionInquiry(submissionset=ss)})
        return kwargs

    def forms_invalid(self, form, inlines):
        return super(SubmissionInquiryView, self).forms_invalid(form, inlines)

    def forms_valid(self, form, inlines):
        """
        If the form and formsets are valid, save the associated models.
        """

        _context = self.get_context_data()
        self.object = form.save()
        for formset in inlines:
            formset.save()

        # Send confirmation email
        # email_to = [_context['institution'].contact_email]
        # if not self.object.anonymous and self.object.email_address:
        #     email_to.append(self.object.email_address)
        #
        # Used to send email directly to liaison, but STARS
        # admins want it sent to them only now, so they may
        # ensure the request is valid before forwarding on
        # to liaison.
        email_to = ["stars@aashe.org"]

        et = EmailTemplate.objects.get(
            slug="submission_accuracy_inquiry")
        email_context = {
            "inquiry": self.object,
            "institution": self.object.submissionset.institution}
        et.send_email(email_to, email_context)

        return TemplateResponse(self.request,
                                "institutions/inquiries/success.html",
                                context=_context)
