"""
    STARS Submissions API
"""
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash
from tastypie.http import HttpGone, HttpMultipleChoices, HttpMethodNotAllowed

from stars.apps.credits.models import Category, Credit, Subcategory
from stars.apps.submissions.models import (BooleanSubmission,
                                           CategorySubmission,
                                           ChoiceSubmission,
                                           CreditUserSubmission,
                                           DateSubmission,
                                           LongTextSubmission,
                                           MultiChoiceSubmission,
                                           NumericSubmission,
                                           SubcategorySubmission,
                                           SubmissionSet,
                                           TextSubmission,
                                           URLSubmission,
                                           UploadSubmission)
from stars.apps.submissions import rules as submission_rules
from stars.apps.api.resources import StarsApiResource
from stars.apps.api.paths import (CREDITS_RESOURCE_PATH,
                                  INSTITUTIONS_RESOURCE_PATH,
                                  SUBMISSIONS_RESOURCE_PATH)


class SubmissionSetResource(StarsApiResource):
    """
        Resource for accessing any (published) SubmissionSet.
    """
    creditset = fields.OneToOneField(
        CREDITS_RESOURCE_PATH + 'NestedCreditSetResource', 'creditset',
        full=True)
    category_submissions = fields.ToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NestedCategorySubmissionResource',
        'categorysubmission_set', full=True)
    institution = fields.OneToOneField(
        INSTITUTIONS_RESOURCE_PATH + 'NestedInstitutionResource',
        'institution', full=True)
    rating = fields.CharField(readonly=True)

    class Meta(StarsApiResource.Meta):
        queryset = SubmissionSet.objects.get_rated().filter(is_locked=False)
        resource_name = 'submissions'
        allowed_methods = ['get']
        # exclude submission_boundary becauses it raises
        # "'ascii' codec can't decode byte ... in position ...: ordinal not
        # in range(128)"
        excludes = ['is_locked',
                    'is_visible',
                    'date_reviewed',
                    'date_registered',
                    'status',
                    'reporter_status',
                    'submission_boundary']

    def dehydrate(self, bundle):
        bundle.data['rating'] = str(bundle.obj.rating)

        if bundle.obj.reporter_status:
            bundle.data['score'] = None

        return bundle

    def prepend_urls(self):
        # The detail URL for each resource must be listed before the list URL.
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/category"
                "/(?P<catpk>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_category_detail')),

            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/category%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_category_list')),

            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/subcategory"
                "/(?P<subcatpk>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_subcategory_detail')),

            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/subcategory%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_subcategory_list')),

            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/credit"
                "/(?P<credpk>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_credit_detail')),

            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/credit%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_credit_list')),

            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/field"
                "/(?P<fieldpk>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_field_detail')),
        ]

    def get_category_list(self, request, **kwargs):
        """Get a list of categories for the SubmissionSet with
        id = kwargs['pk']."""
        # Need to check CategorySubmissionResource.Meta.allowed_methods
        # explicitly because the URL fiddling done above
        # bypasses the usual check:
        if (request.method.lower() not in
                CategorySubmissionResource.Meta.allowed_methods):
            return HttpMethodNotAllowed()
        self.is_authenticated(request)
        basic_bundle = self.build_bundle(request=request)
        try:
            obj = self.cached_obj_get(bundle=basic_bundle,
                                      **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(
                "More than one resource is found at this URI.")

        category_submission_resource = CategorySubmissionResource()
        return category_submission_resource.get_list(request,
                                                     submissionset=obj.pk)

    def get_category_detail(self, request, **kwargs):
        """Get the CategorySubmission that matches the Category
        where id = kwargs['catpk']."""
        # Need to check CategorySubmissionResource.Meta.allowed_methods
        # explicitly because the URL fiddling done above
        # bypasses the usual check:
        if (request.method.lower() not in
                CategorySubmissionResource.Meta.allowed_methods):
            return HttpMethodNotAllowed()
        self.is_authenticated(request)
        category_id = kwargs.pop('catpk')
        basic_bundle = self.build_bundle(request=request)
        try:
            obj = self.cached_obj_get(bundle=basic_bundle,
                                      **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(
                "More than one resource is found at this URI.")
        return CategorySubmissionResource().get_detail(request,
                                                       submissionset_id=obj.pk,
                                                       category_id=category_id)

    def get_subcategory_list(self, request, **kwargs):
        """Get the list of SubcategorySubmissions for the SubmissionSet
        where id = kwargs['pk']."""
        # Need to check SubcategorySubmissionResource.Meta.allowed_methods
        # explicitly because the URL fiddling done above
        # bypasses the usual check:
        if (request.method.lower() not in
                SubcategorySubmissionResource.Meta.allowed_methods):
            return HttpMethodNotAllowed()
        self.is_authenticated(request)
        basic_bundle = self.build_bundle(request=request)
        try:
            obj = self.cached_obj_get(bundle=basic_bundle,
                                      **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(
                "More than one resource is found at this URI.")

        return SubcategorySubmissionResource().get_list(
            request, submissionset_id=obj.pk)

    def get_subcategory_detail(self, request, **kwargs):
        """Get the SubcategorySubmission for the Subcategory where
        id = kwargs['subcatpk']."""
        # Need to check SubcategorySubmissionResource.Meta.allowed_methods
        # explicitly because the URL fiddling done above
        # bypasses the usual check:
        if (request.method.lower() not in
                SubcategorySubmissionResource.Meta.allowed_methods):
            return HttpMethodNotAllowed()
        self.is_authenticated(request)
        subcategory_id = kwargs.pop('subcatpk')
        # Make sure the submission set is valid:
        basic_bundle = self.build_bundle(request=request)
        try:
            obj = self.cached_obj_get(bundle=basic_bundle,
                                      **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(
                "More than one resource is found at this URI.")

        kwargs['subcatpk'] = subcategory_id
        kwargs['submissionset'] = obj
        return SubcategorySubmissionResource().get_detail(
            request, **kwargs)

    def get_credit_list(self, request, **kwargs):
        """Get a list of credits for the SubmssionSet where
        id = kwargs['pk'].
        """
        # Need to check CreditSubmissionResource.Meta.allowed_methods
        # explicitly because the URL fiddling done above
        # bypasses the usual check:
        if (request.method.lower() not in
                CreditSubmissionResource.Meta.allowed_methods):
            return HttpMethodNotAllowed()
        self.is_authenticated(request)
        basic_bundle = self.build_bundle(request=request)
        try:
            obj = self.cached_obj_get(bundle=basic_bundle,
                                      **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(
                "More than one resource is found at this URI.")

        return CreditSubmissionResource().get_list(request,
                                                   submissionset_id=obj.pk)

    def get_credit_detail(self, request, **kwargs):
        """Get the CreditSubmissionResource that matches the Credit
        where id = kwargs['credpk'] and the SubmissionSet where
        id = kwargs['pk'].
        """
        # Need to check CreditSubmissionResource.Meta.allowed_methods
        # explicitly because the URL fiddling done above
        # bypasses the usual check:
        if (request.method.lower() not in
                CreditSubmissionResource.Meta.allowed_methods):
            return HttpMethodNotAllowed()
        self.is_authenticated(request)
        credit_id = kwargs.pop('credpk')
        basic_bundle = self.build_bundle(request=request)
        try:
            submissionset = self.cached_obj_get(
                bundle=basic_bundle,
                **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(
                "More than one resource is found at this URI.")

        kwargs.pop('pk')
        kwargs['credpk'] = credit_id
        kwargs['submissionset'] = submissionset
        credit_submission_resource = CreditSubmissionResource()
        detail = credit_submission_resource.get_detail(request, **kwargs)
        return detail

    def get_field_detail(self, request, **kwargs):
        """Given the id's of a SubmissionSet (kwargs['pk']) and
        a DocumentationField (kwargs['fieldpk']), get the
        DocumentationFieldSubmissionResource that matches.
        """
        # Need to check
        # DocumentationFieldSubmissionResource.Meta.allowed_methods
        # explicitly because the URL fiddling done above bypasses the
        # usual check:
        if (request.method.lower() not in
                DocumentationFieldSubmissionResource.Meta.allowed_methods):
            return HttpMethodNotAllowed()
        self.is_authenticated(request)
        for field_resource_type in (NumericSubmissionResource,
                                    TextSubmissionResource,
                                    NumericSubmissionResource,
                                    TextSubmissionResource,
                                    LongTextSubmissionResource,
                                    DateSubmissionResource,
                                    URLSubmissionResource,
                                    UploadSubmissionResource,
                                    BooleanSubmissionResource,
                                    ChoiceSubmissionResource,
                                    MultiChoiceSubmissionResource):
            resources = field_resource_type().obj_get_list(
                request, submissionset_id=kwargs['pk'])
            try:
                resources.get(documentation_field__id=kwargs['fieldpk'])
                break
            except ObjectDoesNotExist:
                pass
        else:
            return HttpGone()

        kwargs['submissionset_id'] = kwargs.pop('pk')
        field_submission_resource = field_resource_type()
        detail = field_submission_resource.get_detail(request, **kwargs)
        return detail


class NestedSubmissionSetResource(SubmissionSetResource):
    """
        Resource for embedding abbreviated SubmissionSet info
        as a nested resource within another resource.
    """

    class Meta(SubmissionSetResource.Meta):
        fields = ['date_submitted',
                  'rating']
        allowed_methods = None

    def dehydrate(self, bundle):
        bundle.data['version'] = str(bundle.obj.creditset.version)
        bundle.data['rating'] = None
        if bundle.obj.rating is not None:
            bundle.data['rating'] = str(bundle.obj.rating.name)

        return bundle


class CategorySubmissionResource(StarsApiResource):
    """
        Resource for accessing any CategorySubmission
    """
    submissionset = fields.ForeignKey(
        SUBMISSIONS_RESOURCE_PATH + 'NestedSubmissionSetResource',
        'submissionset', full=True)
    category = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'NestedCategoryResource', 'category',
        full=True)
    subcategory_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NestedSubcategorySubmissionResource',
        'subcategorysubmission_set', full=True)

    class Meta(StarsApiResource.Meta):
        queryset = CategorySubmission.objects.all()
        resource_name = 'submissions/category'
        allowed_methods = ['get']
        filtering = {'submissionset': 'exact',
                     'category': 'exact',
                     'id': ALL_WITH_RELATIONS}
        excludes = ['id']

    def dehydrate(self, bundle):
        if bundle.obj.submissionset.reporter_status:
            bundle.data['score'] = None
        return bundle

    def get_resource_uri(self, bundle_or_obj=None,
                         url_name='api_dispatch_list'):
        uri = super(CategorySubmissionResource, self).get_resource_uri(
            bundle_or_obj)
        if not bundle_or_obj:
            return uri
        # default uri is
        #    submissions/category/<category-submission-id>,
        # but we want to use
        #    submissions/<submission-set-id>/category/<category-id>
        # instead.
        submissionset_id = bundle_or_obj.obj.submissionset_id
        uri = uri.replace('submissions/',
                          'submissions/{0}/'.format(submissionset_id))
        category_id = str(bundle_or_obj.obj.category_id)
        return '/'.join(uri.split('/')[:-2] + [category_id, ''])

    def obj_get(self, bundle, **kwargs):
        """Given the id's for a SubmissionSet and a Category, get
        the matching CategorySubmission."""
        kwargs['submissionset'] = SubmissionSet.objects.get(
            pk=kwargs.pop('submissionset_id'))
        kwargs['category'] = Category.objects.get(pk=kwargs.pop('category_id'))
        return super(CategorySubmissionResource, self).obj_get(bundle,
                                                               **kwargs)


class NestedCategorySubmissionResource(CategorySubmissionResource):
    """
        Resource for embedding abbreviated CategorySubmission info
        as a nested resource within another resource.
    """
    title = fields.CharField()

    class Meta(CategorySubmissionResource.Meta):
        fields = ['title']
        allowed_methods = None

    def dehydrate_title(self, bundle):
        return bundle.obj.category.title


class SubcategorySubmissionResource(StarsApiResource):
    """
        Resource for accessing any SubcategorySubmission
    """
    subcategory = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'NestedSubcategoryResource', 'subcategory',
        full=True)
    category_submission = fields.ForeignKey(
        SUBMISSIONS_RESOURCE_PATH + 'NestedCategorySubmissionResource',
        'category_submission', full=True)
    credit_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NestedCreditSubmissionResource',
        'creditusersubmission_set', full=True)

    class Meta(StarsApiResource.Meta):
        queryset = SubcategorySubmission.objects.all()
        resource_name = 'submissions/subcategory'
        allowed_methods = ['get']
        filtering = {'category': ALL_WITH_RELATIONS}
        excludes = ['id']

    def dehydrate_points(self, bundle):
        if bundle.obj.category_submission.submissionset.reporter_status:
            return None
        else:
            return bundle.data['points']

    def get_resource_uri(self, bundle_or_obj=None,
                         url_name='api_dispatch_list'):
        uri = super(SubcategorySubmissionResource, self).get_resource_uri(
            bundle_or_obj)
        if not bundle_or_obj:
            return uri
        # default uri is
        #    submissions/subcategory/<subcategory-submission-id>,
        # but we want to use
        #    submissions/<submission-set-id>/subcategory/<subcategory-id>
        # instead.
        submissionset_id = (
            bundle_or_obj.obj.category_submission.submissionset_id)
        uri = uri.replace('submissions/',
                          'submissions/{0}/'.format(submissionset_id))
        subcategory_id = str(bundle_or_obj.obj.subcategory_id)
        return '/'.join(uri.split('/')[:-2] + [subcategory_id, ''])

    def obj_get(self, bundle, **kwargs):
        """Given the id of a Subcategory and a SubmissionSet,
        get the matching SubcategorySubmission.
        """
        submissionset = kwargs.pop('submissionset')

        kwargs['pk'] = kwargs.pop('subcatpk')
        subcategory = Subcategory.objects.get(**kwargs)

        return subcategory.subcategorysubmission_set.get(
            category_submission__submissionset=submissionset)

    def obj_get_list(self, bundle, **kwargs):
        submissionset_id = kwargs.pop('submissionset_id')
        categories_for_submissionset = CategorySubmission.objects.filter(
            submissionset=submissionset_id)
        return SubcategorySubmission.objects.filter(
            category_submission__in=categories_for_submissionset)


class NestedSubcategorySubmissionResource(SubcategorySubmissionResource):
    """
        Resource for embedding abbreviated SubcategorySubmission info
        as a nested resource within another resource.
    """
    title = fields.CharField()

    class Meta(SubcategorySubmissionResource.Meta):
        fields = ['title']
        allowed_methods = None

    def dehydrate_title(self, bundle):
        return bundle.obj.subcategory.title


class CreditSubmissionResource(StarsApiResource):
    """
        Resource for accessing any CreditSubmission
    """
    credit = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'NestedCreditResource', 'credit', full=True)
    subcategory_submission = fields.ForeignKey(
        SUBMISSIONS_RESOURCE_PATH + 'NestedSubcategorySubmissionResource',
        'subcategory_submission', full=True)
    boolean_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NestedBooleanSubmissionResource',
        'booleansubmission_set', full=True)
    choice_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NestedChoiceSubmissionResource',
        'choicesubmission_set', full=True)
    date_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NestedDateSubmissionResource',
        'datesubmission_set', full=True)
    longtext_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NestedLongTextSubmissionResource',
        'longtextsubmission_set', full=True)
    multichoice_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NestedMultiChoiceSubmissionResource',
        'multichoicesubmission_set', full=True)
    numeric_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NestedNumericSubmissionResource',
        'numericsubmission_set', full=True)
    text_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NestedTextSubmissionResource',
        'textsubmission_set', full=True)
    upload_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NestedUploadSubmissionResource',
        'uploadsubmission_set', full=True)
    url_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NestedURLSubmissionResource',
        'urlsubmission_set', full=True)

    class Meta(StarsApiResource.Meta):
        queryset = CreditUserSubmission.objects.all()
        resource_name = 'submissions/credit'
        allowed_methods = ['get']
        # exclude submission_notes  becauses it raises
        # "'ascii' codec can't decode byte ... in position ...: ordinal not
        # in range(128)"
        excludes = ['last_updated',
                    'internal_notes',
                    'responsible_party_confirm',
                    'submission_notes',
                    'id']

    def dehydrate_title(self, bundle):
        return bundle.obj.credit.title

    def dehydrate(self, bundle):
        bundle.data['title'] = self.dehydrate_title(bundle)

        if bundle.obj.subcategory_submission.category_submission.submissionset.reporter_status:
            bundle.data['assessed_points'] = None

        # combine all the fields into one list
        field_list = []
        field_types = ["boolean_submissions",
                       "choice_submissions",
                       "date_submissions",
                       "longtext_submissions",
                       "multichoice_submissions",
                       "numeric_submissions",
                       "text_submissions",
                       "upload_submissions",
                       "url_submissions"]

        for ft in field_types:
            for f in bundle.data[ft]:
                field_list.append(f)
            del bundle.data[ft]

        # only show the fields if they're published with this credit
        if submission_rules.publish_credit_data(bundle.obj):
            bundle.data['documentation_fields'] = field_list

        return bundle

    def get_resource_uri(self, bundle_or_obj=None,
                         url_name='api_dispatch_list'):
        uri = super(CreditSubmissionResource, self).get_resource_uri(
            bundle_or_obj)
        if not bundle_or_obj:
            return uri
        # default uri is
        #    submissions/credit/<credit-submission-id>,
        # but we want to use
        #    submissions/<submission-set-id>/credit/<credit-id>
        # instead.
        credit_user_submission = bundle_or_obj.obj.creditusersubmission
        subcategory_submission = credit_user_submission.subcategory_submission
        category_submission = subcategory_submission.category_submission
        submissionset_id = category_submission.submissionset.id
        uri = uri.replace('submissions/',
                          'submissions/{0}/'.format(submissionset_id))
        credit_id = str(bundle_or_obj.obj.credit_id)
        return '/'.join(uri.split('/')[:-2] + [credit_id, ''])

    def obj_get(self, bundle, **kwargs):
        """Given the id of a Credit and a SubmissionSet, get the matching
        CreditSubmission.
        """
        # TODO: BEN - what about this crazy get()?
        credit = Credit.objects.get(pk=kwargs['credpk'])
        return credit.creditsubmission_set.get(creditusersubmission__subcategory_submission__category_submission__submissionset=kwargs['submissionset']).creditusersubmission

    def obj_get_list(self, bundle, **kwargs):
        submissionset_id = kwargs.pop('submissionset_id')
        categories_for_submissionset = CategorySubmission.objects.filter(
            submissionset=submissionset_id)
        subcategories_for_submissionset = (
            SubcategorySubmission.objects.filter(
                category_submission__in=categories_for_submissionset))
        return CreditUserSubmission.objects.filter(
            subcategory_submission__in=subcategories_for_submissionset)


