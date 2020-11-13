import collections
import re
import json

from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.views.generic import UpdateView, View

from stars.apps.credits.views import CreditsetStructureMixin
from stars.apps.institutions.models import Institution
from stars.apps.submissions.forms import CreditSubmissionStatusUpdateForm
from stars.apps.submissions.models import (CreditUserSubmission,
                                           DocumentationFieldSubmission)


class SubmissionStructureMixin(CreditsetStructureMixin):
    """
        Extends the creditset structure to work with SubmissionSets

        URL structure can be one of the following
            /institution_slug/submissionset/category_abbreviation/subcategory_slug/credit_number/

            <submissionset> can be either an ID or a date (####-##-##)
    """

    def update_context_callbacks(self):
        super(SubmissionStructureMixin, self).update_context_callbacks()
        self.add_context_callback("get_submissionset")
        self.add_context_callback("get_categorysubmission")
        self.add_context_callback("get_subcategorysubmission")
        self.add_context_callback("get_creditsubmission")
        self.add_context_callback("get_fieldsubmission")

    def get_object_list(self):
        """
            Returns a list of objects to use as filters for get_obj_or_call
        """
        return self.get_institution().submissionset_set.all()

    def get_submissionset(self, use_cache=True):
        """
            Attempts to get a submissionset using the kwargs.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        property = 'pk'
        pattern = "^\d{4}-\d{2}-\d{2}$"
        if re.match(pattern, self.kwargs['submissionset']):
            property = 'date_submitted'

        return self.get_obj_or_call(
            cache_key='submissionset',
            kwargs_key='submissionset',
            klass=self.get_object_list(),
            property=property,
            use_cache=use_cache
        )

    def get_creditset(self):
        """
            override get_creditset to extract from submissionset
        """
        if self.get_submissionset():
            return self.get_submissionset().creditset

    def get_categorysubmission(self):
        """
            Attempts to get a categorysubmission.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_submissionset():
            return self.get_obj_or_call(
                cache_key='category_submission',
                kwargs_key="category_abbreviation",
                klass=self.get_submissionset().categorysubmission_set.all(),
                property='category__abbreviation'
            )

    def get_subcategorysubmission(self):
        """
            Attempts to get a subcategorysubmission.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_categorysubmission():
            return self.get_obj_or_call(
                cache_key='subcategory_submission',
                kwargs_key="subcategory_slug",
                klass=self.get_categorysubmission().subcategorysubmission_set.all(),
                property='subcategory__slug'
            )

    def get_creditsubmission(self):
        """
            Attempts to get a creditusersubmission.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_subcategorysubmission():
            return self.get_obj_or_call(
                cache_key='credit_submission',
                kwargs_key="credit_identifier",
                klass=self.get_subcategorysubmission().creditusersubmission_set.all(),
                property='credit__identifier'
            )

    def get_fieldsubmission(self):
        """
            Attempts to get a submission field.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        cache_key = "field_submission"
        obj = self.get_structure_object(cache_key)

        if not obj and self.get_creditsubmission() and self.get_field():
            klass = DocumentationFieldSubmission.get_field_class(
                self.get_field())
            obj = get_object_or_404(
                klass,
                documentation_field=self.get_field(),
                credit_submission=self.get_creditsubmission())
            self.set_structure_object(cache_key, obj)
        return obj

    def get_current_selection(self):
        """
            Determine which component is newest
        """
        key = 'current'
        current = self.get_structure_object(key)
        if not current:
            current = self.get_submissionset()
            if self.get_categorysubmission():
                current = self.get_categorysubmission()
                if self.get_subcategorysubmission():
                    current = self.get_subcategorysubmission()
                    if self.get_creditsubmission():
                        current = self.get_creditsubmission()
        self.set_structure_object(key, current)
        return current

    def get_submissionset_nav(self, url_prefix="/"):
        """
            Generates the outline list for the django-collapsing-menu
        """
        cache_key = "submissionset_outline_%d" % self.get_submissionset().id
        outline = cache.get(cache_key)
        if outline:
            return outline
        outline = []

        # Top Level: Categories
        for catsub in self.get_submissionset().categorysubmission_set.all():
            catsub_item = {
                'title': catsub.category.title,
                'children': [],
                'attrs': {'id': "outline_cat_%d" % catsub.id}
            }

            # Second Level: Subcategories
            for subcatsub in catsub.subcategorysubmission_set.all():
                subcatsub_item = {
                    'title': subcatsub.subcategory.title,
                    'children': [],
                    'attrs': {'id': "outline_sub_%d" % subcatsub.id}
                }

                # Third Level: T1 Credits
                for creditsub in subcatsub.creditusersubmission_set.all().filter(credit__type='t1'):
                    creditsub_item = {
                        'title': creditsub.credit.__unicode__(),
                        'url': self.get_creditsubmission_url(
                            creditsub, url_prefix),
                        'attrs': {'id': "outline_cred_%d" % creditsub.id}
                    }
                    subcatsub_item['children'].append(creditsub_item)

                # Fourth Level: T2 Credits
                t2_qs = subcatsub.creditusersubmission_set.all().filter(
                    credit__type='t2')
                if t2_qs.count() > 0:
                    t2_header_item = {
                        'title': "Tier 2 Credits",
                        'children': []
                    }
                    for t2 in t2_qs:
                        t2_item = {
                            'title': t2.__unicode__(),
                            'url': self.get_creditsubmission_url(
                                t2, url_prefix),
                            'attrs': {'id': "outline_t2_%d" % t2.id}
                        }

                        t2_header_item['children'].append(t2_item)

                    subcatsub_item['children'].append(t2_header_item)

                catsub_item['children'].append(subcatsub_item)

            outline.append(catsub_item)

        cache.set(cache_key, outline, 60 * 60 * 48)  # cache for 48 hours
        return outline

    def get_creditsubmission_url(self, creditsubmission, url_prefix="/"):
        """ The default creditsubmission link. """
        credit = creditsubmission.credit
        subcategory = creditsubmission.credit.subcategory
        category = creditsubmission.credit.subcategory.category
        submissionset = creditsubmission.get_submissionset()
        return ("/tool/{institution_slug}/submission/{submissionset_id}"
                "/{category_abbreviation}/{subcategory_title}"
                "/{credit_identifier}/").format(
                    institution_slug=submissionset.institution.slug,
                    submissionset_id=submissionset.id,
                    category_abbreviation=category.abbreviation,
                    subcategory_title=slugify(subcategory.title),
                    credit_identifier=credit.identifier)


class SetOptInCreditsView(View):
    """
        An AJAX view to update the opt-in values on some
        CreditUserSubmissions.
    """

    def post(self, request):
        data_changed = False
        for key, value in request.POST.items():
            cus = CreditUserSubmission.objects.get(pk=int(key))
            if value.lower() == 'true':
                if cus.submission_status == 'na':
                    cus.submission_status = 'ns'
                    cus.save()
                    data_changed = True
            else:
                if cus.submission_status != 'na':
                    cus.submission_status = 'na'
                    cus.save()
                    data_changed = True

        ajax_data = {'data_changed': data_changed}

        return HttpResponse(json.dumps(ajax_data),
                            content_type='application/json')


class CreditSubmissionStatusUpdateView(UpdateView):

    model = CreditUserSubmission
    form_class = CreditSubmissionStatusUpdateForm
    template_name = 'institutions/credit_submission_status_update.html'

    def get_success_url(self, *args, **kwargs):
        return self.request.POST['next']

    def get_context_data(self, **kwargs):
        context = super(CreditSubmissionStatusUpdateView,
                        self).get_context_data(**kwargs)
        context['next'] = self.request.GET['next']
        return context

    def form_valid(self, form):
        """Recalculate scores.
        """
        credit_user_submission = self.get_object()

        submissionset = credit_user_submission.get_submissionset()

        message = "<b>%s</b>: <br>" % credit_user_submission.credit.identifier
        message += "Changed status from %s to %s <br>" % (
            credit_user_submission.submission_status,
            form.cleaned_data["submission_status"]
        )

        original_submission_status = self.request.POST[
            "original_submission_status"]

        credit_user_submission.submission_status = (
            form.cleaned_data["submission_status"])

        credit_original_points = credit_user_submission.assessed_points
        credit_calculated_points = credit_user_submission._calculate_points()

        if ((credit_original_points != credit_calculated_points) or
            credit_user_submission.submission_status == 'c' or
            original_submission_status == 'na' or
                credit_user_submission.submission_status == 'na'):

            credit_user_submission.assessed_points = credit_calculated_points
            credit_user_submission.save(calculate_points=False)

            message += "Score changed from %f to %f <br>" % (
                credit_original_points, credit_calculated_points
            )

            subcategory_submission = (
                credit_user_submission.subcategory_submission)
            subcategory_submission.points = None
            subcategory_submission.points = (
                subcategory_submission.get_claimed_points())
            subcategory_submission.save()

            category_submission = subcategory_submission.category_submission
            category_submission.score = None
            category_submission.score = category_submission.get_STARS_score()
            category_submission.save()

            submissionset_original_score = submissionset.score
            submissionset.score = None
            submissionset.score = submissionset.get_STARS_score()
            submissionset.save()

            message += "Report score changed from %f to %f <br>" % (
                submissionset_original_score, submissionset.score
            )

            new_rating = submissionset.get_STARS_rating(recalculate=True)
            if submissionset.rating != new_rating:
                message += "Rating changed from %s to %s! <br>" % (
                    submissionset.rating, new_rating)
                submissionset.rating = new_rating
                submissionset.save()
            else:
                message += "Rating unchanged.<br>"

        messages.info(self.request, (message))

        credit_user_submission.save()
        submissionset.pdf_report = None
        submissionset.save()

        return super(CreditSubmissionStatusUpdateView, self).form_valid(form)


class CurrentRatingsView(View):

    def get(self, request):

        rating_totals = collections.defaultdict(int)
        for institution in Institution.objects.filter(
                current_rating__isnull=False):
            if institution.rating_expires:
                rating_totals[institution.current_rating.name] += 1

        return HttpResponse(json.dumps(rating_totals),
                            content_type='application/json')
