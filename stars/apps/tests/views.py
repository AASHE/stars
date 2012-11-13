"""Base tests for views.
"""
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client


class ViewTest(TestCase):
    """
        Provides a base TestCase that checks if a view;

            1. is GET-able, and;

            2. returns a loadable success_url.
    """
    view_class = None  # Must be set in subclass.

    # List of middlewares that should be applied to the request
    # passed to the view:
    middleware = [SessionMiddleware]

    def setUp(self):
        self.request = self._get_middleworn_request()
        self.request.method = 'GET'

    def test_get_succeeds(self, **kwargs):
        """Is view.as_view() GET-able?
        """
        response = self.view_class.as_view()(self.request, **kwargs)
        self.assertEqual(response.status_code, 200)

    def test_success_url_is_loadable(self, **kwargs):
        """Is the url returned by get_success_url() loadable?
        """
        view = self.view_class()
        # Hack a request object onto the view, since it'll be
        # referenced if no success_url or success_url_name is specified
        # in the view:
        view.request = self.request
        success_url = view.get_success_url(**kwargs)
        response = Client().get(success_url, follow=True)
        self.assertEqual(response.status_code, 200)

    def _get_middleworn_request(self):
        request = HttpRequest()
        for mw in self.middleware:
            mw().process_request(request)
        return request


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
               not satisfied, and;

            3. returns a loadable success_url when the gatekeeper
               rule is satisfied.
    """
    def open_gate(self):
        raise NotImplemented

    def close_gate(self):
        raise NotImplemented

    def test_get_succeeds(self, **kwargs):
        """Is view.as_view() GET-able when the gate is open?
        """
        self.open_gate()
        super(ProtectedViewTest, self).test_get_succeeds(**kwargs)

    def test_get_is_blocked(self, **kwargs):
        """Is view_class.as_view() blocked when the gate is closed?
        """
        self.close_gate()
        response = self.view_class.as_view()(self.request, **kwargs)
        self.assertEqual(response.status_code, 403)

    def test_success_url_is_loadable(self, **kwargs):
        """Is the url returned by get_success_url() loadable?
        """
        self.open_gate()
        super(ProtectedViewTest, self).test_success_url_is_loadable(**kwargs)
