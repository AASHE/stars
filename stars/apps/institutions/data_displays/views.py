import collections
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from logging import getLogger
import re
import hashlib

from excel_response import ExcelResponse

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Avg, StdDev, Min, Max
from django.views.generic import TemplateView
from django.http import Http404

from logical_rules.mixins import RulesMixin
from stars.apps.accounts.mixins import StarsAccountMixin

from stars.apps.credits.models import (CreditSet,
                                       Credit,
                                       Category,
                                       Subcategory,
                                       DocumentationField)
from stars.apps.institutions.data_displays.filters import (
    Filter, FilteringMixin, NarrowFilteringMixin)
from stars.apps.institutions.data_displays.common_filters import (
    BASE_1_0_QS, COMMON_1_0_FILTERS,
    BASE_2_0_QS, COMMON_2_0_FILTERS)

from stars.apps.institutions.data_displays.forms import (
    ScoreColumnForm,
    ReportingFieldSelectForm)
from stars.apps.institutions.models import Institution, Subscription
from stars.apps.submissions.models import (SubmissionSet,
                                           CreditUserSubmission,
                                           DocumentationFieldSubmission,
                                           CategorySubmission,
                                           SubcategorySubmission)

logger = getLogger('stars.request')

USAGE_TEXT = (
    "AASHE believes transparency is a key component in communicating"
    " sustainability claims. STARS data are made publicly available,"
    " and can be used in research and publications, provided that"
    " certain Data Use Guidelines"
    " (http://www.aashe.org/files/documents/STARS/data_use_guidelines.pdf)"
    " are met.")


class Dashboard(TemplateView):
    """
        Display data in a visual form
    """
    template_name = "institutions/data_displays/dashboard.html"

    def get_ratings_context(self):
        """Return a context for the Ratings graph."""
        ratings = collections.defaultdict(int)
        inst = Institution.objects.get_participants_and_reports()
        inst = inst.filter(rated_submission__isnull=False)
        inst = inst.filter(rated_submission__expired=False)
        inst = inst.select_related('rated_submission__rating__name')
        for i in inst:
            ratings[i.rated_submission.rating.name] += 1
        return ratings

    def get_participation_context(self):
        """Return a context for the participation line graph."""
        current_month = date.today()
        current_month = current_month.replace(day=1)
        # create beginning month to replace query on while loop
        # saves 5 seconds of processing
        beginning_date = date(2009, 9, 1)

        def change_month(d, delta):
            if d.month + delta == 13:
                d = d.replace(month=1)
                d = d.replace(year=d.year + 1)
            elif d.month + delta == 0:
                d = d.replace(month=12)
                d = d.replace(year=d.year - 1)
            else:
                d = d.replace(month=d.month+delta)
            return d

        current_month = change_month(current_month, 1)

        slices = []
        context = {}
        context['total_participant_count'] = 0

        # go back through all months until we don't have any subscriptions
        while beginning_date <= current_month:
            # create a "slice" from the current month
            slice = {}

            # create an expiration month
            expiration_month = current_month - relativedelta(years=3)

            # active_participants
            # find all the distinct institutions with active ratings
            # then find the count of all the institutions with subscriptions
            # that are not in that list.
            # add them together and you have active_participants
            active_rating = (SubmissionSet.objects.filter(status='r')
                             .filter(is_visible=True)
                             .filter(date_submitted__lte=current_month)
                             .filter(date_submitted__gt=expiration_month)
                             .values_list('institution', flat=True)
                             .distinct())

            partial_active_participants = (Subscription.objects
                                           .filter(start_date__lte=current_month).values('institution')
                                           .filter(end_date__gt=current_month)
                                           .filter(access_level="Full")
                                           .exclude(institution__in=active_rating).count())

            active_participants = (len(active_rating) +
                                   partial_active_participants)

            slice['active_participants'] = active_participants
            if len(slices) == 0:
                context['current_active_participants'] = active_participants

            subscription_count = Subscription.objects.filter(
                start_date__lte=current_month).values(
                    'institution').count()
            slice['subscription_count'] = subscription_count
            # if len(slices) == 0:
            #     context['total_subscription_count'] = subscription_count

            slice['rating_count'] = len(active_rating)
            if len(slices) == 0:
                context['total_rating_count'] = len(active_rating)

            participant_count = Institution.objects.filter(
                date_created__lt=current_month).count()

            slice['participant_count'] = participant_count
            if len(slices) == 0:
                context['total_participant_count'] = participant_count

            current_month = change_month(current_month, -1)
            slice['date'] = current_month

            slices.insert(0, slice)

        # A good number of Institutions don't have a date_created
        # value, so we need to adjust our counts by that number.
        num_extras = Institution.objects.filter(
            date_created=None).count()
        for slice in slices:
            if slice['participant_count']:
                slice['participant_count'] += num_extras
            else:
                # Don't know how many Institutions we had in this
                # month, but we know we had so many Subscriptions,
                # and each one of those was matched by an
                # Institution, so:
                slice['participant_count'] = slice['subscription_count']

        context['total_participant_count'] += num_extras

        context['ratings_subscriptions_participants'] = slices

        return context

    def get_participants_context(self):
        """Return a context for the Participants map."""
        context = {}
        participants = collections.defaultdict(int)

        for participant in Institution.objects.all():
            if participant.country is not None:
                participants[participant.country] += 1

        # Sort by country.
        ordered_participants = collections.OrderedDict()

        for country, count in sorted(participants.items()):
            ordered_participants[country] = count

        context['participants'] = ordered_participants.items()
        context['half_num_participants'] = len(ordered_participants) / 2

        return context

    def get_context_data(self, **kwargs):

        context = {}
        context['display_version'] = "2.0"  # used in the tabs

        context['ratings'] = self.get_ratings_context()
        context.update(self.get_participation_context())
        context.update(self.get_participants_context())

        context.update(super(Dashboard, self).get_context_data(**kwargs))

        return context


