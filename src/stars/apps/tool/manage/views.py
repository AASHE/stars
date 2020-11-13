from logging import getLogger

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import (CreateView, DeleteView, FormView, ListView,
                                  TemplateView, UpdateView)

# from stars.apps.accounts import xml_rpc
from stars.apps.credits.models import CreditSet
from stars.apps.helpers.forms import form_helpers
from stars.apps.helpers.mixins import ValidationMessageFormMixin
from stars.apps.institutions.models import (StarsAccount,
                                            SubscriptionPayment,
                                            PendingAccount)
from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.tasks import (perform_migration,
                                          perform_data_migration)
from stars.apps.third_parties.tasks import build_csv_export, build_pdf_export
from stars.apps.third_parties.models import ThirdParty
from stars.apps.tool.manage.forms import (AccountForm,
                                          InstitutionPreferences,
                                          MigrateSubmissionSetForm,
                                          NotifyUsersForm,
                                          ParticipantContactForm,
                                          ResponsibleParty,
                                          ResponsiblePartyForm,
                                          ThirdPartiesForm)
from stars.apps.tool.mixins import InstitutionAdminToolMixin
from stars.apps.download_async_task.views import (StartExportView,
                                                  DownloadExportView)

logger = getLogger('stars.request')


def _update_preferences(request, institution):
    """
        Helper method to DRY code around managing institution preferences
        Returns (preferences, preferences_form)
    """
    try:
        preferences = institution.preferences
    except InstitutionPreferences.DoesNotExist:
        preferences = InstitutionPreferences(institution=institution)
    (notify_form, saved) = form_helpers.basic_save_form(
        request, preferences, '', NotifyUsersForm, show_message=False)
    return (preferences, notify_form)


def get_user_level_description(user_level):
    """Returns the description for a user level."""
    permissions = dict(settings.STARS_PERMISSIONS)
    try:
        return permissions[user_level]
    except KeyError:
        return user_level


class ContactView(InstitutionAdminToolMixin, ValidationMessageFormMixin,
                  UpdateView):
    """
        Displays the contact form for an institution
    """
    tab_content_title = 'contact'
    template_name = 'tool/manage/detail.html'
    form_class = ParticipantContactForm

    def get_object(self):
        return self.get_institution()


class InstitutionPaymentsView(InstitutionAdminToolMixin, ListView):
    """
        Displays a list of payments made by an institution.
    """
    context_object_name = 'payment_list'
    tab_content_title = 'payments'
    template_name = 'tool/manage/payments.html'

    def get_queryset(self):
        current_inst = self.get_institution()
        return SubscriptionPayment.objects.filter(
            subscription__institution=current_inst).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super(InstitutionPaymentsView, self).get_context_data(
            **kwargs)
        current_inst = self.get_institution()
        context['subscription_list'] = current_inst.subscription_set.all()
        context['current_inst'] = current_inst
        return context


class ResponsiblePartyListView(InstitutionAdminToolMixin, ListView):
    """
        Displays a list of responsible parties for an institution.
    """
    tab_content_title = 'responsible parties'
    template_name = 'tool/manage/responsible_party_list.html'

    def get_queryset(self):
        current_inst = self.get_institution()
        return current_inst.responsibleparty_set.all()


class ResponsiblePartyEditView(InstitutionAdminToolMixin,
                               ValidationMessageFormMixin,
                               UpdateView):
    """
        Provides a form to edit a responsible party.
    """
    context_object_name = 'responsible_party'
    form_class = ResponsiblePartyForm
    model = ResponsibleParty
    success_url_name = 'tool:manage:responsible-party-list'
    tab_content_title = 'edit a responsible party'
    template_name = 'tool/manage/responsible_party_edit.html'

    def get_context_data(self, **kwargs):
        context = super(ResponsiblePartyEditView, self).get_context_data(
            **kwargs)
        context['credit_list'] = (
            self.get_object().get_creditusersubmissions().all())
        return context


