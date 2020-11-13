from django.conf.urls import url

from stars.apps.helpers.forms.forms import Confirm
from stars.apps.tool.my_submission.forms import (ContactsForm,
                                                 LetterForm,
                                                 StatusForm)
from stars.apps.tool.my_submission.views import (
    AddResponsiblePartyView,
    ApproveSubmissionView,
    CreditSubmissionDocumentationView,
    CreditSubmissionHistoryView,
    CreditSubmissionNotesView,
    CreditSubmissionReviewView,
    CreditSubmissionReportingFieldsView,
    EditBoundaryView,
    SubmitSuccessView,
    SaveSnapshot,
    SendCreditSubmissionReviewNotationEmailView,
    SubcategorySubmissionDetailView,
    SubmissionReviewSummaryView,
    SubmissionSummaryView,
    SubmitForRatingWizard)


from django.views.decorators.cache import never_cache

from stars.apps.institutions.views import PDFDownloadView, ExcelDownloadView

SUBCAT_PATH = "(?P<category_abbreviation>[\w-]+)/(?P<subcategory_slug>[\w-]+)"
CREDIT_PATH = "%s%s" % (SUBCAT_PATH, "/(?P<credit_identifier>[\w-]+)")

app_name = 'my_submission'

urlpatterns = [
    url(r'^$',
        never_cache(SubmissionSummaryView.as_view()),
        name='submission-summary'),

    # Export retrieval view
    url(r'^pdf/download/(?P<task>[^/]+)/$',
        never_cache(PDFDownloadView.as_view())),

    # Export retrieval view
    url(r'^excel/download/(?P<task>[^/]+)/$',
        never_cache(ExcelDownloadView.as_view())),

    # Exports can also be triggered during submition
    # duplication due to unnamed expressions not yet being supported

    # Export retrieval view
    url(r'^submit/pdf/download/(?P<task>[^/]+)/$',
        never_cache(PDFDownloadView.as_view())),

    # Export retrieval view
    url(r'^submit/excel/download/(?P<task>[^/]+)/$',
        never_cache(ExcelDownloadView.as_view())),

    # Submit a snaphot
    url(r'^snapshot/$', SaveSnapshot.as_view(), name='save-snapshot'),

    # Submit for rating
    url(r'^submit/$',
        SubmitForRatingWizard.as_view([StatusForm,
                                       LetterForm,
                                       ContactsForm,
                                       Confirm],
                                      condition_dict={'1': SubmitForRatingWizard.has_letter_feature}),
        name='submission-submit'),

    url(r'^submit/success/$', SubmitSuccessView.as_view(),
        name='submit-success'),

    url(r'^approve/$', ApproveSubmissionView.as_view(),
        name='approve-submission'),

    url(r'^boundary/$', EditBoundaryView.as_view(),
        name='boundary-edit'),

    url(r'^add-responsible-party/$', AddResponsiblePartyView.as_view(),
        name='add-responsible-party'),

    url(r'^%s/$' % SUBCAT_PATH,
        SubcategorySubmissionDetailView.as_view(),
        name='subcategory-submit'),

    # Caching can cause inaccurate info to be displayed after
    # changing Institution.prefers_metric_system (details below),
    # so we `never_cache` this URL:
    url(r'^%s/$' % CREDIT_PATH,
        never_cache(CreditSubmissionReportingFieldsView.as_view()),
        name='creditsubmission-submit'),

    url(r'^%s/documentation/$' % CREDIT_PATH,
        CreditSubmissionDocumentationView.as_view(),
        name='creditdocs-submit'),

    url(r'^%s/notes/$' % CREDIT_PATH,
        never_cache(CreditSubmissionNotesView.as_view()),
        name='creditnotes-submit'),

    url(r'^%s/history/$' % CREDIT_PATH,
        CreditSubmissionHistoryView.as_view(),
        name='credit-history'),

    url(r'^%s/review/$' % CREDIT_PATH,
        never_cache(CreditSubmissionReviewView.as_view()),
        name='credit-submission-review'),

    url(r'^send-review-notations-email/$',
        never_cache(SendCreditSubmissionReviewNotationEmailView.as_view()),
        name='send-credit-submission-review-notations-email'),

    url(r'^submission-review-summary/$',
        never_cache(SubmissionReviewSummaryView.as_view()),
        name='submission-review-summary')
]

# Here's an illustration of the problem with caching
# CreditSubmissionReportingFieldsView, noted above.
#
#   1. Institution.prefers_metric_system is False, so
#      fields that have a related measurement unit display
#      the US versions, e.g., `acres` and `gallons`, not
#      `hectares` and `cubic metres`.
#   2. User pulls up credit submission page with fields labelled `acres`.
#   3. User goes to Settings and sets Institution.prefers_metric_system
#      to True.
#   4. User goes back to same credit submission page, but rather than
#      `hectares`, the field noted above is still labelled `acres`,
#      *and the quantity has not been converted to metric*.  At this point,
#      if the user simply saves the form, his data is corrupted, since
#      the US quantity is submitted, but the backend thinks it's a metric
#      quantity, since Institution.prefers_metric_system is True.  Since
#      it's a metric quantity, it's converted to its US equivalent and
#      this is stored in the database.
