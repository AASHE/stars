from django.conf.urls import url
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from stars.apps.institutions.data_displays.views import *

app_name = 'data_displays'

urlpatterns = [
    # data views
    url(r'^$',
        TemplateView.as_view(
            template_name='institutions/data_views/index.html'),
        name="data_view_index"
        ),
    url(r'^pie-chart-visualization/$',
        PieChartView.as_view(),
        name="piechart"),
    url(r'^dashboard/$',
        never_cache(Dashboard.as_view()),
        name="dashboard"),
    url(r'^(?P<cs_version>[^\/]+)/categories/$',
        never_cache(AggregateFilter.as_view()),
        name="categories_data_display"),
    url(r'^(?P<cs_version>[^\/]+)/scores/$',
        never_cache(ScoreFilter.as_view()),
        name="scores_data_display"),
    url(r'^(?P<cs_version>[^\/]+)/content/$',
        never_cache(ContentFilter.as_view()),
        name="content_data_display"),

    url(r'^(?P<cs_version>[^\/]+)/scores/excel/$',
        never_cache(ScoreExcelFilter.as_view())),
    url(r'^(?P<cs_version>[^\/]+)/content/excel/$',
        never_cache(ContentExcelFilter.as_view())),
    url(r'^callback/cs/(?P<cs_id>\d+)/$',
        CategoryInCreditSetCallback.as_view()),
    url(r'^callback/cat/(?P<category_id>\d+)/$',
        SubcategoryInCategoryCallback.as_view()),
    url(r'^callback/sub/(?P<subcategory_id>\d+)/$',
        CreditInSubcategoryCallback.as_view()),
    url(r'^callback/credit/(?P<credit_id>\d+)/$',
        FieldInCreditCallback.as_view()),
]
