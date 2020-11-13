"""Tests for apps.credits.models.Credit.
"""
from django.test import TestCase

import testfixtures

from stars.apps.credits.models import Credit


class CreditTest(TestCase):

    def test_get_identifier_logging(self):
        """Does get_identifier log an error when there's no identifier?
        """
        credit = Credit()
        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace(
                    'stars.apps.credits.models.Credit.subcategory',
                    MockSubcategory(MockCategory(MockCreditset())),
                )
                r.replace('stars.apps.credits.models.Credit.get_1_0_identifier',
                          lambda x: True)
                credit.get_identifier()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue('No identifier' in log.records[0].msg)

    def test_execute_formula_logging(self):
        """Does execute_formula log an exception when one is raised?
        """
        credit = Credit()
        with testfixtures.LogCapture('stars') as log:
            credit.execute_formula(MockSubmission())

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue('Formula Exception' in log.records[0].msg)
        self.assertTrue(log.records[0].exc_info)

    def test_execute_validation_rules_logging(self):
        """Does execute_validation_rules log an exception when one is raised?
        """
        mcredit = MockCredit()
        with testfixtures.LogCapture('stars') as log:
            mcredit.execute_validation_rules(MockSubmission())

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue('Validation Exception' in log.records[0].msg)
        self.assertTrue(log.records[0].exc_info)


class MockSubcategory(object):
    def __init__(self, category):
        self.category = category


class MockCategory(object):
    def __init__(self, creditset):
        self.creditset = creditset


class MockCreditset(object):
    def __init__(self):
        self.credit_identifier = 'b-o-o-o-o-gus credit identifier'


class MockCredit(Credit):
    def __init__(self):
        self.validation_rules = True


class MockSubmission(object):
    def get_submission_field_key(self):
        return None

    def get_available_points(self, *args, **kwargs):
        return 10
