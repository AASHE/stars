"""Tests for stars.apps.helpers.forms.form_helpers.
"""
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.db import models
from django.http import HttpRequest
from django.shortcuts import render
from django.test import TestCase
import testfixtures

from stars.apps.helpers.forms import form_helpers


class FormHelpersTest(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        self.request.user = User()
        self.request.session = {}
        self.request.method = 'POST'

        # Need MessageMiddleware to add the _messages storage backend
        # to requests
        self.message_middleware = MessageMiddleware()
        self.message_middleware.process_request(self.request)

    def test_object_editing_list_error_message(self):
        """Does object_editing_list show an error message when it should?
        """
        form_helpers.object_editing_list(request=self.request,
                                         object_list=[MockObject()],
                                         form_class=MockInvalidForm,
                                         ignore_errors=False,
                                         ignore_post=False,
                                         ignore_objects=[])
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('lease correct the errors'
                        in error_message_divs[0].text)

    def test_object_editing_list_success_message(self):
        """Does object_editing_list show a message when everything is ok?
        """
        form_helpers.object_editing_list(request=self.request,
                                         object_list=[MockObject()],
                                         form_class=MockValidForm,
                                         ignore_errors=False,
                                         ignore_post=False,
                                         ignore_objects=[])
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        success_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.SUCCESS]})
        self.assertEqual(len(success_message_divs), 1)
        self.assertTrue('hanges were saved successfully'
                        in success_message_divs[0].text)

    def test_object_ordering_error_message(self):
        """Does object_ordering show an error message when it should?
        """
        form_helpers.object_ordering(request=self.request,
                                     object_list=[MockObject()],
                                     form_class=MockInvalidForm,
                                     ignore_errors=False,
                                     ignore_post=False,
                                     ignore_objects=[])
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue('Unable to update order'
                        in error_message_divs[0].text)

    def test_object_ordering_success_message(self):
        """Does object_ordering show a message when everything is ok?
        """
        form_helpers.object_ordering(request=self.request,
                                     object_list=[MockObject()],
                                     form_class=MockValidForm,
                                     ignore_errors=False,
                                     ignore_post=False,
                                     ignore_objects=[])
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        success_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.SUCCESS]})
        self.assertEqual(len(success_message_divs), 1)
        self.assertTrue('Order was updated successfully'
                        in success_message_divs[0].text)

    def test__perform_save_form_error_message(self):
        """Does _perform_save_form show an error message when it should?
        """
        FAIL_MSG = 'better luck next time'
        form_helpers._perform_save_form(request=self.request,
                                        instance=None,
                                        prefix=None,
                                        form_class=MockInvalidForm,
                                        fail_msg=FAIL_MSG)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue(FAIL_MSG in error_message_divs[0].text)

    def test__perform_save_form_success_message(self):
        """Does _perform_save_form show a success message when it should?
        """
        SAVE_MSG = 'winner!'
        form_helpers._perform_save_form(request=self.request,
                                        instance=None,
                                        prefix=None,
                                        form_class=MockValidForm,
                                        save_msg=SAVE_MSG)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        success_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.SUCCESS]})
        self.assertEqual(len(success_message_divs), 1)
        self.assertTrue(SAVE_MSG in success_message_divs[0].text)

    def test_basic_save_form_success_message(self):
        """Does basic_save_form show a success message when it should?
        """
        form_helpers.basic_save_form(request=self.request,
                                     instance=None,
                                     prefix=None,
                                     form_class=MockValidForm)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        success_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.SUCCESS]})
        self.assertEqual(len(success_message_divs), 1)
        self.assertTrue('hanges saved successfully'
                        in success_message_divs[0].text)

    def test_save_new_form_rows_invalid_form_error_message(self):
        """Does save_new_form_rows show an error msg when a form is invalid?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.helpers.forms.forms.HiddenCounterForm',
                      MockInvalidForm)
            form_helpers.save_new_form_rows(request=self.request,
                                            prefix=None,
                                            form_class=MockInvalidForm,
                                            instance_class=MockObject)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue(MockInvalidForm.COUNTER_MESSAGE
                        in error_message_divs[0].text)

    def test_save_new_form_rows_error_saving_error_message(self):
        """Does save_new_form_rows show an error msg when saving fails?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.helpers.forms.forms.HiddenCounterForm',
                      MockValidForm)
            r.replace(
                'stars.apps.helpers.forms.form_helpers._perform_save_form',
                lambda w,x,y,z,show_message: (MockValidForm(), None, False))
            form_helpers.save_new_form_rows(request=self.request,
                                            prefix=None,
                                            form_class=MockValidForm,
                                            instance_class=MockObject)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        error_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(error_message_divs), 1)
        self.assertTrue(MockValidForm.SAVE_ERROR_MESSAGE
                        in error_message_divs[0].text)

    def test_save_new_form_rows_success_message(self):
        """Does save_new_form_rows show a success message when it succeeds?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.helpers.forms.forms.HiddenCounterForm',
                      MockValidForm)
            r.replace(
                'stars.apps.helpers.forms.form_helpers._perform_save_form',
                lambda w,x,y,z,show_message: (MockValidForm(), None, True))
            form_helpers.save_new_form_rows(request=self.request,
                                            prefix=None,
                                            form_class=MockValidForm,
                                            instance_class=MockValidForm)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        success_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.SUCCESS]})
        self.assertEqual(len(success_message_divs), 1)
        self.assertTrue('1 new' and 'were created successfully'
                        in success_message_divs[0].text)

    def test_confirm_unlock_form_success_message(self):
        """Does confirm_unlock_form show a success message upon unlocking?
        """
        MODEL_LABEL = 'buick century'
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.helpers.forms.form_helpers.confirm_form',
                lambda x,y: (None, True))
            r.replace('stars.apps.helpers.forms.form_helpers._get_model_label',
                      lambda x: MODEL_LABEL)
            form_helpers.confirm_unlock_form(self.request, MockObject())
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        success_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.SUCCESS]})
        self.assertEqual(len(success_message_divs), 1)
        self.assertTrue(MODEL_LABEL and 'was unlocked'
                        in success_message_divs[0].text)

    def test_confirm_delete_form_success_message(self):
        """Does confirm_delete_form show a success message after deleting?
        """
        MODEL_LABEL = 'toyota mr2'
        with testfixtures.Replacer() as r:
            r.replace(
                'stars.apps.helpers.forms.form_helpers.confirm_form',
                lambda x,y: (None, True))
            r.replace('stars.apps.helpers.forms.form_helpers._get_model_label',
                      lambda x: MODEL_LABEL)
            form_helpers.confirm_delete_form(
                request=self.request, instance=MockObject(),
                delete_method=lambda : True)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        success_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.SUCCESS]})
        self.assertEqual(len(success_message_divs), 1)
        self.assertTrue(MODEL_LABEL and 'was deleted'
                        in success_message_divs[0].text)


class MockObject(object):

    def __init__(self):
        self.id = 1
        self.ordinal = 1

    def unlock(self):
        pass


class MockForm(models.Model):
    # Based on models.Model because tested code wants klass._meta.

    # def __init__(self, *args, **kwargs):

    def is_valid(self):
        return self._is_valid

    def has_changed(self):
        return True

    def save(self):
        return self


class MockInvalidForm(MockForm):

    COUNTER_MESSAGE = 'good dog!'

    def __init__(self, *args, **kwargs):
        self._is_valid = False
        self.errors = {'counter': self.COUNTER_MESSAGE}


class MockValidForm(MockForm):

    SAVE_ERROR_MESSAGE = 'error saving'

    def __init__(self, *args, **kwargs):
        self._is_valid = True
        self.ordinal = 1
        self.id = 1
        self.errors = self.SAVE_ERROR_MESSAGE
        self.cleaned_data = {'counter': 1}

    def save(self, *args, **kwargs):
        self.ordinal += 1
        return self

    def get_parent(self):
        return MockParent()


class MockParent(object):

    def update_ordering(self):
        return False
