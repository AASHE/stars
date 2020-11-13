from django.conf.urls import include, url
from tastypie.api import Api

from stars.apps.submissions.api import (CategoryPieChart,
                                        SubategoryPieChart,
                                        SummaryPieChart)
from stars.apps.submissions.views import (
    CurrentRatingsView,
    SetOptInCreditsView)


v1_api = Api(api_name='v1')
v1_api.register(CategoryPieChart())
v1_api.register(SubategoryPieChart())
v1_api.register(SummaryPieChart())

app_name = 'submissions'

urlpatterns = [
    url(r'^api/', include(v1_api.urls)),
    url(r'^set-opt-in-credits/$',
        SetOptInCreditsView.as_view(),
        name='set-opt-in-credits'),
    url(r'^current-ratings/$',
        CurrentRatingsView.as_view(),
        name='current-ratings')
]
