"""Tests for apps/tool/manage/views.py.
"""
from logging import getLogger, CRITICAL

import logical_rules
import testfixtures
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render
from django_membersuite_auth.models import MemberSuitePortalUser
from django.test.client import Client
from selenium.webdriver.common.by import By

from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import (PendingAccount, StarsAccount,
                                            Subscription)
import stars.apps.institutions.rules  # loads rules   # noqa
from stars.apps.submissions.models import ResponsibleParty
from stars.apps.test_utils.live_server import StarsLiveServerTest
from stars.apps.tool.manage import views
from stars.apps.tool.tests.views import InstitutionAdminToolMixinTest
from stars.test_factories.models import (CreditUserSubmissionFactory,
                                         PendingAccountFactory,
                                         ResponsiblePartyFactory,
                                         SubmissionSetFactory,
                                         SubscriptionFactory,
                                         StarsAccountFactory,
                                         UserFactory,
                                         ValueDiscountFactory)
# Don't bother me:
logger = getLogger('stars')
logger.setLevel(CRITICAL)


class ContactViewTest(InstitutionAdminToolMixinTest):

    view_class = views.ContactView


class InstitutionPaymentsViewTest(InstitutionAdminToolMixinTest):

    view_class = views.InstitutionPaymentsView


class ResponsiblePartyListViewTest(InstitutionAdminToolMixinTest):

    view_class = views.ResponsiblePartyListView


class ResponsiblePartyCreateViewTest(InstitutionAdminToolMixinTest):

    view_class = views.ResponsiblePartyCreateView

    def test_post_creates_a_responsible_party(self):
        """Does a POST by an admin create a responsible party?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        responsible_party_count_before = ResponsibleParty.objects.count()
        new_responsible_party = ResponsiblePartyFactory.build(
            institution=self.institution)
        form_input = {'first_name': new_responsible_party.first_name,
                      'last_name': new_responsible_party.last_name,
                      'title': new_responsible_party.title,
                      'department': new_responsible_party.department,
                      'email': new_responsible_party.email,
                      'phone': new_responsible_party.phone}
        self.request.POST = form_input
        self.request.FILES = None
        views.ResponsiblePartyCreateView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(responsible_party_count_before + 1,
                         ResponsibleParty.objects.count())

    def test_post_incomplete_form_does_not_create_a_responsible_party(self):
        """Does POSTing an incomplete form create a responsible party?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        responsible_party_count_before = ResponsibleParty.objects.count()
        new_responsible_party = ResponsiblePartyFactory.build(
            institution=self.institution)
        form_input = {'first_name': '',
                      'last_name': new_responsible_party.last_name,
                      'title': new_responsible_party.title,
                      'department': new_responsible_party.department,
                      'email': new_responsible_party.email,
                      'phone': new_responsible_party.phone}
        self.request.POST = form_input
        self.request.FILES = None
        views.ResponsiblePartyCreateView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(responsible_party_count_before,
                         ResponsibleParty.objects.count())


class ResponsiblePartyEditViewTest(InstitutionAdminToolMixinTest):

    view_class = views.ResponsiblePartyEditView

    def setUp(self):
        super(ResponsiblePartyEditViewTest, self).setUp()
        self.responsible_party = ResponsiblePartyFactory(
            institution=self.institution)

    def _get_pk(self):
        return self.responsible_party.id


