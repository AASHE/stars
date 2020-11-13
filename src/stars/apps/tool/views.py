from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import ListView, RedirectView, TemplateView
from django.views.generic.edit import UpdateView

from stars.apps.accounts.mixins import StarsAccountMixin
from stars.apps.helpers.old_path_preserver import (OLD_PATHS_TO_PRESERVE,
                                                   new_path_for_old_path)
from stars.apps.institutions.models import Institution, StarsAccount
from stars.apps.tool.forms import SettingsUpdateForm
from stars.apps.tool.mixins import (InstitutionAdminToolMixin,
                                    InstitutionToolMixin)

import logical_rules
import stars.apps.accounts


class SubmissionLockedView(
        logical_rules.mixins.RulesMixin,
        stars.apps.accounts.mixins.StarsAccountMixin,
        TemplateView):

    template_name = 'tool/submissions/submission_locked.html'


class SummaryToolView(InstitutionToolMixin,
                      TemplateView):
    """
        Displays the summary tool page for an institution.
    """
    tab_content_title = 'summary'
    template_name = 'tool/summary.html'

    def update_logical_rules(self):
        super(SummaryToolView, self).update_logical_rules()
        self.add_logical_rule({'name': 'user_has_view_access',
                               'param_callbacks': [
                                   ('user', 'get_request_user'),
                                   ('institution', 'get_institution')]})

    def get_context_data(self, **kwargs):
        context = super(SummaryToolView, self).get_context_data(**kwargs)
        context['rating_list'] = (
            self.get_institution().submissionset_set.filter(
                status='r').filter(is_visible=True).order_by('date_submitted'))
        return context


class ToolLandingPageView(StarsAccountMixin, RedirectView):
    """
        Redirects user based on the number of STARS accounts he's
        associated with.  Probably mis-named; not really a landing page,
        in that no one ever actually lands here.

        Provides a view that can be pointed to by the 'Reporting' link
        in the menu nav and bread crumbs.
    """

    def get_redirect_url(self, **kwargs):
        """
        Redirect based on the number of STARS accounts associated with
        this user.
        """
        stars_accounts = self.get_stars_account_list()

        if stars_accounts.count() is 0:
            return reverse('tool:no-stars-account')
        elif stars_accounts.count() is 1:
            return reverse(
                'tool:tool-summary',
                kwargs={'institution_slug': stars_accounts[0].institution.slug})
        else:
            return reverse('tool:select-institution')


class NoStarsAccountView(TemplateView):
    """
        Explains to a user what it means that he has no STARS account.

        Needed because folks w/AASHE accounts can get to STARS, but
        are not allowed to access to the reporting tool.
    """
    template_name = 'tool/no_stars_account.html'

    def get_context_data(self, **kwargs):
        context = super(NoStarsAccountView, self).get_context_data(**kwargs)
        institution = self.get_institution(user=self.request.user)
        context['institution'] = institution
        context['liaison_name'] = self.get_liaison_name(institution)
        context['liaison_email'] = (institution.contact_email if institution
                                    else None)
        return context

    def get_institution(self, user):
        """
            Returns one institution associated with this user.

            Usually this is the only institution associated with
            this user.  Rarely, more than one institution will be
            associated with a user; when this happens, the first
            institution that's a STARS participant will be returned.
        """
        inst_list = None
        if hasattr(user, 'aasheuser'):
            user_dict = user.aasheuser.get_drupal_user_dict()
            if user_dict:
                inst_list = user_dict.get('profile_instlist', None)
        if not inst_list:
            return None

        institution_ids = inst_list.split(',')
        num_institutions = len(institution_ids)

        # profile_instlist can be empty, so:
        if num_institutions is 0:
            institution = None
        elif num_institutions is 1:
            try:
                institution = Institution.objects.get(id=institution_ids[0])
            except Institution.DoesNotExist:
                institution = None
        else:
            # valid_institution_ids is a list of ids that point to
            # Institutions; keep track of them so that, in the event that
            # none of the institution_ids represent an Institution that's
            # a STARS participant, we don't try to lookup an id that
            # doesn't point to an Institution.
            valid_institution_ids = []
            for institution_id in institution_ids:
                try:
                    institution = Institution.objects.get(id=institution_id)
                    valid_institution_ids.append(institution.id)
                    if institution.is_participant:
                        break
                except Institution.DoesNotExist:
                    next
            else:
                # None are STARS participants? Just return the first one.
                if valid_institution_ids:
                    institution = Institution.objects.get(
                        id=valid_institution_ids[0])
                else:  # lookup failed for all institution_ids
                    institution = None

        return institution

    def get_liaison_name(self, institution):
        if institution:
            full_name = ''
            for name in (institution.contact_first_name,
                         institution.contact_middle_name,
                         institution.contact_last_name):
                if name:
                    full_name += name + ' '
            return full_name.strip()
        else:
            return None


class SelectInstitutionView(StarsAccountMixin, ListView):
    """
    Displays a list of institutions this user has a STARS account for.

    If 'next' in self.request.GET, when the user selects and institution,
    he's redirected to a URL based on self.request.GET['next'].

    When 'next' not in self.request.GET, the user is redirected to the
    tool-summary page for the institution he picks.
    """
    model = StarsAccount
    tab_content_title = 'institutions'
    template_name = 'tool/select_institution.html'

    def get_queryset(self):
        """
        Returns a StarsAccount queryset usually, unless 'next' in
        self.request.GET, in which case a list of StarsAccounts, with
        a url based on self.request.GET['next'] tacked on to each
        StarsAccount, so the template can use that, rather than the
        default, tool-summary page for StarsAccount.institution.
        """
        queryset = self.get_stars_account_list().order_by('institution__name')
        if 'next' not in self.request.GET:
            return queryset
        else:
            # send the 'next_url' into the template
            stars_accounts = list()
            for stars_account in queryset.all():
                stars_account.next_url = self.resolve_url(
                    self.request.GET['next'],
                    stars_account)
                stars_accounts.append(stars_account)
            return stars_accounts

    def resolve_url(self, path, stars_account):
        """
        Runs path through new_path_for_old_path if it's one we
        want to preserve (listed as OLD_PATHS_TO_PRESERVE in
        stars.urls).  If it's not in that list, path is returned
        unmodified -- we're not using that now, but I'm slipping
        it in so if we stick a 'next' GET parameter on a link
        that points to this view, later, and that 'next' is a valid
        URL, it'll just work.
        """
        # path comes with leading slash on a request, but the url
        # patterns don't want a leading slash, so chop it off here
        # before looking for one in the the other.
        rootless_path = path[1:]
        if rootless_path in OLD_PATHS_TO_PRESERVE:
            return new_path_for_old_path(path, stars_account.institution)
        else:
            return path


class SettingsUpdateView(InstitutionAdminToolMixin, UpdateView):

    template_name = "tool/settings.html"
    form_class = SettingsUpdateForm
    model = Institution

    def get_object(self):
        return self.get_institution()

    def form_valid(self, form):
        messages.success(self.request, "Settings saved.")
        return super(SettingsUpdateView, self).form_valid(form)
