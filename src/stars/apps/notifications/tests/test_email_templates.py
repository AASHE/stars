"""
    Unittests for the EmailTemplate model

    Test premises:
        - utils.build_message()
        - EmailTemplate.get_message()
        - EmailTemplate.send_email()
"""

from django.test import TestCase
from django.core import mail
from django.conf import settings

from stars.apps.notifications.models import EmailTemplate, CopyEmail
from stars.apps.notifications.utils import build_message

from datetime import date
import sys
import os
import random


class TestNotifications(TestCase):

    def setUp(self):
        """ Create a workable template """
        self.et = EmailTemplate(
            slug='test_slug',
            title='Test Title',
            description='Testing this thing',
            content="This is the <b>value</b> '{{ test_val }}'.",
            example_data={'test_val': 1, },
            )
        self.et.save()

        ce = CopyEmail(template=self.et, address='ben@aashe.org', bcc=False)
        ce.save()

        ce = CopyEmail(template=self.et, address='bens@aashe.org', bcc=True)
        ce.save()

    def test_get_message(self):
        " get_message() "
        self.assertEqual(
            self.et.get_message(), "This is the <b>value</b> '1'.")

    def test_non_ascii_chars(self):
        " get_message() "

        class ObjTest(object):
            def __str__(self):
                return "testin' & stuff"

        test_obj = ObjTest()

        _context = {'test_val': test_obj}
        self.assertEqual(
            self.et.get_message(context=_context),
            "This is the <b>value</b> 'testin' & stuff'.")

        self.et.send_email(['ben.stookey@gmail.com', ], _context)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].body,
            "This is the <b>value</b> 'testin' & stuff'.")

    def test_send_email(self):
        " send_email() "
        context = {'test_val': 2, }

        self.et.send_email(['ben.stookey@gmail.com', ], context)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].body, u"This is the <b>value</b> '2'.")
        self.assertEqual(
            mail.outbox[0].extra_headers, {'Reply-To': 'stars@aashe.org'})
        self.assertEqual(mail.outbox[0].cc, [u'ben@aashe.org'])
        self.assertEqual(mail.outbox[0].bcc, [u'bens@aashe.org'])
