"""
    DataCorrectionTest Unit Tests

    Test Premises:
     - saved corrections will notify users
     - corrections will modify scores
"""
from django.test import TestCase
from stars.apps.submissions.models import *

import sys
from datetime import datetime


class DataCorrectionTest(TestCase):
    fixtures = ['data_correction_test.json',
                'notification_emailtemplate_tests.json']

    def setUp(self):
        pass

    def test_correction(self):
        """

        """
        ss = SubmissionSet.objects.get(pk=1)
        self.assertEqual(ss.score, 100.0)

        platinum = Rating.objects.get(pk=5)
        self.assertEqual(ss.rating, platinum)

        cus = CreditUserSubmission.objects.get(pk=1)
        field = NumericSubmission.objects.get(pk=1)
        user = User.objects.get(pk=1)

        correction = DataCorrectionRequest(
            date=datetime.now(),
            reporting_field=field,
            new_value=4,
            explanation='just cuz',
            user=user,
            approved=False)
        correction.save()

        correction.approved = True
        correction.save()

        ss = SubmissionSet.objects.get(pk=1)
        self.assertEqual(ss.score, 80.0)

        gold = Rating.objects.get(pk=4)
        self.assertEqual(ss.rating, gold)
