from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.decorators.cache import never_cache

from stars.apps.institutions.data_displays.views import *

urlpatterns = patterns(
    'django.views.generic.simple',
    # data views
    (r'^$', "direct_to_template",{'template': 'institutions/data_views/index.html'}),
    (r'^dashboard/$', Dashboard.as_view()),
    (r'^categories/$', never_cache(AggregateFilter.as_view())),
    (r'^scores/$', never_cache(ScoreFilter.as_view())),
    (r'^content/$', never_cache(ContentFilter.as_view())),
    (r'^callback/cs/(?P<cs_id>\d+)/$', CategoryInCreditSetCallback.as_view()),
    (r'^callback/cat/(?P<category_id>\d+)/$', SubcategoryInCategoryCallback.as_view()),
    (r'^callback/sub/(?P<subcategory_id>\d+)/$', CreditInSubcategoryCallback.as_view()),
    (r'^callback/credit/(?P<credit_id>\d+)/$', FieldInCreditCallback.as_view()),
)