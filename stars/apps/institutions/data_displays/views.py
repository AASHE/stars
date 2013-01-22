from datetime import date, datetime
from logging import getLogger
import re

from excel_response import ExcelResponse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView

from aashe_rules.mixins import RulesMixin
from stars.apps.accounts.mixins import StarsAccountMixin

from aashe.issdjango.models import TechnicalAdvisor

from stars.apps.credits.models import (CreditSet,
                                       Rating,
                                       Credit,
                                       Category,
                                       Subcategory,
                                       DocumentationField)
from stars.apps.institutions.data_displays.filters import (
    Filter, RangeFilter, FilteringMixin, NarrowFilteringMixin)

from stars.apps.institutions.data_displays.forms import (
    CharacteristicFilterForm, DelCharacteristicFilterForm, ScoreColumnForm,
    ReportingFieldSelectForm)
from stars.apps.institutions.data_displays.models import AuthorizedUser
from stars.apps.institutions.data_displays.utils import (FormListWrapper,
                                                         get_variance)
from stars.apps.institutions.models import Institution, Subscription
from stars.apps.submissions.models import (SubmissionSet, CreditUserSubmission,
                                           DocumentationFieldSubmission,
                                           CategorySubmission,
                                           SubcategorySubmission)

logger = getLogger('stars.request')