class ResponsiblePartyDeleteView(InstitutionAdminToolMixin,
                                 ValidationMessageFormMixin,
                                 DeleteView):
    """
       Deletes a responsible party if they aren't tied to any submissions.
    """
    model = ResponsibleParty
    success_url_name = 'tool:manage:responsible-party-list'
    tab_content_title = 'delete a responsible party'
    template_name = 'tool/manage/responsible_party_confirm_delete.html'

    def delete(self, *args, **kwargs):
        """
            Prevents this responsible party from being deleted if
            there are credits related to it.
        """
        responsible_party = self.get_object()
        if self.get_object().get_creditusersubmissions().count():
            messages.error(self.request,
                           "This Responsible Party cannot be removed because "
                           "he/she is listed with one or more credits.")
            return HttpResponseRedirect(
                reverse(
                    'tool:manage:responsible-party-list',
                    kwargs={'institution_slug': self.get_institution().slug}))

        else:
            messages.info(self.request,
                          "Successfully Deleted Responsible Party: %s" %
                          responsible_party)
            return super(ResponsiblePartyDeleteView, self).delete(*args,
                                                                  **kwargs)


class ResponsiblePartyCreateView(InstitutionAdminToolMixin,
                                 ValidationMessageFormMixin,
                                 CreateView):
    """
        Provides a form to create a responsible party.
    """
    form_class = ResponsiblePartyForm
    model = ResponsibleParty
    success_url_name = 'tool:manage:responsible-party-list'
    tab_content_title = 'add a responsible party'
    template_name = 'tool/manage/responsible_party_edit.html'
    valid_message = 'Responsible Party Added.'

    def form_valid(self, form):
        """
            Attach the current institution to the responsible party before
            it's saved.
        """
        self.object = form.save(commit=False)
        self.object.institution = self.get_institution()
        self.object.save()
        return super(ResponsiblePartyCreateView, self).form_valid(form)


class AccountListView(InstitutionAdminToolMixin, TemplateView):
    """
        Displays a list of user accounts for an institution.
    """
    tab_content_title = 'users'
    template_name = 'tool/manage/account_list.html'

    def _get_accounts(self):
        institution = self.get_institution()
        querysets = [StarsAccount.objects.filter(institution=institution),
                     PendingAccount.objects.filter(institution=institution)]

        # I want to sort the accounts by email address.  StarsAccount
        # has a `user` attribute, and that has an `email` attribute;
        # PendingAccount doesn't have a user, but has a `user_email`
        # attribute.  Since we want to sort the heterogenous list, we
        # have to do it manually (i.e., not via order_by()).

        accounts = []
        for queryset in querysets:
            for account in queryset:
                try:
                    account.email = account.user_email
                except AttributeError:
                    account.email = account.user.email
                accounts.append(account)

        sorted_accounts = sorted(accounts, key=lambda account: account.email)

        return sorted_accounts

    def get_context_data(self, **kwargs):
        context = super(AccountListView, self).get_context_data(**kwargs)
        accounts = self._get_accounts()
        # Tuck the description of the user's role and the user's name
        # into the context:
        for account in accounts:
            account.user_level_description = get_user_level_description(
                account.user_level)
            try:
                account.user_name = ' '.join((account.user.first_name,
                                              account.user.last_name))
            except AttributeError:
                account.user_name = ''
        context['accounts'] = accounts
        return context