class NestedCreditSubmissionResource(CreditSubmissionResource):
    """
        Resource for embedding abbreviated CategorySubmission info
        as a nested resource within another resource.
    """
    class Meta(CreditSubmissionResource.Meta):
        fields = ['title']
        allowed_methods = None

    def dehydrate(self, bundle):
        """Need to override CreditSubmissionResource.dehydrate() because it
        assumes this bundle contains keys that this nested version
        doesn't."""
        bundle.data['title'] = super(NestedCreditSubmissionResource,
                                     self).dehydrate_title(bundle)
        return bundle


class DocumentationFieldSubmissionResource(StarsApiResource):

    documentation_field = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'DocumentationFieldResource',
        'documentation_field')
    credit_submission = fields.ForeignKey(
        SUBMISSIONS_RESOURCE_PATH + 'CreditSubmissionResource',
        'credit_submission')

    class Meta(StarsApiResource.Meta):
        resource_name = 'submissions/field'
        allowed_methods = ['get']
        excludes = ['id']

    def credit_user_submissions_for_submissionset(self,
                                                  submissionset_id):
        """Get all the CreditUserSubmissions for a
        SubmissionSet."""
        categories_for_submissionset = CategorySubmission.objects.filter(
            submissionset=submissionset_id)
        subcategories_for_submissionset = (
            SubcategorySubmission.objects.filter(
                category_submission__in=categories_for_submissionset))
        return(CreditUserSubmission.objects.filter(
            subcategory_submission__in=subcategories_for_submissionset))

    def get_resource_uri(self, bundle_or_obj=None,
                         url_name='api_dispatch_list'):
        # default uri is
        #    submissions/field/<field-submission-id>,
        # but we want to use
        #    submissions/<submission-set-id>/field/<field-id>
        # instead.
        # TODO: depending on the path on the incoming request is
        # bad, right?  If it's not, the all the other get_resource_uri
        # methods should do it this way, too:
        field_id = str(bundle_or_obj.obj.documentation_field_id)
        return '/'.join(bundle_or_obj.request.path.split('/')[:5] +
                        ['field', field_id, ''])

    def obj_get(self, bundle, **kwargs):
        """Given the id's of a SubmissionSet (kwargs['submissionset_id']) and
        and a DocumentationField (kwargs['fieldpk']), get the
        matching DocumentationFieldSubmission.
        """
        field_id = kwargs.pop('fieldpk')
        field_list = self.obj_get_list(bundle=bundle, **kwargs)
        field = field_list.get(documentation_field__id=field_id)
        return field

    def obj_get_list(self, bundle, **kwargs):
        """Get the DocumentationFieldSubmissionResource's *of this type*
        for the SubmissionSet where id = kwargs['submissionset_id'].

        This uses the queryset defined in subclass's Meta classes,
        so it's abstract.  So it doesn't get all the
        DocumentationFieldSubmission's for a SubmissionSet, only
        all instances of a particular subtype.
        """
        credit_user_submissions = (
            self.credit_user_submissions_for_submissionset(**kwargs))
        return self._meta.queryset.filter(
            credit_submission__in=credit_user_submissions)


