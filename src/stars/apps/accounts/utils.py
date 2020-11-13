from logging import getLogger
import MySQLdb
import re

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext


logger = getLogger('stars')

def respond(request, template, context):
    """
        This utility function adds data to the context before sending
        it to the template. The addition is defined by
        TEMPLATE_CONTEXT_PROCESSORS in the settings and calls the
        function below.
    """
    return render_to_response(template,
                              context,
                              context_instance=RequestContext(request))

def account_context(request):
    """
        This is a custom template-context processor that adds the current user.
    """

    context = {'user': request.user,}
    return context

def tracking_context(request):
    """
        This custom template-context processor adds settings.ANALYTICS_ID
    """
    if settings.ANALYTICS_ID:
        return {'analytics_id': settings.ANALYTICS_ID,}

    return {'analytics_id': None,}