class AccountCreateView(
        InstitutionAdminToolMixin, ValidationMessageFormMixin, FormView):
    """
        Allows creation of StarsAccount (and PendingAccount) objects.

        If the email address provided doesn't match a StarsAccount,
        a PendingAccount is created instead.
    """
    form_class = AccountForm
    success_url_name = 'tool:manage:account-list'
    tab_content_title = 'add a user'
    template_name = 'tool/manage/account_detail.html'
    valid_message = 'Account created.'

    def __init__(self, *args, **kwargs):
        self.preferences = None
        self.notify_form = None
        super(AccountCreateView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AccountCreateView, self).get_context_data(**kwargs)
        context['notify_form'] = self.notify_form
        context['help_content_name'] = 'add_account'
        context['creating_new_account'] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        """
            Save preferences for this institution, for use in form_valid()
            and get_context_data() later.
        """
        (self.preferences, self.notify_form) = _update_preferences(
            request, Institution.objects.get(slug=kwargs['institution_slug']))
        return super(AccountCreateView, self).dispatch(
            request, *args, **kwargs)

    def form_valid(self, form):
        # Get the MemberSuite account info for this email
        user_level = form.cleaned_data['userlevel']
        user_email = form.cleaned_data['email']

        # if the user exists, create a StarsAccount
        # if they don't, then we create a Pending Account
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            user = None

        was_created = False
        if user:
            # if the user exists make sure there isn't already an account
            # before creating one
            try:
                account = StarsAccount.objects.get(
                    institution=self.get_institution(),
                    user=user)
                messages.error(
                    self.request,
                    "You already have an account for %s" % user_email)
                self.valid_message = ''
            except StarsAccount.DoesNotExist:
                account = StarsAccount.objects.create(
                    institution=self.get_institution(),
                    user_level=user_level,
                    user=user)
                was_created = True

        else:
            # if the user doesn't exist, confirm there isn't already an invites
            # before creating one
            try:
                account = PendingAccount.objects.get(
                    institution=self.get_institution(),
                    user_email=user_email)
                messages.error(
                    self.request,
                    "You have already invited %s." % user_email)
                self.valid_message = ''
            except PendingAccount.DoesNotExist:
                messages.info(self.request,
                              "An invitation has been sent to %s" % user_email)
                self.valid_message = ''
                account = PendingAccount.objects.create(
                    institution=self.get_institution(),
                    user_level=user_level,
                    user_email=user_email)
                was_created = True

        if self.preferences.notify_users and was_created:
            account.notify(
                StarsAccount.NEW_ACCOUNT,
                self.request.user,
                self.get_institution())

        return super(AccountCreateView, self).form_valid(form)


class AccountEditView(
        InstitutionAdminToolMixin, ValidationMessageFormMixin, FormView):
    """
        Provides an edit view for StarsAccount and PendingAccount objects.
    """
    form_class = AccountForm
    success_url_name = 'tool:manage:account-list'
    template_name = 'tool/manage/account_detail.html'
    tab_content_title = 'edit a user'
    valid_message = 'User updated.'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.account = StarsAccount.objects.get(id=kwargs['pk'])
        except StarsAccount.DoesNotExist:
            self.account = get_object_or_404(PendingAccount, id=kwargs['pk'])
        return super(AccountEditView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AccountEditView, self).get_context_data(
            **kwargs)
        context['help_content_name'] = 'edit_account'
        context['creating_new_account'] = False
        return context

    def get_initial(self):
        return {'userlevel': self.account.user_level,
                'email': self.account.user.email}

    def form_valid(self, form):
        self.account.user_level = form.cleaned_data['userlevel']
        self.account.save()
        return super(AccountEditView, self).form_valid(form)


class AccountDeleteView(InstitutionAdminToolMixin,
                        ValidationMessageFormMixin,
                        DeleteView):
    """
       Deletes a StarsAccount.
    """
    model = StarsAccount
    success_url_name = 'tool:manage:account-list'
    tab_content_title = 'delete a user'
    template_name = 'tool/manage/account_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super(AccountDeleteView, self).get_context_data(**kwargs)
        try:
            self.account = StarsAccount.objects.get(id=kwargs['object'].id)
        except StarsAccount.DoesNotExist:
            self.account = get_object_or_404(
                PendingAccount, id=kwargs['object'].id)
        context['user_level_description'] = get_user_level_description(
            self.account.user_level)
        context['object'] = kwargs['object']
        return context

    def delete(self, request, *args, **kwargs):

        (preferences, notify_form) = _update_preferences(
            request,
            self.get_institution())
        logger.info("Account: %s deleted." % self.get_object(),
                    extra={'request': request})
        if preferences.notify_users:
            self.get_object().notify(StarsAccount.DELETE_ACCOUNT, request.user,
                                     self.get_institution())
        return super(AccountDeleteView, self).delete(request, *args, **kwargs)


