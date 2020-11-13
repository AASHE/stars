"""Tests for stars.apps.helpers.forms.views.
"""
from django.test import TestCase

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpRequest
from django.shortcuts import render
import testfixtures

from stars.apps.helpers.forms import views


class FormActionViewTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.user = User()
        self.request.user.current_inst = False
        self.request.user.is_staff = True
        self.request.session = {}
        self.request.method = 'POST'

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def test_process_form_invalid_form_error_message(self):
        """Does process_form show an error message if a form is invalid?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.helpers.forms.views.FormActionView.get_form',
                      lambda x, y, z: MockForm())
            views.FormActionView(None, None).process_form(request=self.request,
                                                          context={})
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)


class MultiFormViewTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.user = User()
        self.request.user.current_inst = False
        self.request.user.is_staff = True
        self.request.session = {}
        self.request.method = 'POST'

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def test_process_forms_invalid_form_error_message(self):
        """Does test_process display an error message if a form is invalid?
        """
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.helpers.forms.views.MultiFormView.get_form_list',
                lambda x, y, z: ({'mock_form': MockForm()}, {}))
            views.MultiFormView().process_forms(self.request, {})
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors' in
                        error_message_divs[0].text)


class MockForm(object):

    def is_valid(self):
        return False