class PieChartView(TemplateView):
    template_name = 'institutions/data_displays/summary_pie_chart.html'

    def get_context_data(self, **kwargs):
        context = super(PieChartView, self).get_context_data(**kwargs)
        context['display_version'] = "2.0"
        return context


class DisplayAccessMixin(StarsAccountMixin, RulesMixin):
    """
        A basic rule mixin for all Data Displays

        @todo: temporary access
    """

    def access_denied_callback(self):
        self.template_name = self.denied_template_name
        return self.render_to_response(
            {'top_help_text': self.get_description_help_context_name(),
             'display_version': '2.0'})


class CommonFilterMixin(object):
    """
        This mixin just sets the available filters for all displays
    """

    def get_available_filters(self):

        cache_key = '-'.join(['institution__institution_type_filter',
                              self.kwargs['cs_version']])

        filters = cache.get(cache_key, None)
        if filters:
            return filters

        qs = Institution.objects.get_rated().values(
            'institution_type').distinct()
        institution_type_list = []
        for it in qs:
            if it['institution_type'] and it['institution_type'] != '':
                institution_type_list.append((it['institution_type'],
                                              it['institution_type']))
        # value means "don't filter base_qs"
        institution_type_list.insert(0, ('All Institutions',
                                         'DO_NOT_FILTER'))

        if self.kwargs["cs_version"] == "2.0":
            common_filters = COMMON_2_0_FILTERS
            base_qs = BASE_2_0_QS
        else:
            common_filters = COMMON_1_0_FILTERS
            base_qs = BASE_1_0_QS

        filters = [
            Filter(
                key='institution__institution_type',
                title='Institution Type',
                item_list=institution_type_list,
                base_qs=base_qs
            )
        ] + common_filters

        # Store in the cache for 6 hours
        cache.set(cache_key, filters, 60 * 60 * 6)
        return filters

    def convertCacheKey(self, key):
        """
            Convert a key to a hash, because memcached
            can't accept certain characters
        """
        return hashlib.sha1("%s-%s" % (self.__class__.__name__,
                                       key)).hexdigest()


