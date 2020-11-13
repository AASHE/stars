"""Tests for apps.submissions.models.CategorySubmission.
"""
from django.test import TestCase

import testfixtures

from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import CategorySubmission, SubmissionSet


class CategorySubmissionTest(TestCase):

    def test_get_STARS_score_logging(self):
        """Does get_STARS_score log an error when there's no scoring method?
        """
        creditset = CreditSet()
        creditset.scoring_method = 'bogus_scoring_method'
        submissionset = SubmissionSet()
        submissionset.status = 'x'
        submissionset.creditset = creditset
        categorysubmission = CategorySubmission()
        categorysubmission.submissionset = submissionset
        with testfixtures.LogCapture('stars') as log:
            categorysubmission.get_STARS_score()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith(
            'No method (bogus_scoring_method) defined to score category'))
