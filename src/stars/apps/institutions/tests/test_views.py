"""Tests for apps.institutions.views.
"""
import datetime
import sys
import unittest

from django.test import TestCase
from django.test.client import Client

from iss.models import Organization

from stars.apps.institutions import views
from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import (FINALIZED_SUBMISSION_STATUS,
                                           PENDING_SUBMISSION_STATUS,
                                           PROCESSSING_SUBMISSION_STATUS,
                                           RATED_SUBMISSION_STATUS)
from stars.test_factories.models import InstitutionFactory,\
    SubscriptionFactory, RatingFactory, CreditSetFactory, \
    SubmissionSetFactory


class RatedInstitutionsViewTest(TestCase):
    """
        Test the RatedInstitutionsView

        This should also test SortableTableView and
        SortableTableViewWithInstProps.
    """

    def setUp(self):

        today = datetime.date.today()
        td = datetime.timedelta(days=1)

        # create 3 rated Institutions
        cs = CreditSetFactory()
        count = 0
        for l in ['a', 'b', 'c', 'd']:
            count += 1
            r = RatingFactory(minimal_score=count, name=l, creditset=cs)
            ss = SubmissionSetFactory(creditset=cs, status='r', rating=r)
            i = InstitutionFactory(is_participant=True,
                                   rated_submission=ss,
                                   current_rating=r)
        # create 1 non-rated Institutions
        for _ in range(1):
            i = InstitutionFactory()
            s = SubscriptionFactory(end_date=today - td)
            i.current_subscription = s
            i.save()

    def test_with_client(self):
        """
            This test is enough to cover the code and bring up any
            500 errors. It is not a complete functionality test.
        """

        c = Client()

        # confirm we get a 200 just querying
        url = "/institutions/rated/"
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

        view = views.RatedInstitutions()
        qs = view.get_queryset()
        self.assertEqual(len(qs), 4)

        url = "/institutions/rated/?sort=rating"
        response = c.get(url)
        self.assertEqual(response.status_code, 200)


class ScorecardViewTest(TestCase):
    """
        Test the ScorecardView.
    """
    fixtures = ['rated_submission.json']

    def setUp(self):
        for i in Institution.objects.all():
            Organization.objects.create(account_num=i.aashe_id,
                                        org_name=i.name,
                                        city='city',
                                        state='state',
                                        exclude_from_website=False)
        self.client = Client()

    def test_GET_returns_200(self):
        """Does a GET return a 200 status code?"""
        #
        # Travis cannot fetch the seals for the scorecard, and errors. SKIP the
        # test on Travis
        #
        if '--liveserver=' in sys.argv:
            raise unittest.SkipTest()
        url = "/institutions/rated-college-test/report/2011-01-01/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_submission_date_without_day_returns_404(self):
        """Does a submission date (in the URL) without a day return a 404?"""
        url = "/institutions/rated-college-test/report/2011-01-/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_submission_date_without_month_returns_404(self):
        """Does a submission date (in the URL) without a month return a 404?"""
        url = "/institutions/rated-college-test/report/2011--01/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_submission_date_without_year_returns_404(self):
        """Does a submission date (in the URL) without a year return a 404?"""
        url = "/institutions/rated-college-test/report/-01-01/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_empty_submission_date_returns_404(self):
        """Does an empty submission date (in the URL) return a 404?"""
        url = "/institutions/rated-college-test/report/--/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_submission_date_without_dashes_returns_404(self):
        """Does a submission date (in the URL) without dashes return a 404?"""
        url = "/institutions/rated-college-test/report/20110101/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TopLevelTest(TestCase):

    def setUp(self):
        institution = InstitutionFactory()
        self.pending_submission = SubmissionSetFactory(
            institution=institution,
            status=PENDING_SUBMISSION_STATUS)
        self.processing_submission = SubmissionSetFactory(
            institution=institution,
            status=PROCESSSING_SUBMISSION_STATUS)
        self.finalized_submission = SubmissionSetFactory(
            institution=institution,
            status=FINALIZED_SUBMISSION_STATUS)
        self.rated_submission = SubmissionSetFactory(
            institution=institution,
            status=RATED_SUBMISSION_STATUS)
        self.submissions_for_scorecards = views.get_submissions_for_scorecards(
            institution=institution)

    def test_get_submissions_for_scorecards_includes_pending_subs(self):
        """Does get_submissions_for_scorecards() include pending subs?
        """
        self.assertIn(self.pending_submission,
                      self.submissions_for_scorecards)

    def test_get_submissions_for_scorecards_includes_rated_subs(self):
        """Does get_submissions_for_scorecards() include rated subs?
        """
        self.assertIn(self.rated_submission,
                      self.submissions_for_scorecards)

    def test_get_submissions_for_scorecards_filters_processing_subs(self):
        """Does get_submissions_for_scorecards() filter processing subs?
        """
        self.assertNotIn(self.processing_submission,
                         self.submissions_for_scorecards,)

    def test_get_submissions_for_scorecards_filters_finalized_subs(self):
        """Does get_submissions_for_scorecards() filter finalized subs?
        """
        self.assertNotIn(self.finalized_submission,
                         self.submissions_for_scorecards)
