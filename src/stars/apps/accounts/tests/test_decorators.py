"""Tests for apps/accounts/decorators.py.
"""
from django.test import TestCase

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpRequest
from django.shortcuts import render

from stars.apps.accounts import decorators


class DecoratorsTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.user = User()
        self.request.user.has_perm = lambda x: True
        self.request.user.is_authenticated = lambda: True
        self.request.user.is_staff = True
        self.request.session = {}
        self.request.method = 'POST'

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def test_redirect_to_login_please_login_message(self):
        """Does _redirect_to_login show a 'please login' message?
        """
        _ = decorators._redirect_to_login(self.request)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.INFO]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('lease login to access' in info_message_divs[0].text)
