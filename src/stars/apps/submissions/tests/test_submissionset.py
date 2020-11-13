"""Tests for apps.submissions.models.SubmissionSet.
"""
import testfixtures
from django.test import TestCase

from stars.test_factories.models import (CreditFactory,
                                         CreditSetFactory,
                                         SubmissionSetFactory)


class SubmissionSetTest(TestCase):

    def test_get_STARS_score_logging(self):
        """Does get_STARS_score log an error when there's no scoring method?
        """
        creditset = CreditSetFactory(scoring_method='bogus_scoring_method')
        submissionset = SubmissionSetFactory(creditset=creditset, status='x')

        with testfixtures.LogCapture('stars') as log:
            submissionset.get_STARS_score()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith('No method'))

    def test_init_credit_submission_with_opt_in_credit(self):
        """Does init_credit_submission() handle opt-in Credits correctly?
        """
        credit = CreditFactory(is_opt_in=True)
        submissionset = SubmissionSetFactory(
            creditset=credit.subcategory.category.creditset)
        submissionset.init_credit_submissions()
        creditsubmission = (submissionset.categorysubmission_set.all()[0].
                            subcategorysubmission_set.all()[0].
                            creditusersubmission_set.all()[0])
        self.assertEqual('na', creditsubmission.submission_status)

    def test_init_credit_submission_with_non_opt_in_credit(self):
        """Does init_credit_submission() handle non-opt-in Credits correctly?
        """
        credit = CreditFactory(is_opt_in=False)
        submissionset = SubmissionSetFactory(
            creditset=credit.subcategory.category.creditset)
        submissionset.init_credit_submissions()
        creditsubmission = (submissionset.categorysubmission_set.all()[0].
                            subcategorysubmission_set.all()[0].
                            creditusersubmission_set.all()[0])
        self.assertNotEqual('na', creditsubmission.submission_status)
