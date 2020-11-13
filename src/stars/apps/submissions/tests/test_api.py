"""
Tests for submissions API.
"""
import json

from stars.apps.api.test import ReadOnlyResourceTestCase

from stars.apps.submissions.models import (CategorySubmission,
                                           CreditUserSubmission,
                                           LongTextSubmission,
                                           SubcategorySubmission,
                                           SubmissionSet)


submissions_list_path = '/api/0.1/submissions/'


def submissions_detail_path(submissionset_id):
    return '{list_path}{submissionset_id}/'.format(
        list_path=submissions_list_path,
        submissionset_id=submissionset_id)


RATED_SUBMISSIONSET_ID = 75
UNRATED_SUBMISSIONSET_ID = 688
LOCKED_SUBMISSIONSET_ID = 429
RATED_NON_REPORTER_SUBMISSIONSET_ID = RATED_SUBMISSIONSET_ID
RATED_REPORTER_SUBMISSIONSET_ID = 113


class SubmissionSetResourceTestCase(ReadOnlyResourceTestCase):

    __test__ = True  # Override ReadOnlyResourceTestCase.__test__ for nose.

    detail_path = submissions_detail_path(RATED_SUBMISSIONSET_ID)
    list_path = submissions_list_path

    def test_get_submissions_list_requires_auth(self):
        self.requires_auth(self.list_path)

    def test_get_submissions_list(self):
        resp = self.get(self.list_path)
        self.assertValidJSONResponse(resp)

    def test_get_submissions_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_submissions_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)

    def test_get_unrated_submission(self):
        # Get a submission set that should be filtered:
        resp = self.get(submissions_detail_path(UNRATED_SUBMISSIONSET_ID))
        self.assertHttpNotFound(resp)

    def test_unrated_submissions_are_hidden(self):
        resp = self.get(self.list_path + '?limit=0')
        payload = json.loads(resp.content)
        visible_submissionsets = payload['objects']
        visible_submissionset_ids = [ss['id'] for ss
                                     in visible_submissionsets]
        self.assertNotIn(UNRATED_SUBMISSIONSET_ID,
                         visible_submissionset_ids)

    def test_get_locked_submission(self):
        # Get a submission set that should be filtered:
        resp = self.get(submissions_detail_path(LOCKED_SUBMISSIONSET_ID))
        self.assertHttpNotFound(resp)

    def test_locked_submissions_are_hidden(self):
        resp = self.get(self.list_path + '?limit=0')
        payload = json.loads(resp.content)
        visible_submissionsets = payload['objects']
        visible_submissionset_ids = [ss['id'] for ss
                                     in visible_submissionsets]
        self.assertNotIn(LOCKED_SUBMISSIONSET_ID,
                         visible_submissionset_ids)

    def test_rated_unlocked_submissions_are_visible(self):
        resp = self.get(self.list_path + '?limit=0')
        payload = json.loads(resp.content)
        visible_submissionsets = payload['objects']
        visible_submissionset_ids = [ss['id'] for ss
                                     in visible_submissionsets]
        rated_submissionset_ids = [
            submissionset.id
            for submissionset in
            SubmissionSet.objects.get_rated().filter(is_locked=False)]
        self.assertItemsEqual(visible_submissionset_ids,
                              rated_submissionset_ids)

    def test_scoring_hidden_for_reporter(self):
        path = submissions_detail_path(RATED_REPORTER_SUBMISSIONSET_ID)
        resp = self.get(path)
        payload = json.loads(resp.content)
        self.assertTrue(payload['score'] is None)

    def test_scoring_shown_for_non_reporter(self):
        path = submissions_detail_path(RATED_NON_REPORTER_SUBMISSIONSET_ID)
        resp = self.get(path)
        payload = json.loads(resp.content)
        self.assertFalse(payload['score'] is None)


