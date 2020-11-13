from django.conf.urls import url

from views import MyResourcesView

app_name = 'my_resources'

urlpatterns = [
    url(r'^$', MyResourcesView.as_view(), name='my-resources'),
]
