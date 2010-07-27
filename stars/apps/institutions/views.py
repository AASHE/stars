from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import PermissionDenied

import sys
from datetime import date

from stars.apps.auth.utils import respond
from stars.apps.auth.mixins import InstitutionAccessMixin
# from stars.apps.auth.decorators import user_is_staff, user_can_view
from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import *
from stars.apps.institutions.models import Institution, InstitutionState, StarsAccount
from stars.apps.helpers.forms.views import TemplateView

class SortableTableView(TemplateView):
    """
        A class-based view for displaying a sortable list of objects
        The extending class should set two property variables: `columns` and `default_key`
        And override the `get_queryset` method
    """
    
    columns = None # This is coupled to the template :(
    default_key = None # The default column to sort on
    
    def __init__(self, *args, **kwargs):
        
        # make sure that the extending class has defined the requred properties.
        assert (self.columns and self.default_key), "Must `colums` and `default_key` when extending this class"
        return super(SortableTableView, self).__init__(*args, **kwargs)
    
    def get_context(self, request, *args, **kwargs):
        """ Add/update any context variables """
        context = {'sort_columns': self.columns, 'default_key': self.default_key}
        
        (context['sort_key'], context['rev'], context['object_list']) = self.get_object_list(request)
        
        return context
        
    def get_queryset(self):
        """ Gets the base queryset for the object_list """
        raise NotImplementedError, "Please override this method"
        
    def get_object_list(self, request):
        """
            Returns a queryset based on the GET Parameters
            Also returns the selected `sort_key`
            and `rev`, a "-" or empty string indicating the reverse sort order
        """
        
        sort_key = None
        asc = ""
        rev = ""
        queryset = self.get_queryset()
        
        if request.GET.has_key('sort'):
            if request.GET['sort'][0] == '-':
                asc = '-'
                rev = ''
                sort_key = request.GET['sort'][1:]
            else:
                asc = ''
                rev = '-'
                sort_key = request.GET['sort']
        else:
            sort_key = self.default_key
            rev = self.default_rev
            if rev == '':
                asc = '-'
            
        for col in self.columns:
            if col['key'] == sort_key:
                queryset = queryset.order_by("%s%s" % (asc, col['sort_field']), self.secondary_order_field)
        
        return (sort_key, rev, queryset)

class ActiveInstitutions(SortableTableView):
    """
        Extending SortableTableView to show a sortable list of all active submissionsets
    """

    default_key = 'status'
    default_rev = ''
    secondary_order_field = 'institution__name'
    columns = [
                    {
                        'key': 'name',
                        'sort_field': 'institution__name',
                        'title': 'Institution',
                    },
                    {
                        'key': 'status',
                        'sort_field': 'status',
                        'title': 'Status',
                    },
                    {
                        'key': 'rating',
                        'sort_field': 'rating',
                        'title': 'Rating',
                    },
                    {
                        'key': 'date_registered',
                        'sort_field': 'date_registered',
                        'title': 'Date Registered',
                    },
                    {
                        'key':'deadline',
                        'sort_field':'submission_deadline',
                        'title':'Submission Deadline',
                    },
              ]
              
    def get_queryset(self):
        return SubmissionSet.objects.published()

"""
    INSTITUTIONAL REPORTS
"""

class InstitutionScorecards(TemplateView):
    """
        Provides a list of available reports for an institution
        
        Unrated SubmissionSets will be displayed to particpating users only.
    """
    def get_context(self, request, *args, **kwargs):
        
        institution = get_object_or_404(Institution, id=kwargs['institution_id'])
        
        submission_sets = []
        for ss in institution.submissionset_set.all():
            if ss.status == 'r':
                submission_sets.append(ss)
            elif request.user.has_perm('admin'):
                submission_sets.append(ss)
            else:
                try:
                    account = StarsAccount.objects.get(institution=institution, user=request.user)
                    if account.has_access_level('observer'):
                        submission_sets.append(ss)
                except:
                    pass
                    
        if len(submission_sets) < 1:
            raise Http404
                
        return {'submission_sets': submission_sets, 'institution': institution}