class PendingAccountDeleteView(AccountDeleteView):
    """
        Deletes a PendingAccount.
    """
    model = PendingAccount


class ShareDataView(InstitutionAdminToolMixin,
                    ValidationMessageFormMixin,
                    TemplateView):
    """
        Users can view their snapshots
    """
    tab_content_title = 'share data'
    template_name = 'tool/manage/share_snapshots.html'

    def get_context_data(self, **kwargs):
        context = super(ShareDataView, self).get_context_data(**kwargs)
        institution = self.get_institution()
        context['third_party_sharing_list'] = (
            institution.third_parties.all())
        context['snapshot_list'] = SubmissionSet.objects.get_snapshots(
            institution)
        context['latest_report'] = (
            institution.get_latest_submission())
        return context


class SnapshotPDFExportView(StartExportView,
                            InstitutionAdminToolMixin,
                            ValidationMessageFormMixin,
                            TemplateView):
    """
        Shows the download modal and triggers task
    """
    export_method = build_pdf_export

    def get_url_prefix(self):
        return "%s/pdf/" % self.kwargs['submissionset']

    def get_task_params(self):
        return self.get_institution().submissionset_set.get(
            pk=self.kwargs['submissionset']).id


class SnapshotPDFDownloadView(DownloadExportView,
                              InstitutionAdminToolMixin,
                              ValidationMessageFormMixin,
                              TemplateView):
    """
        Returns the result of the task (hopefully an excel export)
    """
    content_type = 'application/pdf'
    extension = "pdf"

    def get_filename(self):
        return self.get_institution().slug[:64]


class SnapshotCSVExportView(StartExportView,
                            InstitutionAdminToolMixin,
                            ValidationMessageFormMixin,
                            TemplateView):
    """
        Shows the download modal and triggers task
    """
    export_method = build_csv_export

    def get_url_prefix(self):
        return "%s/csv/" % self.kwargs['submissionset']

    def get_task_params(self):
        return self.get_institution().submissionset_set.get(
            pk=self.kwargs['submissionset'])


class SnapshotCSVDownloadView(DownloadExportView,
                              InstitutionAdminToolMixin,
                              ValidationMessageFormMixin,
                              TemplateView):
    """
        Returns the result of the task (hopefully an excel export)
    """
    content_type = "application/octet-stream"
    extension = "zip"

    def get_filename(self):
        return self.get_institution().slug[:64]


class ShareThirdPartiesView(InstitutionAdminToolMixin,
                            ValidationMessageFormMixin,
                            UpdateView):
    """
        Users chose which third parties to share data with
    """
    form_class = ThirdPartiesForm
    model = Institution
    tab_content_title = 'share data'
    template_name = 'tool/manage/share_third_parties.html'

    def get_context_data(self, **kwargs):
        context = super(ShareThirdPartiesView, self).get_context_data(**kwargs)
        context['help_content_name'] = 'edit_account'
        context['third_party_list'] = (ThirdParty.objects
                                       .exclude(name='Sustainable Endowments Institute'))
        context['snapshot_count'] = SubmissionSet.objects.get_snapshots(
            self.get_institution()).count()
        return context

    def get_object(self):
        return self.get_institution()