class Dashboard(TemplateView):
    """
        Display data in a visual form
    """
    template_name = "institutions/data_displays/dashboard.html"

    def get_context_data(self, **kwargs):

        _context = cache.get('stars_dashboard_context')
        cache_time = cache.get('stars_dashboard_context_cache_time')

        if not _context:
            _context = {}

            # map vars
            i_list = []
            i_qs = Institution.objects.filter(enabled=True).filter(Q(is_participant=True) | Q(current_rating__isnull=False)).order_by('name')
            ratings = {}
            for r in Rating.objects.all():
                if r.name not in ratings.keys():
                    ratings[r.name] = 0

            for i in i_qs:
                d = {
                        'institution': i.profile,
                        'current_rating': i.current_rating,
                        'ss': i.rated_submission,
                        'subscription': i.current_subscription
                    }
                if i.charter_participant:
                    d['image_path'] = "/media/static/images/seals/STARS-Seal-CharterParticipant_70x70.png"
                else:
                    d['image_path'] = "/media/static/images/seals/STARS-Seal-Participant_70x70.png"
                i_list.append(d)

            _context['mapped_institutions'] = i_list


            # bar chart vars
            bar_chart = {}
            """
                '<cat_abbr>': {'title': '<cat_title>', 'ord': #, 'list': [], 'avg': #}
            """

            for i in Institution.objects.filter(current_rating__isnull=False):
                ratings[i.current_rating.name] += 1

                if i.current_rating.publish_score:
                    ss = i.rated_submission
                    for cs in ss.categorysubmission_set.all():
                        if cs.category.include_in_score and cs.category.abbreviation != "IN":
                            if bar_chart.has_key(cs.category.abbreviation):
                                bar_chart[cs.category.abbreviation]['list'].append(cs.get_STARS_score())
                            else:
                                bar_chart[cs.category.abbreviation] = {}
                                bar_chart[cs.category.abbreviation]['title'] = "%s (%s)" % (cs.category.title, cs.category.abbreviation)
                                bar_chart[cs.category.abbreviation]['ord'] = cs.category.ordinal
                                bar_chart[cs.category.abbreviation]['list'] = [cs.get_STARS_score()]

            _context['ratings'] = ratings

            bar_chart_rows = []
            for k,v in bar_chart.items():
                avg, std, min, max = get_variance(v['list'])
                var = "Standard Deviation: %.2f | Min: %.2f | Max %.2f" % (std, min, max)
                bar_chart_rows.append({'short': k, 'avg': avg, 'var': var, 'ord': v['ord'], 'title': v['title']})

            _context['bar_chart'] = bar_chart_rows

            # get participants-to-submission figures

            current_month = date.today()
            current_month = current_month.replace(day=1)

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

            # go back through all months until we don't have any subscriptions
            while Subscription.objects.filter(start_date__lte=current_month).all():
                # create a "slice" from the current month
                slice = {}
                reg_count = Subscription.objects.filter(start_date__lte=current_month).values('institution').distinct().count()
                slice['reg_count'] = reg_count
                if len(slices) == 0:
                    _context['total_reg_count'] = reg_count

                rating_count = SubmissionSet.objects.filter(status='r').filter(date_submitted__lt=current_month).count()
                slice['rating_count'] = rating_count
                if len(slices) == 0:
                    _context['total_rating_count'] = rating_count

                current_month = change_month(current_month, -1)
                slice['date'] = current_month

                slices.insert(0, slice)

            renew_count = 0
            for slice in slices:
                d = slice['date']
                # find all the subscriptions starting that month
                for sub in Subscription.objects.filter(start_date__year=d.year).filter(start_date__month=d.month):
                    # if this institution has previous subscriptions increment the count
                    if sub.institution.subscription_set.filter(start_date__lt=d):
                        renew_count += 1

                slice['renew_count'] = renew_count

            _context['total_renew_count'] = renew_count

            _context['ratings_renewals_registrations'] = slices

            # Horizontal Bar Chart

            uptake_qs = Institution.objects.filter(enabled=True).filter(Q(is_participant=True) | Q(current_rating__isnull=False))


            properties = {
                            'uptake': uptake_qs.count(),
                            'participant': uptake_qs.filter(is_participant=True).count(),
                            'rated': uptake_qs.filter(current_rating__isnull=False).count(),
                            'pcc': uptake_qs.filter(is_pcc_signatory=True).count(),
                            'member': uptake_qs.filter(is_member=True).count(),
                            'us': uptake_qs.filter(country="United States of America").count(),
                            'canada': uptake_qs.filter(country='Canada').count(),
                            'international': uptake_qs.filter(international=True).count(),

                            'charter': Institution.objects.filter(charter_participant=True).count(),
                            'pilot': Institution.objects.filter(is_pilot_participant=True).count(),
                        }

            _context['properties'] = properties

            cache_time = datetime.now()
            cache.set('stars_dashboard_context', _context, 60*120) # cache this for 2 hours
            cache.set('stars_dashboard_context_cache_time', cache_time, 60*120)

        _context['cache_time'] = cache_time
        _context.update(super(Dashboard, self).get_context_data(**kwargs))
        return _context


