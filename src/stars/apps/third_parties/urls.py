from django.conf.urls import url
from stars.apps.third_parties.views import SnapshotList

app_name = 'third_parties'

urlpatterns = [
    url(r'^(?P<slug>[^/]+)/$', SnapshotList.as_view()),
]