class AggregateFilter(DisplayAccessMixin, CommonFilterMixin, FilteringMixin,
                      TemplateView):
    """
        Provides a filtering tool for average category scores

        Members Only
    """
    template_name = "institutions/data_displays/categories.html"
    denied_template_name = "institutions/data_displays/denied_categories.html"

    def update_logical_rules(self):
        super(AggregateFilter, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'user_has_member_displays',
            'param_callbacks': [
                ('user', 'get_request_user'),
            ],
            'response_callback': 'access_denied_callback'
        })

    def get_description_help_context_name(self):
        return "data_display_categories"

    def get_object_list(self, credit_set, category_list):
        """
            basically the tabular output of the category display

            returns a row for each filter with the average scores for each
            category in the creditset

            Ex:
                        ER          PAE         OP
            Canada      12.2        14.7        22.1
            US          13.2        17.4        21.2

            so the return val would be something like:

            [
                {
                    "title": "Canada",
                    "columns": [
                        {"avg": 12.2, "stddev": 2.2, "cat": ER},
                        {"avg": 14.7, "stddev": 2.1, "cat": PAE},
                        {"avg": 21.2, "stddev": 2.1, "cat": OP},
                    ]
                },
                ...
            ]
        """

        object_list = []
        ss_list = None

        for f, v in self.get_selected_filter_objects():

            # get a unique key for each row @TODO - add version
            cache_key = "%s-%s" % (
                self.convertCacheKey(f.get_active_title(v)),
                credit_set.version)
            # see if a cached version is available
            row = cache.get(cache_key)

            # if not, generate that row
            if not row:
                row = {}
                row['title'] = f.get_active_title(v)

                # all the submissionsets from that filter
                ss_list = f.get_results(v).exclude(rating__publish_score=False)
                row['total'] = ss_list.count()

                columns = []

                """
                    for each submission in the ss_list

                    run a query to get the average `score` for each category

                """
                for cat in category_list:
                    obj = {'cat': cat.title}

                    qs = SubcategorySubmission.objects.all()
                    qs = qs.filter(
                        category_submission__submissionset__in=ss_list)
                    qs = qs.filter(subcategory=cat)

                    result = qs.aggregate(
                        Avg('percentage_score'),
                        StdDev('points'),
                        Min('points'),
                        Max('points'))

                    if result['percentage_score__avg']:
                        obj['avg'] = result['percentage_score__avg'] * 100
                    else:
                        obj['avg'] = 0
                    obj['std'] = result['points__stddev'] or 0
                    obj['min'] = result['points__min'] or 0
                    obj['max'] = result['points__max'] or 0

                    columns.append(obj)

                row['columns'] = columns

                cache.set(cache_key, row, 60 * 60 * 6)  # cache for 6 hours

            object_list.insert(0, row)

        return object_list

    def get_context_data(self, **kwargs):

        _context = super(AggregateFilter, self).get_context_data(**kwargs)

        if self.kwargs["cs_version"] == "1.0":
            credit_set = CreditSet.objects.get(version="1.2")
            _context['display_version'] = "1.0"
        elif self.kwargs["cs_version"] == "2.0":
            credit_set = CreditSet.objects.get(version="2.1")
            _context['display_version'] = "2.0"
        else:
            raise Http404
        _context['credit_set'] = credit_set

        _context['url_1_0'] = "#"
        _context['url_2_0'] = "#"
        if self.kwargs["cs_version"] == "2.0":
            _context['url_1_0'] = reverse(
                'institutions:data_displays:categories_data_display', kwargs={"cs_version": "1.0"})
        if self.kwargs["cs_version"] == "1.0":
            _context['url_2_0'] = reverse(
                'institutions:data_displays:categories_data_display', kwargs={"cs_version": "2.0"})

        subcategory_list = Subcategory.objects.filter(
            category__creditset=credit_set,
            category__include_in_report=True,
            category__include_in_score=True)
        _context['category_list'] = subcategory_list
        _context['object_list'] = self.get_object_list(credit_set,
                                                       subcategory_list)
        _context['top_help_text'] = self.get_description_help_context_name()

        return _context


