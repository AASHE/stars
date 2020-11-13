from datetime import date
from logging import getLogger
from logical_rules.mixins import RulesMixin
from django_celery_downloader.views import StartExportView, DownloadExportView

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.db.models import Min
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, ListView, TemplateView

from stars.apps.accounts.utils import respond
from stars.apps.accounts.decorators import user_is_staff
from stars.apps.institutions.models import (Institution,
                                            SubscriptionPayment,
                                            Subscription)
from stars.apps.institutions.views import SortableTableView
from stars.apps.submissions.models import SubmissionSet
from stars.apps.tool.staff_tool.forms import PaymentForm
from stars.apps.tool.mixins import InstitutionToolMixin
from stars.apps.third_parties.models import ThirdParty
from stars.apps.tasks.notifications import add_months

from tasks import build_accrual_report_csv

logger = getLogger('stars.request')


@user_is_staff
def institutions_search(request):
    """
        Provides a search page for Institutions
    """
    return respond(request, 'tool/admin/institutions/institution_search.html',
                   {})


@user_is_staff
def select_institution(request, id):
    """
        The admin tool for selecting a particular institution
    """
    institution = Institution.objects.get(id=id)
    if not institution:
        raise Http404("No such institution.")
    redirect_url = request.GET.get('redirect',
                                   reverse('tool:tool-summary',
                                           args=(institution.slug,)))
    return HttpResponseRedirect(redirect_url)


class ReportMixin(RulesMixin):

    def update_logical_rules(self):
        super(ReportMixin, self).update_logical_rules()
        self.add_logical_rule({
            'name': 'user_is_staff',
            'param_callbacks': [('user', 'get_request_user')],
        })


class InstitutionList(ReportMixin, SortableTableView):
    """
        A quick report on registration for Jillian
        Institution Name
        Reg date
        Renewal Date
        Submission date
    """
    template_name = "tool/admin/institutions/institution_list.html"

    @method_decorator(user_is_staff)
    def render(self, request, *args, **kwargs):
        return super(InstitutionList, self).render(request, *args, **kwargs)

    default_key = 'name'
    default_rev = '-'
    secondary_order_field = 'name'
    columns = [
        {
            'key': 'name',
            'sort_field': 'name',
            'title': 'Institution',
        },
        {
            'key': 'rating',
            'sort_field': 'current_rating',
            'title': 'Rating',
        },
        {
            'key': 'version',
            'sort_field': 'current_submission__creditset__version',
            'title': 'Version',
        },
        {
            'key': 'participation',
            'sort_field': 'is_participant',
            'title': 'Access Level',
        },
        {
            'key': 'contact_email',
            'sort_field': 'contact_email',
            'title': 'Liaison',
        },
        {
            'key': 'submission',
            'sort_field': 'rated_submission__date_submitted',
            'title': 'Submission Date',
        },
        # {
        #     'key':'subscription',
        #     'sort_field':'current_subscription__start_date',
        #     'title':'Subscription',
        # },
    ]

    def get_queryset(self):
        return (Institution.objects
                .annotate(reg_date=Min('subscription__start_date'))
                .select_related(
                    'current_rating',
                    'current_submission',
                    'current_submission__creditset__version'
                )
                )
