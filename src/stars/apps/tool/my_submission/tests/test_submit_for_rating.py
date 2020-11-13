"""
    Tests for the submit for rating tool that will process an institutions
    submission and notify the liason and STARS Staff

    Test premises:
        - the forms are processed correctly
            - Confirmation form
            - Letter Submission
            - Finalize
        - email notifications are sent
"""
import tempfile

from django.test import TestCase
from django.core import mail
from django.test.client import Client
from django.conf import settings

from stars.apps.submissions.models import SubmissionSet
from stars.apps.institutions.models import Institution


class RatingTest(TestCase):

    fixtures = ['submit_for_rating_tests.json',
                'notification_emailtemplate_tests.json']

    def setUp(self):

        settings.CELERY_ALWAYS_EAGER = True

        self.ss = SubmissionSet.objects.get(pk=1)
        self.ss.save()

        self.inst_slug = 'test-institution'
        self.url = "/tool/%s/submission/1/submit/" % self.inst_slug

        self.exec_dict = {
            '2-president_first_name': 'First',
            '2-president_last_name': 'Last',
            '2-president_title': 'Title',
            '2-department': 'Dept.',
            '2-email': 'test@test.edu',
            '2-president_address': 'Address',
            '2-president_city': 'City',
            '2-president_state': 'ST',
            '2-president_zip': '12345',
            '2-confirm': 'on'}

    def test_process(self):

        c = Client()
        c.login(username='test_user', password='test')

        self.confirmView(c)
        # letter is no longer part of the submission process post version 2.1
        # self.letterView(c)
        self.execContactView(c)
        self.finalizeView(c)

    def confirmView(self, c):
        """
            Test the ConfirmClassView
                - Handles a basic HTTP request w/out 500
                - Processes the form and returns a redirect to step 2
        """
        response = c.get(self.url)
        self.assertEqual(response.status_code, 200)
        response = c.post(self.url,
                          {'submit_for_rating_wizard-current_step': '0'})
        self.assertEqual(response.status_code, 200)

    def letterView(self, c):
        """
            Tests the LetterClassView
                - Handles a basic HTTP request w/out 500
                - Processes the form and redirects to step 3
        """
        letter_file = tempfile.TemporaryFile()
        letter_file.write('Some text just for the hell of it')
        letter_file.seek(0)

        post_dict = {
            'submit_for_rating_wizard-current_step': '1',
            '1-presidents_letter': letter_file,
        }
        response = c.post(self.url, post_dict)
        self.assertTrue(response.status_code == 200)

    def execContactView(self, c):
        """
            Tests the contact info step
        """
        post_dict = {'submit_for_rating_wizard-current_step': '2'}
        post_dict.update(self.exec_dict)
        response = c.post(self.url, post_dict)
        self.assertTrue(response.status_code == 200)

    def finalizeView(self, c):
        """
            Tests the final step
                - Handles a basic HTTP request w/out 500
                - Processes the form and saves the SubmissionSet object
                - Sends emails to liason, user and stars staff
                - updates institution object
        """
        post_dict = {'submit_for_rating_wizard-current_step': '3',
                     '3-confirm': 'on'}
        response = c.post(self.url, post_dict)
        self.assertEqual(response.status_code, 200)
        success_url = ("http://testserver/tool/%s/submission/1/submit/success/"
                       % self.inst_slug)
        response = c.get(success_url)
        self.assertEqual(response.status_code, 200)
