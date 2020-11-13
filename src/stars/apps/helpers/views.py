import collections

from django.http import HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.defaults import page_not_found

from stars.apps.helpers.shortcuts import render_to_any_response
from stars.apps.institutions.models import Institution


def server_error(request):
    """Before watchdog moved to a farm upstate where he can run and
    play and chase rabbits all day, the context below was filled with
    info from any exception available via WatchdogEntry.  Not much
    going on here anymore.
    """
    context = dict()

    return render_to_any_response(HttpResponseServerError,
                                  "500.html",
                                  context,
                                  context_instance=RequestContext(request))


def get_institution_from_path(path):
    """
    Returns the institution specified by the slug in a URL path.
    """
    institution = None
    for part in path.split('/'):
        # Assuming slugs always have dashes in them:
        if '-' in part:
            try:
                institution = Institution.objects.get(slug=part)
            except Institution.DoesNotExist:
                continue
            else:
                break
    return institution


def permission_denied(request):
    """
    Pops the institution derived from the slug in the forbidden URL,
    if there is one, into the template context for 403.html.  Also
    deduces and formats the liaison contact info for that institution,
    then pushes that into the template context, too.
    """

    institution_in_url = get_institution_from_path(request.path)

    # Only show liaison contact info if user has a StarsAccount for this
    # institution:
    liaison_contact_info = ''
    if (request.user.is_authenticated() and
        request.user.starsaccount_set.filter(
            institution=institution_in_url)):
        liaison_email = institution_in_url.get_liaison_email()
        if liaison_email:
            liaison_contact_info = '{liaison_name} is available'.format(
                liaison_name=institution_in_url.get_liaison_name())
            liaison_contact_info += ' via email at {liaison_email}.'.format(
                liaison_email=liaison_email)

    context = {'institution_in_url': institution_in_url,
               'liaison_contact_info': liaison_contact_info}

    return render_to_any_response(HttpResponseForbidden,
                                  "403.html",
                                  context,
                                  context_instance=RequestContext(request))
