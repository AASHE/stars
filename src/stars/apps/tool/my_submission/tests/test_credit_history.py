"""Tests for apps.tool.my_submission.credit_history_tab."""
import datetime

from django.test import TestCase

from stars.apps.submissions.models import (RATED_SUBMISSION_STATUS,
                                           SubmissionSet)
from stars.test_factories.models import InstitutionFactory, SubmissionSetFactory

from ..credit_history import get_submissionsets_to_include_in_history


class GetSubmissionsetsToIncludeInHistoryTest(TestCase):

    def setUp(self):
        SubmissionSet.objects.all().delete()
        self.institution = InstitutionFactory()

    def test_rated_are_included(self):
        """Are rated SubmissionSets included?"""
        ss = SubmissionSetFactory(
            status=RATED_SUBMISSION_STATUS,
            institution=self.institution,
            date_submitted=datetime.date.today())
        self.assertEqual(
            [historicalsubmissionset.submissionset for
             historicalsubmissionset in
             get_submissionsets_to_include_in_history(self.institution)],
            [ss])

    def test_unrated_and_not_migrated_to_are_excluded(self):
        """Are unrated and not migrated_to SubmissionSets excluded?"""
        _ = SubmissionSetFactory(institution=self.institution)
        self.assertEqual(
            get_submissionsets_to_include_in_history(self.institution),
            [])

    def test_migrated_from_are_included(self):
        """Are migrated_from SubmissionSets included?"""
        ss1 = SubmissionSetFactory(institution=self.institution)
        ss2 = SubmissionSetFactory(institution=self.institution,
                                   migrated_from=ss1,
                                   date_created=datetime.date.today())
        historical_submissionsets = (
            get_submissionsets_to_include_in_history(self.institution))
        self.assertEqual(
            [historical_submissionset.submissionset for
             historical_submissionset in historical_submissionsets],
            [ss1])
