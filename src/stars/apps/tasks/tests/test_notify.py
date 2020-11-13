""" Doctests for the registration notification tool that will notify
    institutions that it has been over (4) weeks since they registered
    and haven't paid

    Test premises:
        - Ensure that `get_overdue_payments` returns the
          correct Submission Sets

"""
from datetime import date

from django.test import TestCase
from django.core import mail

from stars.apps.tasks.notifications import (get_new_institutions,
                                            get_overdue_payments,
                                            send_notification,
                                            send_notification_set,
                                            send_post_submission_survey,
                                            send_welcome_email)
from stars.apps.notifications.models import EmailTemplate


class NotificationTest(TestCase):
    fixtures = ['notification_test.json',
                'notification_emailtemplate_tests.json']

    def setUp(self):
        et = EmailTemplate(slug='test', description='test',
                           content="testing: {{ val }}")
        et.save()

    def test_post_submission_survey(self):
        """
            send_post_submission_survey
        """
        mail.outbox = []
        today = date(year=2011, month=1, day=14)
        send_post_submission_survey(today)
        self.assertTrue(len(mail.outbox) == 0)

        today = date(year=2011, month=1, day=15)
        send_post_submission_survey(today)
        self.assertTrue(len(mail.outbox) == 1)

        today = date(year=2011, month=1, day=16)
        send_post_submission_survey(today)
        self.assertTrue(len(mail.outbox) == 2)

        today = date(year=2011, month=1, day=17)
        send_post_submission_survey(today)
        self.assertTrue(len(mail.outbox) == 2)

    def test_send_notification_set(self):
        """
            send_notification_set
        """
        mail.outbox = []

        set = [{'mail_to': ['ben@aashe.org'], 'template_slug': 'test',
                'n_type': 'tst', 'identifier': 'tst_1',
                'email_context': {"val": "testval"}},
               {'mail_to': ['ben@aashe.org'], 'template_slug': 'test',
                'n_type': 'tst', 'identifier': 'tst_2',
                'email_context': {"val": "testval"}},
               {'mail_to': ['ben@aashe.org'], 'template_slug': 'test',
                'n_type': 'tst', 'identifier': 'tst_3',
                'email_context': {"val": "testval"}},
               {'mail_to': ['ben@aashe.org'], 'template_slug': 'test',
                'n_type': 'tst', 'identifier': 'tst_1',
                'email_context': {"val": "testval"}}]
        send_notification_set(set)
        self.assertTrue(len(mail.outbox) == 3)

    def testWelcomeList(self):
        """
            - Ensure that `get_new_institutions` returns the
              correct institutions
        """
        today = date(year=2010, month=5, day=28)
        ss_list = get_new_institutions(today)
        self.assertTrue(len(ss_list) == 0)

        today = date(year=2010, month=5, day=29)
        ss_list = get_new_institutions(today)
        self.assertTrue(len(ss_list) == 0)

        today = date(year=2010, month=6, day=5)
        ss_list = get_new_institutions(today)
        self.assertTrue(len(ss_list) == 1)

        today = date(year=2010, month=6, day=6)
        ss_list = get_new_institutions(today)
        self.assertTrue(len(ss_list) == 2)

    def testWelcomeNotify(self):

        mail.outbox = []

        current_date = date(year=2010, month=5, day=28)
        send_welcome_email(current_date)
        self.assertTrue(len(mail.outbox) == 0)

        current_date = date(year=2010, month=6, day=5)
        send_welcome_email(current_date)
        self.assertTrue(len(mail.outbox) == 1)

        current_date = date(year=2010, month=6, day=6)
        send_welcome_email(current_date)
        # Only one more should be sent, because of the count limit
        # on notifications
        self.assertTrue(len(mail.outbox) == 2)

        # no duplicates
        send_welcome_email(current_date)
        self.assertTrue(len(mail.outbox) == 2)

    def testOverdueList(self):
        """
            Tests:
                - Ensure that `get_overdue_payments` returns the
                  correct SubmissionSets
        """

        today = date(year=2010, month=5, day=29)
        ss_list = get_overdue_payments(4, today)
        self.assertTrue(len(ss_list) == 1)

        today = date(year=2010, month=5, day=31)
        ss_list = get_overdue_payments(4, today)
        self.assertTrue(len(ss_list) == 2)

        today = date(year=2010, month=5, day=25)
        ss_list = get_overdue_payments(4, today)
        self.assertTrue(len(ss_list) == 0)

    def test_send_notification(self):
        """
            Tests:
                - notifications only get sent `count` times
                  (EmailNotification objects created)
                - email shows up in outbox
        """
        mail.outbox = []

        for i in range(0, 3):
            send_notification("tst", "test_1", ["ben@aashe.org"],
                              'test', {'val': "test val"}, count=2)

        self.assertTrue(len(mail.outbox) == 2)
