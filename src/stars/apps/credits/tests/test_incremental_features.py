"""
    Test for migrating a creditset
"""
import sys

from django.test import TestCase

from stars.apps.credits.models import CreditSet


class TestIncrementalFeatures(TestCase):

    fixtures = ['credits_incremental_feature_test.json']

    def setUp(self):
        pass

    def testGetAttribute(self):
        cs = CreditSet.objects.get(pk=1)
        self.assertFalse(cs.is_locked)

        self.assertTrue(cs.has_feature_one_feature)
        self.assertFalse(cs.has_feature_two_feature)
