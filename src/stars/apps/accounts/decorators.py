from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.http import urlquote


def user_is_staff(f):
    """
        This decorator tests to see if the User has staff privileges
    """
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if request.user.is_staff:
            return f(request, *args, **kwargs)
        elif request.user.is_authenticated():
            raise PermissionDenied("AASHE Staff Only")
        else:
            return _redirect_to_login(request)
    return wrap


def _redirect_to_login(request):
    """ Returns a Redirect Response to the login URL, with a ?next=
    parameter back to the current request path """
    messages.info(request, "Please login to access STARS tools.")
    path = urlquote(request.get_full_path())
    return HttpResponseRedirect('%s?next=%s' %(settings.LOGIN_URL, path))
