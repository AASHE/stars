from logging import getLogger

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.http import urlquote

from stars.apps.institutions.models import StarsAccount


logger = getLogger('stars.request')


class StarsAccountMixin(object):
    """
        Login Required
        Adds STARS account list to class
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(StarsAccountMixin, self).dispatch(*args, **kwargs)

    def get_stars_account_list(self):
        """ get all STARS Accounts associated with this user """
        return StarsAccount.objects.filter(user=self.request.user)


class StarsMixin(object):
    """
        The base mixin class that provides `redirect_to_login` for
        now... maybe others
    """

    def redirect_to_login(self, request):
        """ Returns a Redirect Response to the login URL, with a
        ?next= parameter back to the current request path """
        messages.info(request, "Please login to access STARS tools.")
        path = urlquote(request.get_full_path())
        return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, path))


class IsStaffMixin(StarsMixin):
    """
        This class should be used as a mixin to provide the subclass with staff-only access.

        If the user is not authenticated `__call__` will return a permission denied response.

        Assumes `__call__` returns a response object and has the following declaration:
            def __call__(self, request, *args, **kwargs):
    """

    def __call__(self, request, *args, **kwargs):

        # Unauthenticated users are redirected to Login
        if not request.user.is_authenticated():
            return self.redirect_to_login(request)

        # Unauthorized users get a PermissionDenied response
        if not request.user.is_staff:
            raise PermissionDenied(
                "You do not have permission to access this page.")

        return super(IsStaffMixin, self).__call__(request, *args, **kwargs)
