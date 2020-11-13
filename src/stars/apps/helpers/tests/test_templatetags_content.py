"""Tests for stars.apps.helpers.templatetags.content.
"""
from django.test import TestCase
import testfixtures

from stars.apps.helpers.templatetags import content


class ContentTest(TestCase):

    def test_display_block_content_logging(self):
        """Does display_block_content log an warning if there's no BlockConent?
        """
        with testfixtures.LogCapture('stars.user') as log:
            content.display_block_content(key='bo-o-o-o-ogus key')

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'INFO')
        self.assertTrue('BlockContent' in log.records[0].msg)
        self.assertTrue('not found' in log.records[0].msg)

    def test_display_snippet_logging(self):
        """Does display_snippet log a warning if there's no SnippetContent?
        """
        with testfixtures.LogCapture('stars.user') as log:
            content.display_snippet(key='bo-o-o-o-ogus key')

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'WARNING')
        self.assertTrue('SnippetContent' in log.records[0].msg)
        self.assertTrue('not found' in log.records[0].msg)
