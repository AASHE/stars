"""
    STARS Credit API.
"""
from tastypie import fields
from tastypie.authentication import Authentication

import stars.apps.credits.models as credits_models
from stars.apps.api.resources import StarsApiResource
from stars.apps.api.paths import CREDITS_RESOURCE_PATH


class CategoryResource(StarsApiResource):
    """
        Resource for accessing any Category.
    """
    creditset = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'NestedCreditSetResource',
        'creditset', full=True)
    subcategories = fields.OneToManyField(
        CREDITS_RESOURCE_PATH + 'NestedSubcategoryResource',
        'subcategory_set', related_name='category', full=True)

    class Meta(StarsApiResource.Meta):
        authentication = Authentication()
        queryset = credits_models.Category.objects.all()
        resource_name = 'credits/category'
        allowed_methods = ['get']
        excludes = [
                        'max_point_value'
                        'include_in_score',
                    ]


class NestedCategoryResource(CategoryResource):
    """
        A resource for nesting Category info in other resources.
        Shows fewer fields, disallows all HTTP methods.
    """
    class Meta(CategoryResource.Meta):
        authentication = Authentication()
        fields = ['title', 'id']
        allowed_methods = None


class CreditResource(StarsApiResource):
    """
        Resource for accessing any Credit
    """
    subcategory = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'NestedSubcategoryResource',
        'subcategory', full=True)
    documentation_fields = fields.ManyToManyField(
        CREDITS_RESOURCE_PATH + 'NestedDocumentationFieldResource',
        'documentationfield_set', related_name='credit', full=True)

    class Meta(StarsApiResource.Meta):
        authentication = Authentication()
        queryset = credits_models.Credit.objects.all()
        resource_name = 'credits/credit'
        allowed_methods = ['get']
        # exclude these fields because they raise
        # "'ascii' codec can't decode byte ... in position ...: ordinal not
        # in range(128)"
        excludes = ['validation_rules',
                    'formula',
                    'staff_notes',
                    'number'
                    ]


class NestedCreditResource(CreditResource):
    """
        An abbreviated CreditResource for embedding within other
        resources.
    """
    class Meta(CreditResource.Meta):
        authentication = Authentication()
        fields = ['title', 'id', 'identifier']
        allowed_methods = None


class CreditSetResource(StarsApiResource):
    """
        Resource for accessing any CreditSet
    """
    categories = fields.ManyToManyField(
        CREDITS_RESOURCE_PATH + 'NestedCategoryResource',
        'category_set', related_name='creditset', full=True)

    class Meta(StarsApiResource.Meta):
        authentication = Authentication()
        queryset = credits_models.CreditSet.objects.filter(version__gte='1.0')
        resource_name = 'credits/creditset'
        fields = ['id', 'release_date', 'version', 'supported_features']
        allowed_methods = ['get']


class NestedCreditSetResource(CreditSetResource):
    """
        An abbreviated CreditSetResource for embedding within other
        resources.
    """
    class Meta(CreditSetResource.Meta):
        authentication = Authentication()
        fields = ['version']
        allowed_methods = None


class DocumentationFieldResource(StarsApiResource):
    """
        Resource for accessing any DocumentationField
    """
    credit = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'NestedCreditResource',
        'credit', full=True)

    class Meta(StarsApiResource.Meta):
        authentication = Authentication()
        queryset = credits_models.DocumentationField.objects.all()
        resource_name = 'credits/field'
        allowed_methods = ['get']
        excludes = ['last_choice_is_other',
                    'is_published',
                    'identifier',
                    ]


class NestedDocumentationFieldResource(DocumentationFieldResource):
    """
        A resource for nesting DocumentationField info in other resources.
        Shows fewer fields, disallows all HTTP methods.
    """
    class Meta(DocumentationFieldResource.Meta):
        authentication = Authentication()
        fields = ['title', 'id']
        allowed_methods = None


class SubcategoryResource(StarsApiResource):
    """
        Resource for accessing any Subcategory
    """
    category = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'NestedCategoryResource',
        'category', full=True)
    credits = fields.OneToManyField(
        CREDITS_RESOURCE_PATH + 'NestedCreditResource', 'credit_set',
        related_name='subcategory', full=True)

    class Meta(StarsApiResource.Meta):
        authentication = Authentication()
        queryset = credits_models.Subcategory.objects.all()
        resource_name = 'credits/subcategory'
        allowed_methods = ['get']
        excludes = ['max_point_value']


class NestedSubcategoryResource(SubcategoryResource):
    """
        A resource for nesting Subcategory info in other resources.
        Shows fewer fields, disallows all HTTP methods.
    """
    class Meta(SubcategoryResource.Meta):
        authentication = Authentication()
        fields = ['title', 'id']
        allowed_methods = None
