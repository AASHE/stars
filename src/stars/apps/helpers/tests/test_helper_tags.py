"""Tests for stars.apps.helpers.templatetags.help.
"""
from django.test import TestCase
import testfixtures

from stars.apps.helpers.templatetags import help


class HelpTagsTest(TestCase):

    TEST_HELP_TEXT = ("This 'help context' is used by 'automated unit tests' "
                      "- do not change this text!")

    def test_show_help_text_as_tooltip(self):
        context = help.show_help_text(self.TEST_HELP_TEXT)
        self.assertTrue(context['tooltip'])
        self.assertEqual(context['help_text'], self.TEST_HELP_TEXT)

    def test_show_help_context_as_inline(self):
        context = help.show_help_text(self.TEST_HELP_TEXT, False)
        self.assertFalse(context['tooltip'])
        self.assertEqual(context['help_text'], self.TEST_HELP_TEXT)

    def test_lookup_help_context_logging(self):
        """Does lookup_help_context log an error if there's no HelpContext?
        """
        with testfixtures.LogCapture('stars') as log:
            help.lookup_help_context(context_name='bo-o-o-o-ogus name')

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'INFO')
        self.assertTrue('HelpContext' in log.records[0].msg)
        self.assertTrue('not found' in log.records[0].msg)
