from django.conf.urls import url
from django.views.decorators.cache import never_cache

from views import InstitutionList, institutions_search, select_institution

app_name = 'staff_tool'

urlpatterns = [

    # Institutional Admin
    url(r'^$', InstitutionList.as_view(), name='tool-admin'),
    url(r'^search/$', institutions_search),
    url(r'^list$', InstitutionList.as_view()),
    url(r'^institution/masquerade/(?P<id>\d+)/$', select_institution),

]