class ScoreFilter(DisplayAccessMixin, CommonFilterMixin,
                  NarrowFilteringMixin, TemplateView):
    """
        Provides a filtering tool for scores by Category, Subcategory, and
        Credit

        Selected Categories/Subcategories/Credits are stored in the GET:

            ?col1=cat_<category_id>&col2=sub_<subcategory_id>&col3=crd_<credit_id>&col4=

        Maximum of 4 columns
        The view has a form that generates the QueryDict
    """

    template_name = "institutions/data_displays/score.html"
    denied_template_name = "institutions/data_displays/denied_score.html"
    _col_keys = ['col1', 'col2', 'col3', 'col4']
    _obj_mappings = [
        ('cat', Category),
        ('sub', Subcategory),
        ('crd', Credit),
        ('cs', CreditSet)]

    def update_logical_rules(self):
        super(DisplayAccessMixin, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'user_has_member_displays',
            'param_callbacks': [
                ('user', 'get_request_user'),
            ],
            'response_callback': 'access_denied_callback'
        })

    def get_description_help_context_name(self):
        return "data_display_scores"

    """
        Methods

            get_selected_columns:
                gets a dict {<col_key>, <selected_value_as_object>,}

            get_object_from_string
                converts a string to an object eg "cat_2" == Category with id=2

            get_select_form
                populates the form from `get_selected_columns`

            get_object_list
                uses the selected_columns and the current filters to
                create an object list

            get_context_data
                adds the form to the context
                adds the object_list to context

        Notes

            Javascript handles the form submission, but taking the
            selected values and appending them to the current querydict

            @todo: add the current list of filters to the context as a
                   querydict (with FilteringMixin)
    """

    def get_selected_columns(self):
        """
            Get the selected columns from the GET querydict

            Example:
                (<col_key>, <selected_value_as_object>,)
        """
        if hasattr(self, '_selected_columns'):  # a little caching
            return self._selected_columns

        get = self.request.GET
        self._selected_columns = []

        for key in self._col_keys:
            if key in get:
                self._selected_columns.append(
                    (key,
                     self.get_object_from_string(get[key])))

        return self._selected_columns

    def get_object_from_string(self, obj_str):
        """
            Takes a string like, 'cat_2' and returns the category with id=2
        """
        for key, klass in self._obj_mappings:
            m_re = "%s_(\d+)" % key
            matches = re.match(m_re, obj_str)
            if matches and matches.groups():
                obj_id = matches.groups()[0]
                try:
                    return klass.objects.get(pk=obj_id)
                except klass.DoesNotExist:
                    logger.error("Mapping failed for: %s." % obj_str,
                                 extra={'request': self.request})
                    break

        return None

    def get_select_form(self, credit_set):
        """
            Initializes the form for the user to select the columns
        """
        return ScoreColumnForm(
            initial=self.get_selected_columns(),
            credit_set=credit_set)

    def get_object_list(self, credit_set):
        """
            Returns the list of objects based on the characteristic filters
            and the selected columns
        """
        selected_columns = self.get_selected_columns()

        if not selected_columns:
            return None
        else:
            # columns = []
            # for k, col in selected_columns.items():,
            #     columns.insert(0, (k, col))

            # Get the queryset from the filters
            queryset = self.get_filtered_queryset()
            object_list = []

            if queryset:
                # get the column values for each submission set in the queryset
                for ss in queryset.order_by('institution__name').exclude(
                        rating__publish_score=False):
                    row = {'ss': ss, 'cols': []}
                    # @todo - make sure the dictionaries align
                    for key, col_obj in selected_columns:
                        if col_obj is not None:
                            claimed_points = "--"
                            available_points = None
                            units = ""

                            if isinstance(col_obj, Category):
                                # Get the related version in this creditset.
                                cat = col_obj.get_for_creditset(ss.creditset)

                                if cat:
                                    obj = CategorySubmission.objects.get(
                                        submissionset=ss, category=cat)
                                    claimed_points = obj.get_STARS_score()
                                    available_points = (
                                        obj.get_adjusted_available_points())
                                    if obj.category.abbreviation != "IN":
                                        units = "%"
                                    url = obj.get_scorecard_url()
                            elif isinstance(col_obj, Subcategory):
                                sub = col_obj.get_for_creditset(ss.creditset)
                                if sub:
                                    obj = SubcategorySubmission.objects.get(
                                        category_submission__submissionset=ss,
                                        subcategory=sub)
                                    claimed_points = obj.get_claimed_points()
                                    available_points = (
                                        obj.get_adjusted_available_points())
                                    url = obj.get_scorecard_url()
                            elif isinstance(col_obj, Credit):
                                credit = col_obj.get_for_creditset(
                                    ss.creditset)
                                if credit:
                                    cred = CreditUserSubmission.objects.get(
                                        subcategory_submission__category_submission__submissionset=ss,
                                        credit=credit)
                                    url = cred.get_scorecard_url()
                                    if ss.rating.publish_score:
                                        if cred.submission_status == "na":
                                            claimed_points = "Not Applicable"
                                        else:
                                            if cred.credit.type == "t1":
                                                claimed_points = (
                                                    cred.assessed_points)
                                                available_points = (
                                                    cred.credit.point_value)
                                            else:
                                                claimed_points = (
                                                    cred.assessed_points)
                                                available_points = (
                                                    ss.creditset.tier_2_points)
                                    else:
                                        claimed_points = "Reporter"
                            elif isinstance(col_obj, CreditSet):
                                claimed_points = ss.get_STARS_score()
                                url = ss.get_scorecard_url()

                            # Sometimes `url` isn't bound here.  Dunno why.
                            # When it isn't, substitute '' for `url`.
                            try:
                                row['cols'].append({
                                    'claimed_points': claimed_points,
                                    'available_points': available_points,
                                    'units': units,
                                    'url': url})
                            except UnboundLocalError:
                                row['cols'].append({
                                    'claimed_points': claimed_points,
                                    'available_points': available_points,
                                    'units': units,
                                    'url': ''})

                    object_list.append(row)

            return object_list

    def get_context_data(self, **kwargs):
        _context = super(ScoreFilter, self).get_context_data(**kwargs)

        if self.kwargs["cs_version"] == "1.0":
            credit_set = CreditSet.objects.get(version="1.2")
            _context['display_version'] = "1.0"
        elif self.kwargs["cs_version"] == "2.0":
            credit_set = CreditSet.objects.get(version="2.1")
            _context['display_version'] = "2.0"
        else:
            raise Http404
        _context['credit_set'] = credit_set

        _context['url_1_0'] = "#"
        _context['url_2_0'] = "#"
        if self.kwargs["cs_version"] == "2.0":
            _context['url_1_0'] = reverse(
                'institutions:data_displays:scores_data_display', kwargs={"cs_version": "1.0"})
        elif self.kwargs["cs_version"] == "1.0":
            _context['url_2_0'] = reverse(
                'institutions:data_displays:scores_data_display', kwargs={"cs_version": "2.0"})
        else:
            raise Http404

        _context['top_help_text'] = self.get_description_help_context_name()
        _context['object_list'] = self.get_object_list(credit_set)

        # Add a title for each selected column:
        _context['column_headings'] = []

        for key, value in self.get_selected_columns():
            if not isinstance(value, CreditSet):
                _context['column_headings'].append((key, str(value)))
            else:
                _context['column_headings'].append((key, "Overall Score"))

        _context['select_form'] = self.get_select_form(credit_set)

        return _context


