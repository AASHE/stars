"""Base tests for views.
"""
import unittest

from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client


class ViewTest(TestCase):
    """
        Provides a base TestCase that checks if a view is GET-able.
    """
    view_class = None  # Must be set in subclass.

    # List of middlewares that should be applied to the request
    # passed to the view:
    middleware = [SessionMiddleware, MessageMiddleware]

    def setUp(self):
        self.request = self._get_middleworn_request()
        self.request.method = 'GET'

    def test_get_succeeds(self, status_code=200, **kwargs):
        """Is view.as_view() GET-able?

        Checks if the status code of the response is equal to status_code,
        which defaults to 200.  Maybe your view returns a redirect, though,
        so a successful GET returns a 301 -- so status_code can be
        specified.
        """
        if self.view_class == None:
            # Test is only meant to be run in subclass wher view_class is set
            return
        response = self.view_class.as_view()(self.request, **kwargs)
        self.assertEqual(response.status_code, status_code)

    def _get_middleworn_request(self):
        request = HttpRequest()
        for mw in self.middleware:
            mw().process_request(request)
        return request


class FormMixinViewTest(ViewTest):
    """
        Adds a test to check that a view's success_url is loadable to
        those defined in ViewTest.
    """

    def test_success_url_is_loadable(self, **kwargs):
        """Is the url returned by get_success_url() loadable?
        """
        view = self.view_class()
        if self.view_class == None:
            # Test is only meant to be run in subclass wher view_class is set
            return
        # Hack a request object onto the view, since it'll be
        # referenced if no success_url or success_url_name is specified
        # in the view:
        view.request = self.request
        success_url = view.get_success_url(**kwargs)
        response = Client().get(success_url, follow=True)
        self.assertEqual(response.status_code, 200)


class ProtectedViewTest(ViewTest):
    """
        Provides a base TestCase for views that are protected.

        The protection is implemented by the open_gate and close_gate
        methods.  open_gate should set the conditions for the view's
        protection rules to be satisfied; close_gate should do the
        opposite.

        The tests performed check that;

            1. the view is GET-able when the gatekeeper rule is
               satisfied;

            2. is *non* GET-able when the gatekeeper rule is
               not satisfied.
    """

    def open_gate(self):
        raise NotImplemented

    def close_gate(self):
        raise NotImplemented

    def test_get_succeeds(self, **kwargs):
        """Is view.as_view() GET-able when the gate is open?
        """
        if self.view_class == None:
            # Test is only meant to be run in subclass wher view_class is set
            return
        self.open_gate()
        super(ProtectedViewTest, self).test_get_succeeds(**kwargs)

    def test_get_is_blocked(self, **kwargs):
        """Is view_class.as_view() blocked when the gate is closed?
        """
        if self.view_class == None:
            # Test is only meant to be run in subclass wher view_class is set
            return
        self.close_gate()
        self.assertRaises(PermissionDenied,
                          self.view_class.as_view(),
                          self.request,
                          **kwargs)


class ProtectedFormMixinViewTest(ProtectedViewTest, FormMixinViewTest):
    """
        Adds a test to check that a view's success_url is loadable
        when the gatekeeper rule is satisfied, to those tests defined
        in ProtectedViewTest.
    """

    def test_success_url_is_loadable(self, **kwargs):
        """Is the url returned by get_success_url() loadable?
        """
        if self.view_class == None:
            # Test is only meant to be run in subclass wher view_class is set
            return
        self.open_gate()
        super(ProtectedFormMixinViewTest,
              self).test_success_url_is_loadable(**kwargs)
