"""Tests for apps.submissions.models.MultiChoiceWithOtherSubmission.
"""
from django.test import TestCase

import testfixtures

from stars.apps.credits.models import Choice
from stars.apps.submissions.models import MultiChoiceWithOtherSubmission


class MultiChoiceWithOtherSubmissionTest(TestCase):

    def test_decompress_nonexistant_choice_logging(self):
        """Does decompress log an error when there's no choice?
        """
        mcwos = MultiChoiceWithOtherSubmission()
        with testfixtures.LogCapture('stars') as log:
            mcwos.decompress(value=[-99999])

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith(
            'Attempt to decompress non-existing'))

    def test_decompress_fake_choice_logging(self):
        """Does decompress log an error when the choice is not bonafide?
        """
        mcwos = MultiChoiceWithOtherSubmission()

        choices = [Choice(id=-99998, is_bonafide=False, choice=True),
                   Choice(id=-99999, is_bonafide=False)]
        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace('stars.apps.submissions.models.Choice',
                          MockChoiceModel(choices))
                r.replace(('stars.apps.submissions.models.'
                           'MultiChoiceWithOtherSubmission.get_last_choice'),
                          lambda x: choices[0])
                mcwos.decompress(value=[-99998, -99999])

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue(log.records[0].msg.startswith(
            'Found multiple \'other\' choices'))

    def test_compress_warning_logging(self):
        """Does compress log a warning message if data might be lost?
        """
        mcwos = MultiChoiceWithOtherSubmission()
        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace(
                    'stars.apps.submissions.models.'
                    'MultiChoiceWithOtherSubmission.get_last_choice',
                    lambda x: Choice(id=-88888,
                                     is_bonafide=False, choice='green'))
                mcwos.compress(choices=['yellow'], other_value=True)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'WARNING')
        self.assertTrue('will not be saved because' in log.records[0].msg)


class MockChoiceModel(object):

    def __init__(self, choices):
        self.choices = choices
        self.objects = MockObjectManager(choices)


class MockObjectManager(object):

    def __init__(self, choices):
        self.choices = choices

    def get(self, id):
        for choice in self.choices:
            if choice.id == id:
                return choice
