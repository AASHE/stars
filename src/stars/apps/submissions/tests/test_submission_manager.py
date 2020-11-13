"""
    SubmissionManager Unit Tests

    Test Premises:
     - published():
      - correctly applies the date limitation
      - returns all paid institutions
      - displays all unpaid institutions before deadline
      - hides all unpaid institutions later than deadline
      - ignores submissionsets w/out payments
"""
from django.test import TestCase

from stars.apps.submissions.models import (SubmissionSet,
                                           REGISTRATION_PUBLISH_DEADLINE)


class ManagerTest(TestCase):
    fixtures = ['manager_test.json']

    def setUp(self):
        pass

    def testManager(self):
        """
            Ensure that no institutions w/out payments show up after
            REGISTRATION_PUBLISH_DEADLINE
        """
        # Confirm that all those unpaid submissionsets in the
        # published registered before the deadline
        ss_list = SubmissionSet.objects.published()
        for ss in ss_list:
            paid = False
            for p in ss.payment_set.all().order_by('date'):
                if p.type != 'later':
                    paid = True
                    break
            if not paid:
                self.assertTrue(ss.date_registered <
                                REGISTRATION_PUBLISH_DEADLINE)

        # Ensure that only unpaid institutions are excluded from the list
        all_ss_list = SubmissionSet.objects.all()
        for ss in all_ss_list:
            if ss not in ss_list:
                paid = False
                for p in ss.payment_set.all().order_by('date'):
                    if p.type != 'later':
                        paid = True
                        break
                self.assertFalse(paid)
