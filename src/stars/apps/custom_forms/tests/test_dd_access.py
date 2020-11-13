"""
    Test cases for 'eligibility-inquiry' url.
"""
from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.client import Client


class DataDisplayAccessTest(TestCase):
    fixtures = ['notification_emailtemplate_tests.json']

    def setUp(self):
        self.c = Client()
        self.post_dict = {
            'has_instructor': False,
            'end': u"1/2/2013",
            'name': u'Benjamin Stookey',
            'title': u'Testing',
            'city_state': u'Newport, RI',
            'summary': u'words and stuff',
            'will_publish': False,
            'affiliation': u'AASHE',
            'audience': u'no sharing!',
            'period': u"1/3/2013",
            'how_data_used': u'more words',
            'instructor': u'',
            'email': u'ben@aashe.org'
        }
        self.url = reverse('custom_forms:dd-access-request')

    def test_200_status_code(self):
        """Does the view return a 200?
        """
        response = self.c.post(self.url,
                               self.post_dict)

        self.assertEqual(response.status_code, 200)

    def test_mail_sent(self):
        """Do two emails get sent?
        """
        outgoing_mails = len(mail.outbox)
        self.c.post(self.url, self.post_dict)
        self.assertEqual((len(mail.outbox) - outgoing_mails), 2)