class ExcelMixin(object):
    """
        Provides a method that will get the current filters as rows
    """

    def get_filters_as_rows(self, context):
        cell = "Selected Filters: "
        for f in context['selected_filters']:
            cell += "%s|%s" % (f['filter_title'], f['selected_item_title'])
        return [(cell,)]


class ScoreExcelFilter(ExcelMixin, ScoreFilter):
    """
        An extension of the score filter for export to Excel
    """

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response with a template rendered with the given context.
        """

        rows = [
            (USAGE_TEXT,),
        ]

        rows += self.get_filters_as_rows(context)

        cols = ["Institution", 'Country', 'Institution Type',
                "STARS Version"]

        selected_columns = self.get_selected_columns()

        for column in selected_columns:
            if not isinstance(column[1], CreditSet):
                column_name = str(column[1])
            else:
                column_name = "Overall Score"
            cols.append(column_name)
            cols.append("")  # blank space
        rows.append(cols)

        subcols = ["", "", "", ""]
        for c in selected_columns:
            subcols.append("Points Earned")
            subcols.append("Available Points")
        rows.append(subcols)

        for o in context['object_list']:
            row = ["%s" % o['ss'].institution,
                   "%s" % o['ss'].institution.country,
                   "%s" % o['ss'].institution.institution_type,
                   "%s" % o['ss'].creditset.version]

            for c in o['cols']:
                if c['claimed_points'] is not None:
                    if isinstance(c['claimed_points'], float):
                        row.append("%.2f" % c['claimed_points'])
                    else:
                        row.append(c['claimed_points'])
                else:
                    row.append('')
                if c['available_points']:
                    row.append("%.2f" % c['available_points'])
                else:
                    row.append('')
            rows.append(row)

        return ExcelResponse(rows)


class ContentFilter(DisplayAccessMixin, CommonFilterMixin,
                    NarrowFilteringMixin, TemplateView):
    """
        Provides a filtering tool that shows all the values for a selected
        Reporting Field for the filtered set of institutions

        The view passes a form to the view that gets initially populated
        with credit sets. Subsequent subcategories down to reporting fields
        are populated using ajax.

        Javascript is used to calculate the new URL based on the selected
        field and the current querydict;
    """
    template_name = "institutions/data_displays/content.html"
    denied_template_name = "institutions/data_displays/denied_content.html"

    """
        Methods

            get_selected_field:
                gets the selected credit from the querydict

            get_form:
                returns the selection form with the inital value from above

            get_object_list:
                returns the results of the query

            get_context_data
                adds the form to the context
                adds the selected field
                adds the object_list to context

        Notes

            Javascript handles the form submission, but taking the selected
            value and appending them to the current querydict
    """

    def update_logical_rules(self):
        super(ContentFilter, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'user_has_member_displays',
            'param_callbacks': [
                ('user', 'get_request_user'),
            ],
            'response_callback': 'access_denied_callback'
        })

    def get_description_help_context_name(self):
        return "data_display_content"

    def get_select_form(self):
        """
            Get the form for selecting a reporting field
        """
        return ReportingFieldSelectForm(initial={'reporting_field':
                                                 self.get_selected_field()})

    def get_selected_field(self):
        """
            Get the selected field from the QueryDict
        """
        if 'reporting_field' in self.request.GET:
            try:
                return DocumentationField.objects.get(
                    pk=self.request.GET['reporting_field'])
            except DocumentationField.DoesNotExist:
                pass
        return None

    def get_object_list(self):
        """
            Get a list of objects based on the filters and the selected field
        """
        cache_key = self.convertCacheKey(self.request.GET.urlencode())
        object_list = cache.get(cache_key)
        if object_list:
            return object_list

        rf = self.get_selected_field()
        object_list = []

        if rf:
            queryset = self.get_filtered_queryset()
            if queryset:
                for ss in queryset.order_by('institution__name'):

                    field_class = DocumentationFieldSubmission.get_field_class(
                        rf)
                    cus_lookup = ("subcategory_submission__"
                                  "category_submission__submissionset")
                    # I have to get creditusersubmissions so i can be sure
                    # these are actual user submissions and not tests.
                    credit = rf.credit.get_for_creditset(ss.creditset)
                    try:
                        cus = CreditUserSubmission.objects.get(
                            **{cus_lookup: ss, 'credit': credit})
                    except CreditUserSubmission.DoesNotExist:
                        pass
                    try:
                        df = field_class.objects.get(
                            credit_submission=cus,
                            documentation_field=rf.get_for_creditset(
                                ss.creditset))
                        cred = CreditUserSubmission.objects.get(
                            pk=df.credit_submission.id)
                        row = {'field': df, 'ss': ss, 'credit': cred}
                        if ss.rating.publish_score:
                            if cred.submission_status == "na":
                                row['assessed_points'] = "Not Applicable"
                                row['point_value'] = ""
                                # Set the field to None because they
                                # aren't reporting.
                                row['field'] = None
                            else:
                                row['assessed_points'] = (
                                    "%.2f" % cred.assessed_points)
                                row['point_value'] = cred.credit.point_value
                                if (cred.submission_status == 'np' or
                                        cred.submission_status == 'ns'):
                                    row['field'] = None
                        else:
                            row['assessed_points'] = "Reporter"
                            row['point_value'] = ""

                    except:
                        row = {'field': None, 'ss': ss, 'credit': None,
                               "assessed_points": None, 'point_value': None}
                    object_list.append(row)

        cache.set(cache_key, object_list, 60 * 120)  # Cache for 2 hours
        return object_list

    def get_context_data(self, **kwargs):

        _context = super(ContentFilter, self).get_context_data(**kwargs)

        if self.kwargs["cs_version"] == "1.0":
            credit_set = CreditSet.objects.get(version="1.2")
            _context['display_version'] = "1.0"
        elif self.kwargs["cs_version"] == "2.0":
            credit_set = CreditSet.objects.get(version="2.1")
            _context['display_version'] = "2.0"
        else:
            raise Http404
        _context['credit_set'] = credit_set

        _context['url_1_0'] = "#"
        _context['url_2_0'] = "#"
        if self.kwargs["cs_version"] == "2.0":
            _context['url_1_0'] = reverse(
                'institutions:data_displays:content_data_display', kwargs={"cs_version": "1.0"})
        if self.kwargs["cs_version"] == "1.0":
            _context['url_2_0'] = reverse(
                'institutions:data_displays:content_data_display', kwargs={"cs_version": "2.0"})

        _context['top_help_text'] = self.get_description_help_context_name()
        _context['reporting_field'] = self.get_selected_field()
        _context['object_list'] = self.get_object_list()
        _context['select_form'] = self.get_select_form()

        return _context


class ContentExcelFilter(ExcelMixin, ContentFilter):
    """
        An extension of the content filter for export to Excel
    """

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response with a template rendered with the given context.
        """
        cols = [
            (USAGE_TEXT,),
        ]
        cols += self.get_filters_as_rows(context)
        cols += [
            ('Institution', 'Country', 'Institution Type',
             'STARS Version', 'Points Earned',
             'Available Points', context['reporting_field'].title,
             'Units'),
        ]

        for o in context['object_list']:

            row = ["%s" % o['ss'].institution,
                   "%s" % o['ss'].institution.country,
                   "%s" % o['ss'].institution.institution_type,
                   "%s" % o['ss'].creditset.version]
            if o['assessed_points']:
                row.append(o['assessed_points'])
            else:
                row.append('')
            if o['point_value']:
                row.append(o['point_value'])
            else:
                row.append('')
            if o['field']:
                if o['field'].documentation_field.type == 'upload':
                    if o['field'].value:
                        if self.request.is_secure():
                            url = 'https://'
                        else:
                            url = 'http://'
                        url += (self.request.get_host() +
                                o['field'].value.url)
                        row.append(url)
                    else:
                        row.append('')
                    row.append('')
                elif o['field'].documentation_field.type == 'choice':
                    row.append(str(o['field'].value))
                else:
                    row.append(o['field'].value)
                    if o['field'].documentation_field.units:
                        row.append(o['field'].documentation_field.units.name)
                    else:
                        row.append('')
            else:
                row.append('')
                row.append('')
            cols.append(row)

        return ExcelResponse(cols)