class NestedDocumentationFieldSubmissionResource(
        DocumentationFieldSubmissionResource):
    """
        Resource for embedding abbreviated DocumentationFieldSubmission info
        as a nested resource within another resource.
    """
    title = fields.CharField()

    class Meta(DocumentationFieldSubmissionResource.Meta):
        fields = ['title']
        allowed_methods = None

    def dehydrate_title(self, bundle):
        return bundle.obj.documentation_field.title


class BooleanSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = BooleanSubmission.objects.all()


class NestedBooleanSubmissionResource(
        NestedDocumentationFieldSubmissionResource):

    class Meta(NestedDocumentationFieldSubmissionResource.Meta):
        queryset = BooleanSubmission.objects.all()


class ChoiceSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = ChoiceSubmission.objects.all()


class NestedChoiceSubmissionResource(
        NestedDocumentationFieldSubmissionResource):

    class Meta(NestedDocumentationFieldSubmissionResource.Meta):
        queryset = ChoiceSubmission.objects.all()


class DateSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = DateSubmission.objects.all()


class NestedDateSubmissionResource(
        NestedDocumentationFieldSubmissionResource):

    class Meta(NestedDocumentationFieldSubmissionResource.Meta):
        queryset = DateSubmission.objects.all()


class LongTextSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = LongTextSubmission.objects.all()