class ResponsiblePartyDeleteViewTest(InstitutionAdminToolMixinTest):

    view_class = views.ResponsiblePartyDeleteView

    def setUp(self):
        super(ResponsiblePartyDeleteViewTest, self).setUp()
        self.responsible_party = ResponsiblePartyFactory(
            institution=self.institution)

    def _get_pk(self):
        return self.responsible_party.id

    def test_delete_responsible_party_listed_with_no_credits(self):
        """Does delete for a resp. party listed with no credits succeed?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        responsible_party_count_before = ResponsibleParty.objects.count()
        self.request.POST = {}
        self.request.FILES = None
        views.ResponsiblePartyDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.responsible_party.id)
        self.assertEqual(responsible_party_count_before - 1,
                         ResponsibleParty.objects.count())

    def test_delete_responsible_party_listed_with_credits(self):
        """Is delete for a responsible party listed with credits blocked?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        self.request.POST = {}
        self.request.FILES = None
        self._make_credits_for_responsible_party()
        responsible_party_count_before = ResponsibleParty.objects.count()
        views.ResponsiblePartyDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.responsible_party.id)
        self.assertEqual(responsible_party_count_before,
                         ResponsibleParty.objects.count())

    def test_delete_responsible_party_success_message(self):
        """Is a success message shown when all is ok?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        self.request.POST = {}
        self.request.FILES = None
        views.ResponsiblePartyDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.responsible_party.id)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.INFO]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('uccessfully Deleted' in info_message_divs[0].text)

    def test_delete_responsible_party_with_credits_error_message(self):
        """Is an error shown when a deletion fails?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        self.request.POST = {}
        self.request.FILES = None
        self._make_credits_for_responsible_party()
        views.ResponsiblePartyDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.responsible_party.id)
        response = render(self.request, 'base.html')
        soup = BeautifulSoup(response.content)
        info_message_divs = soup.find_all(
            'div',
            {'class': settings.MESSAGE_TAGS[messages.ERROR]})
        self.assertEqual(len(info_message_divs), 1)
        self.assertTrue('cannot be removed' in info_message_divs[0].text)

    def _make_credits_for_responsible_party(self):
        """List some credits for this responsible_party."""
        credits = list()
        for credit in xrange(4):
            credits.append(CreditUserSubmissionFactory(
                responsible_party=self.responsible_party))


class AccountListViewTest(InstitutionAdminToolMixinTest):

    view_class = views.AccountListView

    def setUp(self):
        super(InstitutionAdminToolMixinTest, self).setUp()
        self.account.user_level = 'admin'
        self.account.save()

    def test_lists_stars_and_pending_accounts(self):
        """Are both StarsAccounts and PendingAccounts listed?"""
        accounts = [self.account]
        for i in xrange(4):
            accounts.append(StarsAccountFactory(institution=self.institution))

        pending_accounts = list()
        for account in accounts:
            pending_accounts.append(
                PendingAccountFactory(institution=self.institution))

        view = views.AccountListView.as_view()(
            self.request,
            institution_slug=self.institution.slug)
        soup = BeautifulSoup(view.rendered_content)
        table = soup.find('table')
        tbody = table.findChild('tbody')
        rows = tbody.findChildren('tr')
        self.assertEqual(len(rows), len(accounts) + len(pending_accounts))

    def test_sorting(self):
        """Are accounts sorted correctly (by email address)?"""
        def make_account(pending, email):
            if pending:
                return PendingAccountFactory(user_email=email,
                                             institution=self.institution)
            else:
                return StarsAccountFactory(user=UserFactory(email=email),
                                           institution=self.institution)

        def get_email(account):
            try:
                return account.user.email
            except KeyError:
                return account.user_email

        accounts = [make_account(pending=False, email='m@sa.com'),
                    make_account(pending=True, email='f@pa.com'),
                    make_account(pending=False, email='b@sa.com'),
                    make_account(pending=True, email='a@pa.com'),
                    make_account(pending=False, email='z@sa.com'),
                    make_account(pending=True, email='b@pa.com'),
                    self.account]

        view = views.AccountListView.as_view()(
            self.request,
            institution_slug=self.institution.slug)
        soup = BeautifulSoup(view.rendered_content)
        table = soup.find('table')
        tbody = table.findChild('tbody')

        email_tds = tbody.findChildren('td',
                                       {'class': 'account-email-address'})

        account_emails_on_page = [
            email_td.text.split()[0].strip() for email_td in email_tds
        ]

        self.assertListEqual(account_emails_on_page,
                             sorted([get_email(acct) for acct in accounts]))