class CategorySubmissionResourceTestCase(ReadOnlyResourceTestCase):

    __test__ = True  # Override ReadOnlyResourceTestCase.__test__ for nose.

    RATED_CATEGORYSUBMISSION_ID = 91
    UNRATED_CATEGORYSUBMISSION_ID = 2176

    # detail_path and list_path are defined for
    # ReadOnlyResourceTestCase tests.

    @property
    def list_path(self):
        return self._list_path(rated_submissionset=True)

    @property
    def detail_path(self):
        return self._detail_path(rated_submissionset=True)

    def _list_path(self, rated_submissionset):
        """rated_submissionset is True or False."""
        submissionset_id = (RATED_SUBMISSIONSET_ID if rated_submissionset
                            else UNRATED_SUBMISSIONSET_ID)
        return submissions_detail_path(submissionset_id) + 'category/'

    def _detail_path(self, rated_submissionset):
        """Detail URI for one CategorySubmission of a SubmissionSet.
        The CategorySubmission belongs to a SubmissionSet that's rated
        if rated_submissionset is True, otherwise it belongs to an unrated
        SubmissionSet.
        """
        catsub_id = (
            self.RATED_CATEGORYSUBMISSION_ID if rated_submissionset
            else self.UNRATED_CATEGORYSUBMISSION_ID)
        return (self._list_path(rated_submissionset) +
                self.detail_path_part(catsub_id))

    def detail_path_part(self, categorysubmission_id):
        """Detail part of path for a specific CategorySubmission."""
        categorysubmission = CategorySubmission.objects.get(
            pk=categorysubmission_id)
        return str(categorysubmission.category.id) + '/'

    def test_get_categorysubmission_list_requires_auth(self):
        self.requires_auth(self._list_path(rated_submissionset=True))

    def test_get_categorysubmission_list(self):
        resp = self.get(self._list_path(rated_submissionset=True))
        self.assertValidJSONResponse(resp)

    def test_get_categorysubmission_detail_requires_auth(self):
        self.requires_auth(self._detail_path(rated_submissionset=True))

    def test_get_categorysubmission_detail(self):
        path = self._detail_path(rated_submissionset=True)
        resp = self.get(path)
        self.assertValidJSONResponse(resp)

    def test_get_categorysubmission_for_unrated_submissionset(self):
        path = self._detail_path(rated_submissionset=False)
        resp = self.get(path)
        self.assertHttpGone(resp)


class SubcategorySubmissionResourceTestCase(ReadOnlyResourceTestCase):

    # TODO - add test for UNRATED_SUBCATEGORYSUBMISSION_ID?

    __test__ = True  # Override ReadOnlyResourceTestCase.__test__ for nose.

    RATED_SUBCATEGORYSUBMISSION_ID = 429
    UNRATED_SUBCATEGORYSUBMISSION_ID = None
    RATED_NON_REPORTER_SUBCATEGORYSUBMISSION_WITH_POINTS_ID = (
        RATED_SUBCATEGORYSUBMISSION_ID)
    RATED_REPORTER_SUBCATEGORYSUBMISSION_WITH_POINTS_ID = 1291

    # detail_path and list_path are defined for
    # ReadOnlyResourceTestCase tests.

    @property
    def list_path(self):
        return self._list_path(rated_submissionset=True)

    @property
    def detail_path(self):
        return self._detail_path(rated_submissionset=True)

    def _list_path(self, rated_submissionset):
        """List URI for the SubcategorySubmissions of a SubmissionSet.
        The SubcategorySubmissions belong to a SubmissionSet that's rated
        if rated_submissionset is True, otherwise they belong to an unrated
        SubmissionSet.
        """
        submissionset_id = (RATED_SUBMISSIONSET_ID if rated_submissionset
                            else UNRATED_SUBMISSIONSET_ID)
        return self.list_path_for_submissionset(submissionset_id)

    def list_path_for_submissionset(self, submissionset_id):
        return submissions_detail_path(submissionset_id) + 'subcategory/'

    def _detail_path(self, rated_submissionset):
        """Detail URI for one SubcategorySubmission of a SubmissionSet.
        The SubcategorySubmission belongs to a SubmissionSet that's rated
        if rated_submissionset is True, otherwise it belongs to an unrated
        SubmissionSet.
        """
        subcatsub_id = (
            self.RATED_SUBCATEGORYSUBMISSION_ID if rated_submissionset
            else self.UNRATED_SUBCATEGORYSUBMISSION_ID)
        return (self._list_path(rated_submissionset) +
                self.detail_path_part(subcatsub_id))

    def detail_path_part(self, subcategorysubmission_id):
        """Part of detail path for a specific SubcategorySubmission."""
        subcategorysubmission = SubcategorySubmission.objects.get(
            pk=subcategorysubmission_id)
        return str(subcategorysubmission.subcategory.id) + '/'

    def test_get_subcategorysubmission_list_requires_auth(self):
        self.requires_auth(self._list_path(rated_submissionset=True))

    def test_get_subcategorysubmission_list(self):
        resp = self.get(self._list_path(rated_submissionset=True))
        self.assertValidJSONResponse(resp)

    def test_get_subcategorysubmission_detail_requires_auth(self):
        self.requires_auth(self._detail_path(rated_submissionset=True))

    def test_get_subcategorysubmission_detail(self):
        path = self._detail_path(rated_submissionset=True)
        resp = self.get(path)
        self.assertValidJSONResponse(resp)

    def test_dehydrate_points(self):

        # Make sure points aren't None for everybody:
        path = (
            self.list_path_for_submissionset(
                RATED_NON_REPORTER_SUBMISSIONSET_ID) +
            self.detail_path_part(
                self.RATED_NON_REPORTER_SUBCATEGORYSUBMISSION_WITH_POINTS_ID))

        resp = self.get(path)

        self.assertValidJSONResponse(resp)
        payload = json.loads(resp.content)
        self.assertTrue(payload['points'] is not None)

        # Now check that they're None for reporters:
        path = (
            self.list_path_for_submissionset(
                RATED_REPORTER_SUBMISSIONSET_ID) +
            self.detail_path_part(
                self.RATED_REPORTER_SUBCATEGORYSUBMISSION_WITH_POINTS_ID))

        resp = self.get(path)

        self.assertValidJSONResponse(resp)
        payload = json.loads(resp.content)
        self.assertTrue(payload['points'] is None)


