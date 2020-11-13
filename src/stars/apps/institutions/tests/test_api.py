"""
Tests for institutions API.
"""
import json

from stars.apps.api.test import ReadOnlyResourceTestCase


class InstitutionResourceTestCase(ReadOnlyResourceTestCase):

    RATED_INSTITUTION = 74

    multi_db = True
    list_path = '/api/0.1/institutions/'
    detail_path = list_path + str(RATED_INSTITUTION) + '/'
    __test__ = True  # Override ReadOnlyResourceTestCase.__test__ for nose.

    def test_get_institutions_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_institutions_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_institutions_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_institutions_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)

    def test_unrated_submissionsets_are_hidden_in_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)
        institutions = json.loads(resp.content)['objects']
        for institution in institutions:
            for submission_set in institution['submission_sets']:
                self.assertFalse(
                    submission_set['rating'] in ['None', None, ''])

    # These are the names of the institutions that are
    # loaded via api_test_fixture.json.  Note that if
    # other institutions are loaded, these search tests
    # will probably fail and need to be adjusted.
    # For now, they expect the following names, and no
    # others.
    #
    # "Moraine Valley Community College"
    # "Portland State University"
    # "Western University"
    # "University of Minnesota, Duluth"

    # def test_search_name_contains(self):
    #     """Test the 'name_contains' filter for searching."""
    #     path = self.list_path + '?name_contains=iversi'
    #     resp = self.get(path)
    #     payload = json.loads(resp.content)
    #     self.assertTrue(payload['meta']['total_count'] is 3)
    #
    # def test_search_name_contains_case_insensitivity(self):
    #     """The 'name_contains' filter should be case insensitive."""
    #     path = self.list_path + '?name_contains=IVERSI'
    #     resp = self.get(path)
    #     payload = json.loads(resp.content)
    #     self.assertTrue(payload['meta']['total_count'] is 3,
    #                     'case insensitive match failed')
    #
    # def test_search_name_startswith(self):
    #     """Test the 'name_startswith' filter for searching."""
    #     path = self.list_path + '?name_startswith=Wes'
    #     resp = self.get(path)
    #     payload = json.loads(resp.content)
    #     self.assertTrue(payload['meta']['total_count'] is 1)
    #
    # def test_search_name_startswith_case_insensitivity(self):
    #     """The 'name_startswith' filter should be case insensitive."""
    #     path = self.list_path + '?name_startswith=wes'
    #     resp = self.get(path)
    #     payload = json.loads(resp.content)
    #     self.assertTrue(payload['meta']['total_count'] is 1,
    #                     'case insensitive match failed')
    #
    # def test_search_name_endswith(self):
    #     """Test the 'name_endswith' filter for searching."""
    #     path = self.list_path + '?name_endswith=sity'
    #     resp = self.get(path)
    #     payload = json.loads(resp.content)
    #     self.assertTrue(payload['meta']['total_count'] is 2)
    #
    # def test_search_name_endswith_case_insensitivity(self):
    #     """The 'name_endswith' filter should be case insensitive."""
    #     path = self.list_path + '?name_endswith=SITY'
    #     resp = self.get(path)
    #     payload = json.loads(resp.content)
    #     self.assertTrue(payload['meta']['total_count'] is 2,
    #                     'case insensitive match failed')
    #
    # def test_search_name(self):
    #     """Test the 'name' filter for searching."""
    #     path = self.list_path + '?name=Moraine Valley Community College'
    #     resp = self.get(path)
    #     print "RESPONSE: %s" % resp.content
    #     payload = json.loads(resp.content)
    #     self.assertTrue(payload['meta']['total_count'] is 1)
    #
    # def test_search_name_case_insensitivity(self):
    #     """The 'name' filter should be case insensitive."""
    #     path = self.list_path + '?name=MORAINE VALLEY COMMUNITY COLLEGE'
    #     resp = self.get(path)
    #     payload = json.loads(resp.content)
    #     self.assertTrue(payload['meta']['total_count'] is 1,
    #                     'case insensitive match failed')