class MigrateOptionsView(InstitutionAdminToolMixin, TemplateView):
    """
        Provides a user with migration options (i.e., migrate some data or
        migrate a submission).
    """
    tab_content_title = 'manage data'
    template_name = 'tool/manage/migrate_submissionset.html'

    def get_context_data(self, **kwargs):
        context = super(MigrateOptionsView, self).get_context_data(**kwargs)
        context['active_submission'] = (
            self.get_institution().current_submission)
        context['latest_creditset'] = CreditSet.objects.get_latest()
        context['available_submission_list'] = self._get_available_submissions(
            institution=self.get_institution())
        return context

    @classmethod
    def _get_available_submissions(cls, institution):
        submissions = (institution.submissionset_set.filter(status='r') |
                       institution.submissionset_set.filter(status='f'))
        return submissions


class MigrateDataView(InstitutionAdminToolMixin,
                      ValidationMessageFormMixin,
                      UpdateView):
    """
        Provides a form to solicit user's confirmation that this
        data migration should proceed.
    """
    form_class = MigrateSubmissionSetForm
    model = SubmissionSet
    success_url_name = 'tool:tool-summary'
    tab_content_title = 'data migration'
    template_name = 'tool/manage/migrate_data.html'
    valid_message = ("Your migration is in progress. Please allow a "
                     "few minutes before you can access your submission.")
    invalid_message = ("Before the migration can begin, you need to "
                       "confirm your intention by checking that little "
                       "check box down there above the Migrate My Data "
                       "button.")

    def update_logical_rules(self):
        super(MigrateDataView, self).update_logical_rules()
        self.add_logical_rule({'name': 'user_can_migrate_from_submission',
                               'param_callbacks': [
                                   ('user', 'get_request_user'),
                                   ('submission', '_get_old_submission')]})

    def _get_old_submission(self):
        return get_object_or_404(
            self.get_institution().submissionset_set.all(),
            id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(MigrateDataView, self).get_context_data(**kwargs)
        context['active_submission'] = (
            self.get_institution().current_submission)
        context['old_submission'] = self._get_old_submission()
        return context

    def form_valid(self, form):
        # if user hasn't checked the magic box:
        if not form.cleaned_data['is_locked']:
            return self.form_invalid(form)
        try:
            user_id = self.request.user.id
        except:
            user_id = None
        # otherwise, start a migration task
        perform_data_migration.delay(self._get_old_submission().id,
                                     user_id)
        return super(MigrateDataView, self).form_valid(form)


class MigrateVersionView(InstitutionAdminToolMixin,
                         ValidationMessageFormMixin,
                         UpdateView):
    """
        Provides a form to solicit user's confirmation that this
        version migration should proceed.
    """
    form_class = MigrateSubmissionSetForm
    model = SubmissionSet
    success_url_name = 'tool:manage:migrate-options'
    template_name = 'tool/manage/migrate_version.html'
    tab_content_title = 'version upgrade'
    valid_message = ("Your upgrade is in progress. Please allow a "
                     "few minutes before you can access your submission.")
    invalid_message = ("Before the upgrade can begin, you need to "
                       "confirm your intention by checking that little "
                       "check box down there above the Migrate Version "
                       "button.")

    def update_logical_rules(self):
        super(MigrateVersionView, self).update_logical_rules()
        self.add_logical_rule({'name': 'user_can_migrate_version',
                               'param_callbacks': [
                                   ('user', 'get_request_user'),
                                   ('current_inst', 'get_institution')]})

    def get_context_data(self, **kwargs):
        context = super(MigrateVersionView, self).get_context_data(**kwargs)
        current_submission = self.get_institution().current_submission
        context['current_submission'] = current_submission
        context['latest_creditset'] = CreditSet.objects.get_latest()
        return context

    def form_valid(self, form):
        # if user hasn't checked the magic box, do not proceed . . .
        if not form.cleaned_data['is_locked']:
            return self.form_invalid(form)
        # . . . otherwise, start a migration task
        perform_migration.delay(
            old_ss_id=self.get_institution().current_submission.id,
            new_cs_id=CreditSet.objects.get_latest().id,
            user_email=self.request.user.email)
        return super(MigrateVersionView, self).form_valid(form)