COMMON_FILTERS = [
                        Filter(
                                key='institution__org_type',
                                title='Organization Type',
                                item_list=[
                                    ('All Institutions', 'DO_NOT_FILTER'), # value means "don't filter base_qs"
                                    ('Two Year Institution', 'Two Year Institution'),
                                    ('Four Year Institution', 'Four Year Institution'),
                                    ('Graduate Institution', 'Graduate Institution'),
                                    ('System Office', 'System Office'),
                                ],
                                base_qs=SubmissionSet.objects.filter(status='r'),
                        ),
                        Filter(
                               key='institution__country',
                               title='Country',
                               item_list=[
                                    ('United States', "United States of America"),
                                    ('Canada', 'Canada')
                               ],
                               base_qs=SubmissionSet.objects.filter(status='r'),
                        ),
                        Filter(
                              key='institution__is_member',
                              title='AASHE Membership',
                              item_list=[
                                   ('AASHE Member', True),
                                   ('Not an AASHE Member', False)
                              ],
                              base_qs=SubmissionSet.objects.filter(status='r'),
                        ),
                        Filter(
                                key='institution__is_pcc_signatory',
                                title='ACUPCC Signatory Status',
                                item_list=[
                                     ('ACUPCC Signatory', True),
                                     ('Not an ACUPCC Signatory', False)
                                ],
                                base_qs=SubmissionSet.objects.filter(status='r'),
                        ),
                        Filter(
                                key='institution__charter_participant',
                                title='STARS Charter Participant',
                                item_list=[
                                     ('Charter Participant', True),
                                     ('Not a Charter Participant', False)
                                ],
                                base_qs=SubmissionSet.objects.filter(status='r'),
                        ),
                        Filter(
                                key='institution__is_pilot_participant',
                                title='STARS Pilot Participant',
                                item_list=[
                                     ('Pilot Participant', True),
                                     ('Not a Pilot Participant', False)
                                ],
                                base_qs=SubmissionSet.objects.filter(status='r'),
                        ),
                        Filter(
                                key='rating__name',
                                title='STARS Rating',
                                item_list=[
                                    ('Bronze', 'Bronze'),
                                    ('Silver', 'Silver'),
                                    ('Gold', 'Gold'),
                                    ('Platinum', 'Platinum'),
                                ],
                                base_qs=SubmissionSet.objects.filter(status='r'),
                        ),
                        RangeFilter(
                                key='institution__fte',
                                title='FTE Enrollment',
                                item_list=[
                                    ('Less than 200', 'u200', None, 200),
                                    ('200 - 499', 'u500', 200, 500),
                                    ('500 - 999', 'u1000', 500, 1000),
                                    ('1,000 - 1,999', 'u2000', 1000, 2000),
                                    ('2,000 - 4,999', 'u5000', 2000, 5000),
                                    ('5,000 - 9,999', 'u10000', 5000, 10000),
                                    ('10,000 - 19,999', 'u20000', 10000, 20000),
                                    ('Over 20,000', 'o20000', 20000, None),
                                ],
                                base_qs=SubmissionSet.objects.filter(status='r'),
                        ),
                      ]


class DisplayAccessMixinOld(object):
    """
        Objects must define two properties:

            denied_template_name = ""
            access_list = ['', ''] valid strings are 'member' and 'participant'

        if either access level is fulfilled then they pass
        if access_list is empty no access levels are required

        users must be authenticated
    """
    def deny_action(self, request):
        """
            @todo - I should turn this into some sort of (class?) decorator
        """

        try:
            au = AuthorizedUser.objects.get(email=request.user.email, start_date__lte=datetime.now(), end_date__gte=datetime.now())
        except AuthorizedUser.DoesNotExist:
            au = None

        ta_access = False
        ta_qs = TechnicalAdvisor.objects.filter(email=request.user.email)
        ta = next(iter(ta_qs), None)
        if ta:
            ta_access= True

        if self.access_list:
            denied = True
            profile = request.user.get_profile()
            if 'member' in self.access_list or ta_access:
                if profile.is_member or profile.is_aashe_staff:
                    denied = False
                elif au and au.member_level: # check the authorized users
                    denied = False

            if 'participant' in self.access_list:
                if profile.is_participant() or profile.is_aashe_staff or ta_access:
                    denied = False
                elif au and au.participant_level: # check the authorized users
                    denied = False
            if denied:
                self.template_name = self.denied_template_name
                return self.render_to_response({'top_help_text': self.get_description_help_context_name(),})
        return None

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):

        deny_action = self.deny_action(request)
        if deny_action:
            return deny_action

        return super(DisplayAccessMixin, self).get(request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):

        deny_action = self.deny_action(request)
        if deny_action:
            return deny_action

        return super(DisplayAccessMixin, self).post(request, *args, **kwargs)

class DisplayAccessMixin(StarsAccountMixin, RulesMixin):
    """
        A basic rule mixin for all Data Displays
        
        @todo: temporary access
    """
    def access_denied_callback(self):
        self.template_name = "institutions/data_displays/denied_categories.html"
        return self.render_to_response({'top_help_text': self.get_description_help_context_name(),})
    

