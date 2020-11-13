"""Tests for apps.tool.views.
"""
import re

from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.core.exceptions import SuspiciousOperation
from django.http import Http404
from mock import patch

from stars.apps.test_utils.views import (ProtectedFormMixinViewTest,
                                         ProtectedViewTest, ViewTest)
from stars.apps.tool.views import (NoStarsAccountView, ToolLandingPageView,
                                   SelectInstitutionView, SummaryToolView)
from stars.test_factories.models import (CreditSetFactory,
                                         InstitutionFactory,
                                         StarsAccountFactory,
                                         SubmissionSetFactory,
                                         UserFactory,
                                         UserProfileFactory)

import logical_rules  # loads rules   # noqa


class InstitutionToolMixinTest(ProtectedFormMixinViewTest):
    """
        Provides a base TestCase for views that inherit from
        InstitutionToolMixin.
    """
    blessed_user_level = None  # user_level that should be allowed to GET
    blocked_user_level = None  # user_level that should be blocked
    middleware = ProtectedFormMixinViewTest.middleware + [MessageMiddleware]

    def setUp(self):
        super(InstitutionToolMixinTest, self).setUp()
        self.institution = InstitutionFactory(slug='on-the-beach-soldier')
        self.account = StarsAccountFactory(institution=self.institution)
        self.request.user = self.account.user
        creditset = CreditSetFactory()
        self.submission = SubmissionSetFactory(
            institution=self.institution,
            creditset=creditset)

    def open_gate(self):
        self._assign_user_level(self.blessed_user_level)

    def close_gate(self):
        self._assign_user_level(self.blocked_user_level)

    def _assign_user_level(self, user_level):
        self.account.user_level = user_level
        self.account.save()

    def _get_pk(self):
        """
            Provides the value for the kwarg named 'pk' that's
            passed to the view's on_view() product.
        """
        return ''

    def test_success_url_is_loadable(self, **kwargs):
        if kwargs != {}:
            super(InstitutionToolMixinTest, self).test_get_succeeds(**kwargs)
        else:
            super(InstitutionToolMixinTest, self).test_get_succeeds(
                institution_slug=self.institution.slug,
                pk=self._get_pk())

    def test_get_succeeds(self, **kwargs):
        if kwargs != {}:
            super(InstitutionToolMixinTest, self).test_get_succeeds(**kwargs)
        else:
            super(InstitutionToolMixinTest, self).test_get_succeeds(
                institution_slug=self.institution.slug,
                pk=self._get_pk())

    def test_get_is_blocked(self, **kwargs):
        if kwargs != {}:
            super(InstitutionToolMixinTest, self).test_get_is_blocked(**kwargs)
        else:
            super(InstitutionToolMixinTest, self).test_get_is_blocked(
                institution_slug=self.institution.slug,
                pk=self._get_pk())


class InstitutionAdminToolMixinTest(InstitutionToolMixinTest):
    """
        Provides a base TestCase for InstitutionToolMixinTests that
        are protected; only admin users can GET them.
    """
    blessed_user_level = 'admin'
    blocked_user_level = ''
    view_class = None  # Must be set in subclass.


class InstitutionViewOnlyToolMixinTest(InstitutionToolMixinTest):
    """
       Base class for InstitutionToolMixin views that are accessible
       by users with at least 'view' access for the institution.
    """
    blessed_user_level = 'view'
    blocked_user_level = ''


class UserCanEditSubmissionMixinTest(ProtectedViewTest):
    """
        Provides a base TestCase for views that inherit from
        UserCanEditSubmissionMixin.
    """

    def setUp(self):
        super(UserCanEditSubmissionMixinTest, self).setUp()
        self.institution = InstitutionFactory(slug='on-the-beach-soldier')
        self.account = StarsAccountFactory(institution=self.institution)
        self.request.user = self.account.user
        creditset = CreditSetFactory()
        self.submission = SubmissionSetFactory(
            institution=self.institution,
            creditset=creditset)

    def open_gate(self):
        self._make_submission_editable()
        self.account.user_level = 'submit'
        self.account.save()

    def close_gate(self):
        self._make_submission_uneditable()

    def _make_submission_editable(self):
        self.submission.status = 'f'
        self.institution.current_submission = self.submission

    def _make_submission_uneditable(self):
        self.submission.status = 'r'

    def test_get_succeeds(self, **kwargs):
        super(UserCanEditSubmissionMixinTest, self).test_get_succeeds(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id),
            **kwargs)

    def test_get_is_blocked(self, **kwargs):
        super(UserCanEditSubmissionMixinTest, self).test_get_is_blocked(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id),
            **kwargs)


