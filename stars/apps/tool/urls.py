from django.conf.urls import include, patterns, url

from stars.apps.tool.views import (NoStarsAccountView,
                                   SelectInstitutionView,
                                   SettingsUpdateView,
                                   SubmissionLockedView,
                                   SummaryToolView,
                                   ToolLandingPageView)

urlpatterns = patterns(
    "",

    url('^$', ToolLandingPageView.as_view(), name='tool-landing-page'),

    url('^no-stars-account/', NoStarsAccountView.as_view(),
        name='no-stars-account'),

    url('^select-institution/', SelectInstitutionView.as_view(),
        name='select-institution'),

    url(r'^submission-locked/$', SubmissionLockedView.as_view(),
        name='submission-locked'),

    (r'^credit-editor/', include('stars.apps.tool.credit_editor.urls')),

    (r'^admin/', include('stars.apps.tool.staff_tool.urls')),

    (r'^(?P<institution_slug>[^/]*)/submission/(?P<submissionset>\d+)/',
     include('stars.apps.tool.my_submission.urls')),

    (r'^(?P<institution_slug>[^/]*)/my-resources/',
     include('stars.apps.tool.my_resources.urls')),

    url(r'^(?P<institution_slug>[^/]*)/$', SummaryToolView.as_view(),
        name='tool-summary'),

    url(r'^(?P<institution_slug>[^/]*)/settings/$',
        SettingsUpdateView.as_view(),
        name='settings'),

    (r'^(?P<institution_slug>[^/]*)/manage/',
     include('stars.apps.tool.manage.urls')),
)