class CreditSubmissionResourceTestCase(ReadOnlyResourceTestCase):

    # TODO - add test for UNRATED_CREDITSUBMISSION_ID?

    __test__ = True  # Override ReadOnlyResourceTestCase.__test__ for nose.

    RATED_CREDITSUBMISSION_ID = 3475
    UNRATED_CREDITSUBMISSION_ID = None

    # detail_path and list_path are defined for
    # ReadOnlyResourceTestCase tests.

    @property
    def list_path(self):
        return self._list_path(rated_submissionset=True)

    @property
    def detail_path(self):
        return self._detail_path(rated_submissionset=True)

    def _list_path(self, rated_submissionset):
        """List URI for the CreditSubmissions of a SubmissionSet.
        The CreditSubmissions belong to a SubmissionSet that's rated
        if rated_submissionset is True, otherwise they belong to an unrated
        SubmissionSet.
        """
        submissionset_id = (RATED_SUBMISSIONSET_ID if rated_submissionset
                            else UNRATED_SUBMISSIONSET_ID)
        return submissions_detail_path(submissionset_id) + 'credit/'

    def _detail_path(self, rated_submissionset):
        """Detail URI for one CreditSubmission of a SubmissionSet.
        The CreditSubmission belongs to a SubmissionSet that's rated
        if rated_submissionset is True, otherwise it belongs to an unrated
        SubmissionSet.
        """
        creditsubmission_id = (
            self.RATED_CREDITSUBMISSION_ID if rated_submissionset
            else self.UNRATED_CREDITSUBMISSION_ID)
        creditsubmission = CreditUserSubmission.objects.get(
            pk=creditsubmission_id)
        return (self._list_path(rated_submissionset) +
                str(creditsubmission.credit.id) + '/')

    def test_get_creditsubmission_list_requires_auth(self):
        self.requires_auth(self._list_path(rated_submissionset=True))

    def test_get_creditsubmission_list(self):
        resp = self.get(self._list_path(rated_submissionset=True))
        self.assertValidJSONResponse(resp)

    def test_get_creditsubmission_detail_requires_auth(self):
        self.requires_auth(self._detail_path(rated_submissionset=True))

    def test_get_creditsubmission_detail(self):
        path = self._detail_path(rated_submissionset=True)
        resp = self.get(path)
        self.assertValidJSONResponse(resp)


class DocumentationFieldSubmissionResourceTestCase(ReadOnlyResourceTestCase):

    # TODO - add test for UNRATED_DOCUMENTATIONFIELDSUBMISSION_ID?

    __test__ = True  # Override ReadOnlyResourceTestCase.__test__ for nose.

    RATED_DOCUMENTATIONFIELDSUBMISSION_ID = 10345
    UNRATED_DOCUMENTATIONFIELDSUBMISSION_ID = None

    # For ReadOnlyResourceTestCase tests, list_path and must be defined:
    list_path = None

    # For ReadOnlyResourceTestCase tests, detail_path and must be available
    # as an attribute of the class, not a method:
    @property
    def detail_path(self):
        return self._detail_path(rated_submissionset=True)

    def _detail_path(self, rated_submissionset):
        """Detail URI for one DocumentationFieldSubmission of a
        SubmissionSet.  The DocumentationFieldSubmission belongs to a
        SubmissionSet that's rated if rated_submissionset is True,
        otherwise it belongs to an unrated SubmissionSet.
        """
        submissionset_id = (RATED_SUBMISSIONSET_ID if rated_submissionset
                            else UNRATED_SUBMISSIONSET_ID)
        documenatationfieldsubmission_id = (
            self.RATED_DOCUMENTATIONFIELDSUBMISSION_ID if rated_submissionset
            else self.UNRATED_DOCUMENTATIONFIELDSUBMISSION_ID)
        documentationfieldsubmission = LongTextSubmission.objects.get(
            pk=documenatationfieldsubmission_id)
        return (submissions_detail_path(submissionset_id) + 'field/' +
                str(documentationfieldsubmission.documentation_field.id) + '/')

    def test_get_documentationfieldsubmission_detail_requires_auth(self):
        self.requires_auth(self.detail_path)

    def test_get_documentationfieldsubmission_detail(self):
        resp = self.get(self.detail_path)
        self.assertValidJSONResponse(resp)