class CreditBrowsingView(TemplateView):
    """
        Class-based view that can

            - extract the Category, Subcategory, and Credit
              from the variables passed to __call__()

            - provide the outline for the left nav menu for the CreditSet

        Thoughts:

            - use a `get_context_from_request` method so that it can be used with mixins
    """
        
    def get_creditset_selection(self, request, **kwargs):
        """
            Gets the Category/Subcategory/Credit from the kwargs
            returns a tuple: (category, subcategory, credit)
            assumes the naming scheme: category_id/subcategory_id/credit_id
        """
        
        category = None
        subcategory = None
        credit = None
        
        # Get the CategorySubmission
        if kwargs.has_key('category_id'):
            category = get_object_or_404(Category, id=kwargs['category_id'])
            
            # Get the SubcategorySubmission
            if kwargs.has_key('subcategory_id'):
                subcategory = get_object_or_404(Subcategory, id=kwargs['subcategory_id'])
                
                # Get the Credit
                if kwargs.has_key('credit_id'):
                    credit = get_object_or_404(Credit, id=kwargs['credit_id'])
                    
        return (category, subcategory, credit)
        
    def get_creditset_navigation(self, creditset, url_prefix, current=None):
        """
            Provides a list of categories for a given `creditset`,
            each with a subcategory dict containing a list of subcategories,
            each with credits and tier2 credits dicts containing lists of credits
            
            Category:
                {'title': title, 'url': url, 'subcategories': subcategory_list}
            Subcategory:
                {'title': title, 'url': url, 'credits': credit_list, 'tier2': credit_list}
            Credit:
                {'title': title, 'url': url}
        """
        outline = []
        # Top Level: Categories
        for cat in creditset.category_set.all():
            subcategories = []
            
            # Second Level: Subcategories
            for sub in cat.subcategory_set.all():
                credits = []
                tier2 = []
                
                # Third Level: Credits
                for credit in sub.credit_set.all():
                    c = {
                            'title': credit.__unicode__(),
                            'url': self.get_credit_url(credit, url_prefix),
                            'id': credit.id,
                            'selected': False,
                        }
                    if current == credit:
                        c['selected'] = True
                    if credit.type == 't1':
                        credits.append(c)
                    elif credit.type == 't2':
                        tier2.append(c)
                
                temp_sc =   {
                            'title': sub.title,
                            'url': self.get_subcategory_url(sub, url_prefix),
                            'credits': credits,
                            'tier2': tier2,
                            'id': sub.id,
                            'selected': False,
                        }
                if current == sub:
                    temp_sc['selected'] = True
                subcategories.append(temp_sc)
                             
            temp_c =    {
                            'title': cat.title,
                            'url': self.get_category_url(cat, url_prefix),
                            'subcategories': subcategories,
                            'id': cat.id,
                            'selected': False,
                        }
            if current == cat:
                temp_c = True
            outline.append(temp_c)
        
        return outline
        
    def get_category_url(self, category, url_prefix):
        """
            The default link for a category. Used by Reporting Tool and Reports.
            Reporting tool should override.
        """
        return "%s%s" % (url_prefix, category.get_browse_url())
        
    def get_subcategory_url(self, subcategory, url_prefix):
        """
            The default link for a category. Used by Reporting Tool and Reports.
            Reporting tool should override.
        """
        return "%s%s" % (url_prefix, subcategory.get_browse_url())
        
    def get_credit_url(self, credit, url_prefix):
        """ The default credit link """
        return "%s%s" % (url_prefix, credit.get_browse_url())
        
class ScorecardView(CreditBrowsingView):
    """
        Browse credits according to submission in the credit browsing view
    """
    
    def get_context(self, request, *args, **kwargs):
        """ Expects arguments for category_id/subcategory_id/credit_id """
        
        context = self.get_submissionset_context(request, **kwargs)
        
        url_prefix = context['submissionset'].get_scorecard_url()
            
        context['outline'] = self.get_creditset_navigation(context['submissionset'].creditset, url_prefix, context['current'])
        
        context['score'] = context['submissionset'].get_STARS_score()
        context['rating'] = context['submissionset'].get_STARS_rating()
        
        return context
        
    def get_submissionset_context(self, request, **kwargs):
        """
            Gets all the available contexts associated with a submission from the kwargs
            
            Available keywords:
                - institution_id
                - submissionset_id
                - category_id
                - subcategory_id
                - credit_id
        """
        context = {}
        # Get the Institution
        if kwargs.has_key('institution_id'):
            institution = get_object_or_404(Institution, id=kwargs['institution_id'])
            context['institution'] = institution
            
            # Check that the user has a StarsAccount for this institution, or is an admin
            if request.user.is_authenticated():
                try:
                    account = StarsAccount.objects.get(institution=institution, user=request.user)
                except StarsAccount.DoesNotExist:
                    account = None
                    
                if account or request.user.has_perm('admin'):
                    context['user_tied_to_institution'] = True
                
            
            # Get the SubmissionSet
            if kwargs.has_key('submissionset_id'):
                submissionset = get_object_or_404(SubmissionSet, id=kwargs['submissionset_id'], institution=institution)
                # if the submissionset isn't rated raise a 404 exception unless the user has preview access
                if submissionset.status != 'r':
                    if context.has_key('user_tied_to_institution'):
                        context['preview'] = True
                    else:
                        raise Http404
                    
                context['submissionset'] = submissionset
                
        category, subcategory, credit = self.get_creditset_selection(request, **kwargs)
        
        # Get the submission objects for each element...
        context['current'] = None
        if category:
            category_submission = get_object_or_404(CategorySubmission, category=category, submissionset=submissionset)
            context['category_submission'] = category_submission
            context['current'] = category
        if subcategory:
            subcategory_submission = get_object_or_404(SubcategorySubmission, category_submission=category_submission, subcategory=subcategory)
            context['subcategory_submission'] = subcategory_submission
            context['current'] = subcategory
        if credit:
            credit_submission = get_object_or_404(CreditUserSubmission, subcategory_submission=subcategory_submission, credit=credit)
            context['credit_submission'] = credit_submission
            context['current'] = credit

        return context

class ScorecardInternalNotesView(InstitutionAccessMixin, ScorecardView):
    """
        An extension of the scorecard view that requires permission on the selected institution.
    """
    
    # Mixin required properties
    access_level = 'observer'
    def raise_redirect(self):
        raise Http404
    fail_response = raise_redirect
    