class AccountCreateViewTest(InstitutionAdminToolMixinTest):

    view_class = views.AccountCreateView

    def test_form_valid_no_msportaluser_account_creates_pendingaccount(self):
        """Does form_valid() create a PendingAccount if no MS acct exists?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        pending_account_count_before = PendingAccount.objects.count()
        form_input = {'email': 'joe.hump@fixityourself.com',
                      'userlevel': 'bystr'}
        self.request.POST = form_input
        views.AccountCreateView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(pending_account_count_before + 1,
                         PendingAccount.objects.count())

    def test_form_valid_creates_starsaccount(self):
        """Does form_valid() create a StarsAccount?
        """
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        email = "joehump@fixityourself.com"
        user = User.objects.create(email=email)
        membersuite_id = "bo-o-o-o-o-o-o-gus"
        MemberSuitePortalUser.objects.create(
            membersuite_id=membersuite_id,
            user=user)
        stars_account_count_before = StarsAccount.objects.count()
        form_input = {'email': email,
                      'userlevel': 'bystr'}
        self.request.POST = form_input
        views.AccountCreateView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug)
        self.assertEqual(stars_account_count_before + 1,
                         StarsAccount.objects.count())


class AccountEditViewTest(InstitutionAdminToolMixinTest):

    view_class = views.AccountEditView

    def _get_pk(self):
        return self.account.id


class AccountDeleteViewTest(InstitutionAdminToolMixinTest):

    view_class = views.AccountDeleteView

    def _get_pk(self):
        return self.account.id

    def test_delete_stars_account(self):
        """Does deleting a stars account work?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        stars_account_count_before = StarsAccount.objects.count()
        self.request.POST = {}
        self.request.FILES = None
        views.AccountDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.account.id)
        self.assertEqual(stars_account_count_before - 1,
                         StarsAccount.objects.count())


class PendingAccountDeleteViewTest(InstitutionAdminToolMixinTest):

    view_class = views.PendingAccountDeleteView

    def setUp(self):
        super(PendingAccountDeleteViewTest, self).setUp()
        self.pending_account = PendingAccountFactory(
            institution=self.institution)

    def _get_pk(self):
        return self.pending_account.id

    def test_delete_stars_account(self):
        """Does deleting a pending account work?"""
        self.account.user_level = 'admin'
        self.account.save()
        self.request.method = 'POST'
        pending_account_count_before = PendingAccount.objects.count()
        self.request.POST = {}
        self.request.FILES = None
        views.PendingAccountDeleteView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self.pending_account.id)
        self.assertEqual(pending_account_count_before - 1,
                         PendingAccount.objects.count())


class ShareDataViewTest(InstitutionAdminToolMixinTest):

    view_class = views.ShareDataView


class MigrateOptionsViewTest(InstitutionAdminToolMixinTest):

    view_class = views.MigrateOptionsView

    def setUp(self):
        super(MigrateOptionsViewTest, self).setUp()
        self.request.user.user_level = 'admin'
        self.r_status_submissionsets = list()
        self.f_status_submissionsets = list()
        for _ in xrange(2):
            self.r_status_submissionsets.append(SubmissionSetFactory(
                institution=self.institution, status='r'))
        for _ in xrange(2):
            self.f_status_submissionsets.append(SubmissionSetFactory(
                institution=self.institution, status='f'))

    def make_institution_participant(self, institution):
        current_subscription = SubscriptionFactory(
            institution=self.institution,
            access_level=Subscription.FULL_ACCESS)
        current_subscription.save()
        self.institution.current_subscription = current_subscription
        self.institution.save()

    def make_institution_not_participant(self, institution):
        self.institution.current_submission = None
        self.institution.save()

    def test__get_available_submissions_not_participant(self):
        self.make_institution_not_participant(self.institution)
        view = views.MigrateOptionsView
        available_submissions = view._get_available_submissions(
            institution=self.institution)
        self.assertEqual(len(available_submissions),
                         len(self.r_status_submissionsets) +
                         len(self.f_status_submissionsets))

    def test__get_available_submissions_is_participant(self):
        self.make_institution_participant(self.institution)
        view = views.MigrateOptionsView
        available_submissions = view._get_available_submissions(
            institution=self.institution)
        self.assertEqual(len(available_submissions),
                         len(self.r_status_submissionsets) +
                         len(self.f_status_submissionsets))


