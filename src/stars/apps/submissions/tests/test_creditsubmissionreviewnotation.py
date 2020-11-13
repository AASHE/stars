"""Tests for apps.submissions.models.CreditSubmissionReviewNotation.
"""
from django.test import TestCase

from ..models import (CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS,
                      CreditSubmissionReviewNotation)
from stars.test_factories.models import CreditUserSubmissionFactory


class CreditSubmissionReviewNotationTest(TestCase):

    def setUp(self):
        self.credit_user_submission = CreditUserSubmissionFactory()
        submissionset = self.credit_user_submission.get_submissionset()
        submissionset.is_under_review = True
        submissionset.save()

    def testRevisionRequestUnlocksSubmission(self):
        """Does a Revision Request notation unlock the submission?
        """
        CreditSubmissionReviewNotation.objects.create(
            kind=CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS[
                "REVISION_REQUEST"],
            credit_user_submission=self.credit_user_submission)
        self.assertTrue(self.credit_user_submission.is_unlocked_for_review)

    def testSuggestionForImprovementUnlocksSubmission(self):
        """Does a Suggestion For Improvement notation unlock the submission?
        """
        CreditSubmissionReviewNotation.objects.create(
            kind=CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS[
                "SUGGESTION_FOR_IMPROVEMENT"],
            credit_user_submission=self.credit_user_submission)
        self.assertTrue(self.credit_user_submission.is_unlocked_for_review)

    def testBestPracticeDoesNotUnlockSubmission(self):
        """Does a Best Practice notation unlock the submission? (It shouldn't.)
        """
        CreditSubmissionReviewNotation.objects.create(
            kind=CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS[
                "BEST_PRACTICE"],
            credit_user_submission=self.credit_user_submission)
        self.assertFalse(self.credit_user_submission.is_unlocked_for_review)

    def testDeleteLastRevisionRequestLocksCreditUserSubmission(self):
        """Does deleting the last Revision Request re-lock the submission?
        (Assuming there are no other unlocking kinds of notations on the
        submission.)
        """
        revision_request = CreditSubmissionReviewNotation.objects.create(
            kind=CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS[
                "REVISION_REQUEST"],
            credit_user_submission=self.credit_user_submission)
        suggestion_for_improvement = (
            CreditSubmissionReviewNotation.objects.create(
                kind=CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS[
                    "SUGGESTION_FOR_IMPROVEMENT"],
                credit_user_submission=self.credit_user_submission))
        self.assertTrue(self.credit_user_submission.is_unlocked_for_review)
        suggestion_for_improvement.delete()
        self.assertTrue(self.credit_user_submission.is_unlocked_for_review)
        revision_request.delete()
        self.assertFalse(self.credit_user_submission.is_unlocked_for_review)

    def testDeleteLastSuggestionForImprovementLocksCreditUserSubmission(self):
        """Does deleting the last Sugg. for Imprvmnt. re-lock the submission?
        (Assuming there are no other unlocking kinds of notations on the
        submission.)
        """
        revision_request = CreditSubmissionReviewNotation.objects.create(
            kind=CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS[
                "REVISION_REQUEST"],
            credit_user_submission=self.credit_user_submission)
        suggestion_for_improvement = (
            CreditSubmissionReviewNotation.objects.create(
                kind=CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS[
                    "SUGGESTION_FOR_IMPROVEMENT"],
                credit_user_submission=self.credit_user_submission))
        self.assertTrue(self.credit_user_submission.is_unlocked_for_review)
        revision_request.delete()
        self.assertTrue(self.credit_user_submission.is_unlocked_for_review)
        suggestion_for_improvement.delete()
        self.assertFalse(self.credit_user_submission.is_unlocked_for_review)