class SubmissionSetIsNotLockedMixinTest(ProtectedViewTest):
    """
        Provides a base TestCase for views that inherit from
        SubmissionSetIsNotLockedMixin.
    """

    def setUp(self):
        super(SubmissionSetIsNotLockedMixinTest, self).setUp()
        self.institution = InstitutionFactory(slug='hey-baby-you-look-lonely')
        self.account = StarsAccountFactory(institution=self.institution)
        self.request.user = self.account.user
        self.submission = SubmissionSetFactory(institution=self.institution)

    def open_gate(self):
        self._unlock_submission()

    def close_gate(self):
        self._lock_submission()

    def _unlock_submission(self):
        self.submission.is_locked = False

    def _lock_submission(self):
        self.submission.is_locked = True

    def test_get_succeeds(self, **kwargs):
        super(SubmissionSetIsNotLockedMixinTest, self).test_get_succeeds(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id))

    def test_get_is_blocked(self, **kwargs):
        super(SubmissionSetIsNotLockedMixinTest, self).test_get_is_blocked(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id))


class NoStarsAccountViewTest(ViewTest):

    middleware = (ViewTest.middleware +
                  [AuthenticationMiddleware])
    view_class = NoStarsAccountView

    def setUp(self):
        super(NoStarsAccountViewTest, self).setUp()
        # changed
        # self.user_aashe_account = MemberSuitePortalUserFactory()
        # self.user_aashe_account = AASHEAccountFactory()
        self.user_aashe_account = UserProfileFactory()
        self.user = self.user_aashe_account.user
        self.request.user = self.user
        self.view = self.view_class()

    def test_get_institution_empty_profile_instlist(self):
        """Does get_institution work when profile has no institutions?"""
        self.assertEqual(self.view.get_institution(user=self.user),
                         None)

    def test_get_liaison_name(self):
        institution = InstitutionFactory(
            contact_first_name='William',
            contact_middle_name='S',
            contact_last_name='Burroughs')
        self.assertEqual(self.view.get_liaison_name(institution),
                         'William S Burroughs')

    def test_get_liaison_name_no_middle_name(self):
        institution = InstitutionFactory(
            contact_first_name='William',
            contact_last_name='Burroughs')
        self.assertEqual(self.view.get_liaison_name(institution),
                         'William Burroughs')


class SelectInstitutionViewTest(ViewTest):

    middleware = ViewTest.middleware + [AuthenticationMiddleware]
    view_class = SelectInstitutionView

    def setUp(self):
        """
            Creates some data to show on the page.
            Gives ViewTest.test_get_succeeds a little bit
            more of a work out.
        """
        super(SelectInstitutionViewTest, self).setUp()
        institution = InstitutionFactory()
        stars_account = StarsAccountFactory(institution=institution,
                                            user=UserFactory())
        self.request.user = stars_account.user


class SummaryToolViewTest(InstitutionViewOnlyToolMixinTest):
    view_class = SummaryToolView

    def test_get_with_no_slug_raises_page_not_found(self):
        """Does a GET w/no institution slug raise a 404?"""
        with self.assertRaises(Http404):
            self.view_class.as_view()(self.request,
                                      institution_slug='')


class ToolLandingPageViewTest(ViewTest):
    view_class = ToolLandingPageView

    def setUp(self):
        super(ToolLandingPageViewTest, self).setUp()
        self.request.user = UserFactory()

    def test_get_succeeds(self):
        """Is view.as_view() GET-able?
        """
        super(ToolLandingPageViewTest, self).test_get_succeeds(
            status_code=301)

    def test_redirect_when_no_stars_account(self):
        """Is the redirection when the user has no STARS accounts correct?"""
        with patch('stars.apps.tool.views.reverse') as reverse_mock:
            try:
                self.view_class.as_view()(request=self.request)
            except SuspiciousOperation:  # Django doesn't like reverse mocked.
                pass
            reverse_mock.assert_called_with('no-stars-account')

    def test_redirect_when_one_stars_account(self):
        """Is the redirection when the user has one STARS account correct?"""
        stars_account = StarsAccountFactory(user=self.request.user)
        with patch('stars.apps.tool.views.reverse') as reverse_mock:
            try:
                self.view_class.as_view()(request=self.request)
            except SuspiciousOperation:  # Django doesn't like reverse mocked.
                pass
            reverse_mock.assert_called_with(
                'tool-summary',
                kwargs={'institution_slug':
                        stars_account.institution.slug})

    def test_redirect_when_many_stars_accounts(self):
        """Is the redirection when the user has >1 STARS accounts correct?"""
        for i in (1, 2):
            StarsAccountFactory(user=self.request.user)
        with patch('stars.apps.tool.views.reverse') as reverse_mock:
            try:
                self.view_class.as_view()(request=self.request)
            except SuspiciousOperation:  # Django doesn't like reverse mocked.
                pass
            reverse_mock.assert_called_with('select-institution')