class CallbackView(TemplateView):
    """
        Child classes must implement self.get_object_list()
    """

    template_name = "institutions/data_displays/option_callback.html"

    def get_context_data(self, **kwargs):

        _context = super(CallbackView, self).get_context_data(**kwargs)
        if 'current' in self.request.GET:
            _context['current'] = int(self.request.GET['current'])

        _context['object_list'] = self.get_object_list(**kwargs)

        return _context


class CategoryInCreditSetCallback(CallbackView):
    """
        A callback method that accepts returns a list of
        categories as <options> for a <select>
    """

    def get_object_list(self, **kwargs):

        cs = CreditSet.objects.get(pk=kwargs['cs_id'])
        return cs.category_set.filter(include_in_report=True)


class SubcategoryInCategoryCallback(CallbackView):
    """
        A callback method that accepts returns a list of
        subcategories as <options> for a <select>
    """

    def get_object_list(self, **kwargs):

        cat = Category.objects.get(pk=kwargs['category_id'])
        return cat.subcategory_set.all()


class CreditInSubcategoryCallback(CallbackView):
    """
        A callback method that accepts returns a list of
        credits as <options> for a <select>
    """

    def get_object_list(self, **kwargs):

        sub = Subcategory.objects.get(pk=kwargs['subcategory_id'])
        return sub.credit_set.all()


class FieldInCreditCallback(CallbackView):
    """
        A callback method that accepts returns a list of
        documentation fields as <options> for a <select>
    """

    def get_object_list(self, **kwargs):

        credit = Credit.objects.get(pk=kwargs['credit_id'])
        return credit.documentationfield_set.exclude(type='tabular')
