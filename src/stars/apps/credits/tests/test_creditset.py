"""Tests for apps.credits.models.CreditSet.
"""
from django.test import TestCase

import testfixtures

from stars.apps.credits.models import CreditSet


class CreditSetTest(TestCase):

    def setUp(self):
        self.creditset = CreditSet()

    def test_get_rating_logging(self):
        """Does get_rating log an error when there's no rating?
        """
        with testfixtures.LogCapture('stars') as log:
            self.creditset.get_rating(None)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'WARNING')
        self.assertTrue('No valid rating' in log.records[0].msg)
