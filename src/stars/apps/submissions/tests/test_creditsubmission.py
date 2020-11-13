"""Tests for apps.submissions.models.CreditSubmission.
"""
from django.test import TestCase

import testfixtures

from stars.apps.credits.models import Credit
from stars.apps.submissions.models import CreditSubmission
from stars.test_factories.models import (CreditFactory,
                                         CreditSubmissionFactory,
                                         CreditTestSubmissionFactory,
                                         CreditUserSubmissionFactory)


class CreditSubmissionTest(TestCase):

    def test_round_points_logging(self):
        """Does round_points log an error when there's an exception?
        """
        with testfixtures.LogCapture('stars') as log:
            CreditSubmission.round_points(points='bob', log_error=True)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith(
            'Error converting formula'))

    def test_validate_points_logging(self):
        """Does validate_points log an error when there's an out of range
        error?

        """
        credit_user_submission = CreditUserSubmissionFactory(
            credit=CreditFactory(point_value=10))

        with testfixtures.LogCapture('stars') as log:
            credit_user_submission.validate_points(points=-1.0, log_error=True)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith(
            'Points (-1.0) are out of range'))

    def test_is_test_true_for_test_submission(self):
        """Is is_test True for a CreditTestSubmission?
        """
        test_submission = CreditTestSubmissionFactory()
        self.assertTrue(test_submission.is_test())

    def test_is_test_false_for_user_submission(self):
        """Is is_test True for a CreditUserSubmission?
        """
        user_submission = CreditUserSubmissionFactory()
        self.assertFalse(user_submission.is_test())

    def test_is_test_false_for_sexless_credit_submission(self):
        """Is is_test False for a CreditSubmission that's neither
        a CreditUserSubmission or a CreditTestSubmission?
        """
        credit_submission = CreditSubmissionFactory()
        self.assertFalse(credit_submission.is_test())

    def test_is_test_true_for_testy_credit_submission(self):
        """Is is_test True for a CreditSubmission that's not
        a CreditTestSubmission but looks like one?
        """
        credit_submission = CreditSubmissionFactory()
        credit_submission.credittestsubmission = CreditTestSubmissionFactory()
        self.assertTrue(credit_submission.is_test())

    def test_is_test_true_for_usery_credit_submission(self):
        """Is is_test False for a CreditSubmission that's not
        a CreditUserSubmission but looks like one?
        """
        credit_submission = CreditSubmissionFactory()
        credit_submission.creditusersubmission = CreditUserSubmissionFactory()
        self.assertFalse(credit_submission.is_test())
