from django.conf.urls import url
from django.views.decorators.cache import never_cache

from stars.apps.tool.credit_editor.views import *


# Define some prefixes here to keep the clutter down.
cs_prefix = "(?P<creditset_id>\d+)/"
ct_prefix = cs_prefix + "(?P<category_id>\d+)/"
sb_prefix = ct_prefix + "(?P<subcategory_id>\d+)/"
cr_prefix = sb_prefix + "(?P<credit_id>\d+)/"

app_name = 'credit_editor'

urlpatterns = [
    url(r'^$', home),

    # Creditsets
    url(r'^add-creditset/$', AddCreditset()),
    url(r'^%s$' % cs_prefix, CreditsetDetail()),
    # (r'^%sdelete/$' % cs_prefix, DeleteCreditset()),

    # Categories
    url(r'^%sadd-category/$' % cs_prefix, AddCategory()),
    url(r'^%s$' % ct_prefix, CategoryDetail()),
    # (r'^%sdelete/$' % ct_prefix, DeleteCategory()),

    # Subcategories
    url(r'^%sadd-subcategory/$' % ct_prefix, AddSubcategory()),
    url(r'^%s$' % sb_prefix, SubcategoryDetail()),
    # (r'^%sdelete/$' % sb_prefix, DeleteSubcategory()),

    # Credits
    url(r'^%sadd-credit/$' % sb_prefix, AddT1Credit()),
    url(r'^%sadd-t2-credit/$' % sb_prefix, AddT2Credit()),
    url(r'^%s$' % cr_prefix, CreditDetail()),

    url(r'^%sfields/$' % cr_prefix, never_cache(CreditReportingFields())),
    url(r'^%sadd-field/$' % cr_prefix, AddReportingField()),
    url(r'^%s(?P<field_id>\d+)/$' % cr_prefix, EditReportingField()),

    url(r'^%sapplicability/$' % cr_prefix,
        ApplicabilityReasons(),
        name="applicability-reason-list"),
    url(r'^%sadd-reason/$' % cr_prefix, AddApplicabilityReason()),
    url(r'^%sapplicability/(?P<reason_id>\d+)/$' % cr_prefix,
        EditApplicabilityReason()),
    url(r'^credits/applicabilityreason/(?P<pk>\d+)/delete/$',
        DeleteApplicabilityReason.as_view(),
        name="applicability-reason-delete"),

    url(r'^%sformula/$' % cr_prefix, FormulaAndValidation()),
    url(r'^%sformula/add-test-case/$' % cr_prefix, AddTestCase()),
    url(r'^%sformula/(?P<test_id>\d+)/$' % cr_prefix, EditTestCase()),
    url(r'^%sformula/(?P<pk>\d+)/delete/$' % cr_prefix,
        DeleteTestCase.as_view(),
        name="test-case-delete"),
]