class AggregateFilter(DisplayAccessMixin, FilteringMixin, TemplateView):
    """
        Provides a filtering tool for average category scores

        Participants and Members Only
    """
    template_name = "institutions/data_displays/categories.html"
    
    def update_logical_rules(self):
        super(DisplayAccessMixin, self).update_logical_rules()
        self.add_logical_rule({
                               'name': 'user_is_participant_or_member',
                               'param_callbacks': [
                                                    ('user', 'get_request_user'),
                                                    ],
                               'response_callback': 'access_denied_callback'                 
                               })
    
    def get_available_filters(self):
        return COMMON_FILTERS

    def get_description_help_context_name(self):
        return "data_display_categories"

    def get_object_list(self):
        
        object_list = []
        ss_list = None

        for f, v in self.get_selected_filter_objects():

            d = {}
            d['title'] = f.get_active_title(v)

            ss_list = f.get_results(v).exclude(rating__publish_score=False)

            count = 0
            for ss in ss_list:
                for cat in ss.categorysubmission_set.all():
                    k_list = "%s_list" % cat.category.abbreviation
                    if not d.has_key(k_list):
                        d[k_list] = []
                    d[k_list].append(cat.get_STARS_score())
                count += 1
            d['total'] = count

            for k in d.keys():
                m = re.match("(\w+)_list", k)
                if m:
                    cat_abr = m.groups()[0]
                    if len(d['%s_list'% cat_abr]) != 0:
                        d["%s_avg" % cat_abr], std, min, max = get_variance(d['%s_list'% cat_abr])
                    else:
                        d["%s_avg" % cat_abr] = std, min, max = None
                    d['%s_var' % cat_abr] = "Standard Deviation: %.2f | Min: %.2f | Max %.2f" % (std, min, max)

            object_list.insert(0, d)
            
        return object_list

    def get_context_data(self, **kwargs):

        _context = super(AggregateFilter, self).get_context_data(**kwargs)
        _context['top_help_text'] = self.get_description_help_context_name()
        _context['object_list'] = self.get_object_list()

        return _context

class ScoreFilter(DisplayAccessMixin, NarrowFilteringMixin, TemplateView):
    """
        Provides a filtering tool for scores by Category, Subcategory, and Credit

        Selected Categories/Subcategories/Credits are stored in the GET:
        
            ?col1=cat_<category_id>&col2=sub_<subcategory_id>&col3=crd_<credit_id>&col4=
            
        Maximum of 4 columns
        
        The view has a form that generates the QueryDict
    """
    template_name = "institutions/data_displays/score.html"
    _col_keys = ['col1', 'col2', 'col3', 'col4']
    _obj_mappings = [
                    ('cat', Category),
                    ('sub', Subcategory),
                    ('crd', Credit)]
    
    def update_logical_rules(self):
        super(DisplayAccessMixin, self).update_logical_rules()
        self.add_logical_rule({
                               'name': 'user_is_participant',
                               'param_callbacks': [
                                                    ('user', 'get_request_user'),
                                                    ],
                               'response_callback': 'access_denied_callback'                 
                               })

    def get_description_help_context_name(self):
        return "data_display_scores"
    
    def get_available_filters(self):
        return COMMON_FILTERS
    
    
    """
        Methods
        
            get_selected_columns:
                gets a dict {<col_key>, <selected_value_as_object>,}
                
            get_object_from_string
                converts a string to an object eg "cat_2" == Category with id=2
                
            get_select_form
                populates the form from `get_selected_columns`
                
            get_object_list
                uses the selected_columns and the current filters to create an object list
                
            get_context_data
                adds the form to the context
                adds the object_list to context
                
        Notes
            
            Javascript handles the form submission, but taking the selected values and appending
            them to the current querydict
                
            @todo: add the current list of filters to the context as a querydict (with FilteringMixin)
    """
    
    def get_selected_columns(self):
        """
            Get the selected columns from the GET querydict
            
            Example:
                (<col_key>, <selected_value_as_object>,)
        """
        if hasattr(self, '_selected_columns'): # a little caching
            return self._selected_columns
        
        get = self.request.GET
        self._selected_columns = []
        for key in self._col_keys:
            if get.has_key(key):
                self._selected_columns.append((key, self.get_object_from_string(get[key])))
        
        return self._selected_columns
    
    def get_object_from_string(self, obj_str):
        """
            Takes a string like, 'cat_2' and returns the category with id=2
        """
        for key, klass in self._obj_mappings:
            m_re = "%s_(\d+)" % key
            matches = re.match(m_re, obj_str)
            if matches and matches.groups():
                id = matches.groups()[0]
                try:
                    return klass.objects.get(pk=id)
                except klass.DoesNotExist:
                    logger.error("String-to-object mapping failed for: %s." % obj_str,
                                extra={'request': self.request})
                    break
        
        return None
        

    def get_select_form(self):
        """
            Initializes the form for the user to select the columns
        """
        return ScoreColumnForm(initial=self.get_selected_columns())
    
    def get_object_list(self):
        """
            Returns the list of objects based on the characteristic filters
            and the selected columns
        """
        selected_columns = self.get_selected_columns()

        if not selected_columns:
            return None
        else:
#            columns = []
#            for k, col in selected_columns.items():
#                columns.insert(0, (k, col))

            # Get the queryset from the filters
            queryset = self.get_filtered_queryset()
            object_list = []
            
            if queryset:
                # get the column values for each submission set in the queryset
                for ss in queryset.order_by('institution__name').exclude(rating__publish_score=False):
                    row = {'ss': ss, 'cols': []}
                    count = 0
                    # @todo - make sure the dictionaries align
                    for key, col_obj in selected_columns:
                        if col_obj != None:
                            score = "--"
                            units = ""
                            
                            if isinstance(col_obj, Category):
                                cat = col_obj.get_for_creditset(ss.creditset) # get the related version in this creditset
                                if cat:
                                    obj = CategorySubmission.objects.get(submissionset=ss, category=cat)
                                    score = "%.2f" % obj.get_STARS_score()
                                    if obj.category.abbreviation != "IN":
                                        units = "%"
                                    url = obj.get_scorecard_url()
                            elif isinstance(col_obj, Subcategory):
                                sub = col_obj.get_for_creditset(ss.creditset)
                                if sub:
                                    obj = SubcategorySubmission.objects.get(category_submission__submissionset=ss, subcategory=sub)
                                    score = "%.2f / %.2f" % (obj.get_claimed_points(), obj.get_adjusted_available_points())
                                    url = obj.get_scorecard_url()
                            elif isinstance(col_obj, Credit):
                                credit = col_obj.get_for_creditset(ss.creditset)
                                if credit:
                                    cred = CreditUserSubmission.objects.get(subcategory_submission__category_submission__submissionset=ss, credit=credit)
                                    url = cred.get_scorecard_url()
                                    if ss.rating.publish_score:
                                        if cred.submission_status == "na":
                                            score = "Not Applicable"
                                        else:
                                            if cred.credit.type == "t1":
                                                score = "%.2f / %d" % (cred.assessed_points, cred.credit.point_value)
                                            else:
                                                score = "%.2f / %.2f" % (cred.assessed_points, ss.creditset.tier_2_points)
                                    else:
                                        score = "Reporter"
    
                            row['cols'].append({'score': score, 'units': units, 'url': url})
    
                    object_list.append(row)

            return object_list
        

    def get_context_data(self, **kwargs):

        _context = super(ScoreFilter, self).get_context_data(**kwargs)
        _context['top_help_text'] = self.get_description_help_context_name()
        _context['object_list'] = self.get_object_list()
        _context['selected_columns'] = self.get_selected_columns()
        _context['select_form'] = self.get_select_form()
            
        return _context