class MigrateViewTest(InstitutionAdminToolMixinTest):
    """
        A base class for MigrateDataViewTest and MigrateVersionViewTest.
    """
    view_class = None
    # Each subclass protects itself with a rule that must be True before
    # access is granted.  That's called 'gatekeeper_aashe_rule' here:
    gatekeeper_aashe_rule = None
    # Name of the task that actually starts the migration:
    migration_task_name = None

    def setUp(self):
        super(MigrateViewTest, self).setUp()

        self.submissionset = SubmissionSetFactory(
            institution=self.institution, status='r')
        self.institution.current_submission = self.submissionset
        self.institution.save()

        current_subscription = SubscriptionFactory(
            institution=self.institution,
            access_level=Subscription.FULL_ACCESS)
        current_subscription.save()

        self.c = Client()

    def _get_pk(self):
        return self.submissionset.id

    def _stub_out_rule(self, rule_name, returns):
        """
            Deregisters a rule, and replaces it with a function that
            always returns arg named returns.
        """
        logical_rules.site.unregister(rule_name)
        logical_rules.site.register(rule_name,
                                    lambda *args: returns)

    def close_gate(self):
        super(MigrateViewTest, self).close_gate()
        self._stub_out_rule(rule_name=self.gatekeeper_aashe_rule,
                            returns=False)

    def open_gate(self):
        super(MigrateViewTest, self).open_gate()
        self._stub_out_rule(rule_name=self.gatekeeper_aashe_rule,
                            returns=True)

    def test_form_valid_starts_migration(self):
        """When all is ok, is a migration task started?
        """
        if self.migration_task_name:
            # only run in subclass where attributes are set.
            self.account.user_level = 'admin'
            self.account.save()
            self.request.method = 'POST'
            self.request.POST = {'is_locked': True}

            class migrationTask(object):
                def delay(self, *args, **kwargs):
                    return 1 / 0

            with testfixtures.Replacer() as r:
                self.open_gate()
                # stub out the migration function with a lambda that'll
                # raise a ZeroDivisionError, then we can check to
                # see if that error's raised when the migration
                # function should be called.
                r.replace('stars.apps.tool.manage.views.' +
                          self.migration_task_name,
                          migrationTask())
                self.assertRaises(ZeroDivisionError,
                                  self.view_class.as_view(),
                                  self.request,
                                  institution_slug=self.institution.slug,
                                  pk=self._get_pk())


class MigrateDataViewTest(MigrateViewTest):

    view_class = views.MigrateDataView
    gatekeeper_aashe_rule = 'user_can_migrate_from_submission'
    migration_task_name = 'perform_data_migration'


class MigrateVersionViewTest(MigrateViewTest):

    view_class = views.MigrateVersionView
    gatekeeper_aashe_rule = 'user_can_migrate_version'
    migration_task_name = 'perform_migration'

    def test_dispatch_prevents_migration_when_already_at_latest_version(self):
        """Does dispatch prevent migration if current sub is at latest version?
        """

        self.account.user_level = 'admin'
        self.account.save()

        latest_creditset = CreditSet.objects.get_latest()
        self.submissionset.creditset = latest_creditset
        self.submissionset.save()

        try:
            views.MigrateVersionView.as_view()(
                request=self.request,
                institution_slug=self.institution.slug,
                pk=self._get_pk())
        except Exception, e:
            self.assertEqual(e.__class__.__name__, "PermissionDenied")

    def test_dispatch_allows_migration_when_not_already_at_latest_version(
            self):
        """Does dispatch allow migration if current sub isn't latest version?
        """
        self.account.user_level = 'admin'
        self.account.save()

        response = views.MigrateVersionView.as_view()(
            request=self.request,
            institution_slug=self.institution.slug,
            pk=self._get_pk())
        self.assertEqual(response.status_code, 200)