class NestedLongTextSubmissionResource(
        NestedDocumentationFieldSubmissionResource):

    class Meta(NestedDocumentationFieldSubmissionResource.Meta):
        queryset = LongTextSubmission.objects.all()


class MultiChoiceSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = MultiChoiceSubmission.objects.all()


class NestedMultiChoiceSubmissionResource(
        NestedDocumentationFieldSubmissionResource):

    class Meta(NestedDocumentationFieldSubmissionResource.Meta):
        queryset = MultiChoiceSubmission.objects.all()


class NumericSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = NumericSubmission.objects.all()


class NestedNumericSubmissionResource(
        NestedDocumentationFieldSubmissionResource):

    class Meta(NestedDocumentationFieldSubmissionResource.Meta):
        queryset = NumericSubmission.objects.all()


class TextSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = TextSubmission.objects.all()


class NestedTextSubmissionResource(
        NestedDocumentationFieldSubmissionResource):

    class Meta(NestedDocumentationFieldSubmissionResource.Meta):
        queryset = TextSubmission.objects.all()


class UploadSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = UploadSubmission.objects.all()


class NestedUploadSubmissionResource(
        NestedDocumentationFieldSubmissionResource):

    class Meta(NestedDocumentationFieldSubmissionResource.Meta):
        queryset = UploadSubmission.objects.all()


class URLSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = URLSubmission.objects.all()


class NestedURLSubmissionResource(NestedDocumentationFieldSubmissionResource):

    class Meta(NestedDocumentationFieldSubmissionResource.Meta):
        queryset = URLSubmission.objects.all()
