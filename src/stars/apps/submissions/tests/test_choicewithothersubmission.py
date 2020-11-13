"""Tests for apps.submissions.models.ChoiceWithOtherSubmission.
"""
from django.test import TestCase

import testfixtures

from stars.apps.credits.models import Choice
from stars.apps.submissions.models import ChoiceWithOtherSubmission


class ChoiceWithOtherSubmissionTest(TestCase):

    def test_decompress_logging(self):
        """Does decompress log an error when there's an exception?
        """
        cwos = ChoiceWithOtherSubmission()
        with testfixtures.LogCapture('stars') as log:
            cwos.decompress(value=-99999)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith(
            'Attempt to decompress non-existing'))

    def test_compress_warning_logging(self):
        """Does compress log a warning message if data might be lost?
        """
        cwos = ChoiceWithOtherSubmission()
        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace(
                    'stars.apps.submissions.models.ChoiceWithOtherSubmission.'
                    'get_last_choice',
                    lambda x: MockChoice())
                cwos.compress(choice='yellow', other_value=True)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'WARNING')
        self.assertTrue('will not be saved because' in log.records[0].msg)


class MockChoice(object):

    def __init__(self):
        self.choice = 'blue'
