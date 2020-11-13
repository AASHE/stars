"""
    Tests for Data Accuracy Requests

    Premises:
        People can submit accuracy inquiries
        Emails are sent for inquiries
        Emails are redacted for anonymous inquiries
"""
from django.test import TestCase
from django.test.client import Client
from django.core import mail
from django.conf import settings

import os


class AccuracyInquiryTest(TestCase):
    fixtures = ["rated_submission.json",
                "notification_emailtemplate_tests.json"]

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def tearDown(self):
        os.environ['RECAPTCHA_TESTING'] = 'False'

    def test_submit_form(self):
        """
            Test the captcha form
        """
        c = Client()
        url = "/institutions/rated-college-test/report/2011-01-01/inquiry/"

        response = c.get(url)
        self.assertEqual(response.status_code, 200)

        post = {
                    "anonymous": u'on',
                    "additional_comments": u'testing',
                    "creditsubmissioninquiry_set-TOTAL_FORMS": u'1',
                    "creditsubmissioninquiry_set-INITIAL_FORMS": u'0',
                    "creditsubmissioninquiry_set-MAX_NUM_FORMS": u'',
                    "creditsubmissioninquiry_set-0-credit": 1,
                    "creditsubmissioninquiry_set-0-explanation": "Bogus Explanation",
                    "creditsubmissioninquiry_set-0-submission_inquiry": u'',
                    "creditsubmissioninquiry_set-0-id": u'',
                    'recaptcha_response_field': 'PASSED'
                }
        response = c.post(url, post)
        self.assertEqual(len(mail.outbox), 1)
