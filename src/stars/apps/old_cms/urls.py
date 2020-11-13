from django.conf.urls import url

from views import ArticleDetailView, OldPathRedirectView

app_name = 'old_cms'

urlpatterns = [
    url(r'^[^\/]+/(?P<nid>\d+)/$',
        OldPathRedirectView.as_view(),
        name='cms-old-path-redirect'),

    url(r'^(?P<category_slug>[^\/]+)/(?P<article_slug>[^\/]+).html$',
        ArticleDetailView.as_view(),
        name='cms-article-detail')
]
