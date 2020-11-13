"""
Tests for the STARS credits API.

These are included in stars/apps/credits/tests/__init__.py.
"""
import unittest

from stars.apps.api.test import ReadOnlyResourceTestCase


AUTH = 'off'  # change to 'on' when authorization is turned back on
BASE_API_PATH = '/api/0.1/credits/'


class CreditSetResourceTestCase(ReadOnlyResourceTestCase):

    list_path = BASE_API_PATH + 'creditset/'
    detail_path = list_path + '4/'
    __test__ = True  # Override ReadOnlyResourceTestCase.__test__ for nose.

    @unittest.skipIf(AUTH != 'on', 'authorization checking disabled')
    def test_get_creditset_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_creditset_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    @unittest.skipIf(AUTH != 'on', 'authorization checking disabled')
    def test_get_creditset_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_creditset_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponseNotError(resp)


class CategoryResourceTestCase(ReadOnlyResourceTestCase):

    list_path = BASE_API_PATH + 'category/'
    detail_path = list_path + '6/'
    __test__ = True  # Override ReadOnlyResourceTestCase.__test__ for nose.

    @unittest.skipIf(AUTH != 'on', 'authorization checking disabled')
    def test_get_category_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_category_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    @unittest.skipIf(AUTH != 'on', 'authorization checking disabled')
    def test_get_category_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_category_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponseNotError(resp)


class SubcategoryResourceTestCase(ReadOnlyResourceTestCase):

    list_path = BASE_API_PATH + 'subcategory/'
    detail_path = list_path + '21/'
    __test__ = True  # Override ReadOnlyResourceTestCase.__test__ for nose.

    @unittest.skipIf(AUTH != 'on', 'authorization checking disabled')
    def test_get_subcategory_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_subcategory_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    @unittest.skipIf(AUTH != 'on', 'authorization checking disabled')
    def test_get_subcategory_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_subcategory_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponseNotError(resp)


class CreditResourceTestCase(ReadOnlyResourceTestCase):

    list_path = BASE_API_PATH + 'credit/'
    detail_path = list_path + '143/'
    __test__ = True  # Override ReadOnlyResourceTestCase.__test__ for nose.

    @unittest.skipIf(AUTH != 'on', 'authorization checking disabled')
    def test_get_credit_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_credit_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    @unittest.skipIf(AUTH != 'on', 'authorization checking disabled')
    def test_get_credit_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_credit_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponseNotError(resp)


class DocumentationFieldResourceTestCase(ReadOnlyResourceTestCase):

    list_path = BASE_API_PATH + 'field/'
    detail_path = list_path + '26/'
    __test__ = True  # Override ReadOnlyResourceTestCase.__test__ for nose.

    @unittest.skipIf(AUTH != 'on', 'authorization checking disabled')
    def test_get_documentation_field_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_documentation_field_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    @unittest.skipIf(AUTH != 'on', 'authorization checking disabled')
    def test_get_documentation_field_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_documentation_field_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponseNotError(resp)