class ContentFilter(DisplayAccessMixin, NarrowFilteringMixin, TemplateView):
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
    
    def get_available_filters(self):
        return COMMON_FILTERS
    
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
            
            Javascript handles the form submission, but taking the selected value and appending
            them to the current querydict
    """

    def get_description_help_context_name(self):
        return "data_display_content"

    def get_select_form(self):
        """
            Get the form for selecting a reporting field
        """
        return ReportingFieldSelectForm(initial={'reporting_field': self.get_selected_field()})
    
    def get_selected_field(self):
        """
            Get the selected field from the QueryDict
        """
        if self.request.GET.has_key('reporting_field'):
            try:
                return DocumentationField.objects.get(pk=self.request.GET['reporting_field'])
            except DocumentationField.DoesNotExist:
                pass
        return None
    
    def get_object_list(self):
        """
            Get a list of objects based on the filters and the selected field
        """
        cache_key = self.request.GET.urlencode()
        object_list = cache.get(cache_key)
        if object_list:
            return object_list
        
        rf = self.get_selected_field()
        object_list = []

        if rf:
            queryset = self.get_filtered_queryset()
            if queryset:
                for ss in queryset.order_by('institution__name'):
    
                    field_class = DocumentationFieldSubmission.get_field_class(rf)
                    cus_lookup = "subcategory_submission__category_submission__submissionset"
                    # I have to get creditusersubmissions so i can be sure these are actual user submissions and not tests
                    cus = CreditUserSubmission.objects.get(**{cus_lookup: ss, 'credit': rf.credit.get_for_creditset(ss.creditset)})
                    try:
                        df = field_class.objects.get(credit_submission=cus, documentation_field=rf.get_for_creditset(ss.creditset))
                        cred = CreditUserSubmission.objects.get(pk=df.credit_submission.id)
                        row = {'field': df, 'ss': ss, 'credit': cred}
                        if ss.rating.publish_score:
                            if cred.submission_status == "na":
                                row['assessed_points'] = "Not Applicable"
                                row['point_value'] = ""
                                # set the field to None because they aren't reporting
                                row['field'] = None
                            else:
                                row['assessed_points'] = "%.2f" % cred.assessed_points
                                row['point_value'] = cred.credit.point_value
                                if cred.submission_status == 'np' or cred.submission_status == 'ns':
                                    row['field'] = None
                        else:
                            row['assessed_points'] = "Reporter"
                            row['point_value'] = ""
    
                    except:
                        row = {'field': None, 'ss': ss, 'credit': None, "assessed_points": None, 'point_value': None}
                    object_list.append(row)
                
        cache.set(cache_key, object_list, 60*120) #Cache for 2 hours
        return object_list
        

    def get_context_data(self, **kwargs):

        _context = super(ContentFilter, self).get_context_data(**kwargs)
        _context['top_help_text'] = self.get_description_help_context_name()
        _context['reporting_field'] = self.get_selected_field()
        _context['object_list'] = self.get_object_list()
        _context['select_form'] = self.get_select_form()
        _context['get_params'] = self.request.GET.urlencode()
        
        return _context
    
class ContentExcelFilter(ContentFilter):
    """
        An extension of the content filter for export to Excel
    """
    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response with a template rendered with the given context.
        """
        
        cols = [(
                'Institution', 'Assessed Points', 'Available Points', context['reporting_field'].title
                )]
        
        
        for o in context['object_list']:
            
            row = ["%s" % o['ss']]
            if o['assessed_points']:
                row.append(o['assessed_points'])
            else:
                row.append('')
            if o['point_value']:
                row.append(o['point_value'])
            else:
                row.append('')
            if o['field']:
                row.append(o['field'].get_human_value())
            else:
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
        if self.request.GET.has_key('current'):
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
        return cs.category_set.all()


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
        return credit.documentationfield_set.all()
