"""
    Tests for apps.submissions.models.ResponsibleParty.
"""
from django.test import TestCase

from stars.apps.submissions.models import (CreditUserSubmission,
                                           ResponsibleParty)
from stars.test_factories.models import (CreditUserSubmissionFactory,
                                         ResponsiblePartyFactory)


def _hide_creditusersubmission(creditusersubmission):
    """
        'Hides' a CreditUserSubmission by making the related
        SubmissionSet invisible.
    """
    subcategory_submission = creditusersubmission.subcategory_submission
    category_submission = subcategory_submission.category_submission
    submissionset = category_submission.submissionset
    submissionset.is_visible = False
    submissionset.save()


class ResponsiblePartyTest(TestCase):

    def setUp(self):
        self.responsible_party = ResponsiblePartyFactory()
        self.credit_user_submissions = list()
        for _ in xrange(4):
            self.credit_user_submissions.append(CreditUserSubmissionFactory(
                responsible_party=self.responsible_party))

    def test_get_creditusersubmissions_correct_count(self):
        """Does get_creditusersubmissions return the correct number of items?
        """
        self.assertEqual(
            self.responsible_party.get_creditusersubmissions().count(),
            len(self.credit_user_submissions))

    def test_get_creditusersubmissions_invisible_credits_excluded(self):
        """Does get_creditusersubmissions return only visible items?"""
        _hide_creditusersubmission(self.credit_user_submissions[1])
        _hide_creditusersubmission(self.credit_user_submissions[2])
        self.assertEqual(
            self.responsible_party.get_creditusersubmissions().count(),
            len(self.credit_user_submissions) - 2)

    def test_deleting_responsible_party_doesnt_delete_submission(self):
        """Does deleting a RP delete the related CreditUserSubmissions?
        (It shouldn't.)
        """
        num_cus_before = CreditUserSubmission.objects.count()
        num_rp_before = ResponsibleParty.objects.count()
        self.responsible_party.delete()
        self.assertEqual(num_rp_before - 1, ResponsibleParty.objects.count())
        self.assertEqual(num_cus_before, CreditUserSubmission.objects.count())
