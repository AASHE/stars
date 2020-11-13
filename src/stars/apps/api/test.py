import json

from django.contrib.auth.models import User
from tastypie.models import ApiKey
from tastypie.test import ResourceTestCase

API_URI = 'http://localhost:8000/api/0.1'


class StarsApiTestCase(ResourceTestCase):

    fixtures = ['api_test_fixture.json']

    # list_path and detail_path should be set in classes derived from this one.
    list_path = ''
    detail_path = ''

    def setUp(self):
        super(StarsApiTestCase, self).setUp()

        # Create a user:
        self.user, self.created_user = User.objects.get_or_create(
            username='johndoe')

        # Create an API key for the user:
        _, self.created_api_key = ApiKey.objects.get_or_create(user=self.user)

    def tearDown(self):
        if self.created_api_key:
            ApiKey.objects.get(user=self.user).delete()
        if self.created_user:
            User.objects.get(pk=self.user.id).delete()

    # HTTP method wrappers:

    def delete(self, path):
        """Do a DELETE using the default credentials."""
        return self.api_client.delete(path,
                                      authentication=self.get_credentials())

    def get(self, path):
        """Do a GET using the default credentials."""
        return self.api_client.get(path,
                                   authentication=self.get_credentials())

    def patch(self, path, data=None):
        """Do a PATCH using the default credentials."""
        data = data or {}
        return self.api_client.patch(path,
                                     authentication=self.get_credentials(),
                                     data=data)

    def post(self, path, data=None):
        """Do a POST using the default credentials."""
        data = data or {}
        return self.api_client.post(path,
                                    authentication=self.get_credentials(),
                                    data=data)

    def put(self, path, data=None):
        """Do a PUT using the default credentials."""
        data = data or {}
        return self.api_client.put(path,
                                   authentication=self.get_credentials(),
                                   data=data)

    # Misc.

    def assertValidJSONResponseNotError(self, response):
        """Response is valid JSON and not an error message."""
        self.assertValidJSONResponse(response)
        content_dict = json.loads(response.content)
        self.assertNotIn('error_message', content_dict)

    def get_credentials(self):
        return self.create_apikey(username=self.user.username,
                                  api_key=self.user.api_key.key)

    def requires_auth(self, path):
        """Does path require authentication?"""
        resp = self.api_client.get(path)
        self.assertHttpUnauthorized(resp)


class ReadOnlyResourceTestCase(StarsApiTestCase):
    """A base test case for resources that don't allow any
    write HTTP methods (PATCH, POST, PUT, or DELETE).

    self.__class__.__name__ is patched into the method doc strings
    below to indicate which sub class test failed.  The traceback
    provided when a test fails points to this file, which isn't
    very helpful.
    """

    # So nose won't think ReadOnlyResourceTestCase is a test that should
    # should be run when it sees ReadOnlyResourceTestCase imported.
    __test__ = False

    def test_delete_not_allowed(self):
        """No DELETE requests are allowed"""
        self._testMethodDoc += ' ({0}).'.format(self.__class__.__name__)
        resp = self.delete(self.detail_path)
        self.assertHttpMethodNotAllowed(resp)

    def test_patch_not_allowed(self):
        """No PATCH requests are allowed"""
        self._testMethodDoc += ' ({0}).'.format(self.__class__.__name__)
        resp = self.patch(self.detail_path, data={})
        self.assertHttpMethodNotAllowed(resp)

    def test_post_not_allowed(self):
        """No POST requests are allowed"""
        self._testMethodDoc += ' ({0}).'.format(self.__class__.__name__)
        if self.list_path:  # DocumentationFieldSubmission has only detail_path.
            resp = self.post(self.list_path, data={})
            self.assertHttpMethodNotAllowed(resp)

    def test_put_not_allowed(self):
        """No PUT requests are allowed"""
        self._testMethodDoc += ' ({0}).'.format(self.__class__.__name__)
        resp = self.put(self.detail_path, data={})
        self.assertHttpMethodNotAllowed(resp)
