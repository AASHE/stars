from django.conf.urls.defaults import *
from django.views.decorators.cache import never_cache

from stars.apps.institutions.views import *

urlpatterns = patterns(
    'stars.apps.institutions.views',
    
    # Active Institutions
    (r'^$', ActiveInstitutions.as_view()),
    (r'^rated/$', RatedInstitutions.as_view()),
    
    # Submission Inquiry Form
    (r'^inquiry/$', 'inquiry_select_institution'),

    # All scorecards for an Institution
    (r'^(?P<institution_slug>[^/]+)/report/$', InstitutionScorecards.as_view()),

    # Specific scorecard summary for an institution
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/$', ScorecardSummary.as_view()),
    
    # Specific scorecard summary for an institution
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/inquiry/$', SubmissionInquiryView()),
    
    # PDF Export of Submission
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/pdf/$', PDFExportView.as_view()),

    # Credit Scorecard
     (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_abbreviation>[^/]+)/(?P<subcategory_slug>[^/]+)/(?P<credit_identifier>[^/]+)/$', ScorecardCredit.as_view()),
    
    # Data correction request
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_abbreviation>[^/]+)/(?P<subcategory_slug>[^/]+)/(?P<credit_identifier>[^/]+)/(?P<field_id>\d+)/$', DataCorrectionView.as_view()),
    
    # Credit Documentation
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_abbreviation>[^/]+)/(?P<subcategory_slug>[^/]+)/(?P<credit_identifier>[^/]+)/documentation/$', ScorecardCreditDocumentation.as_view()),
     
    # Internal Notes
    (r'^(?P<institution_slug>[^/]+)/report/(?P<submissionset>[^/]+)/(?P<category_abbreviation>[^/]+)/(?P<subcategory_slug>[^/]+)/(?P<credit_identifier>[^/]+)/internal-notes/$', ScorecardInternalNotesView.as_view()),
    
    (r'^data-displays/', include('stars.apps.institutions.data_displays.urls')),
)