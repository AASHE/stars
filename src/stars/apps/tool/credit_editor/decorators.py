from functools import wraps

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from stars.apps.credits.models import CreditSet

def creditset_is_unlocked(f):
    """
        This decorator tests to see if the creditset is locked - 2nd arg. must be the creditset ID.
    """
    @wraps(f)
    def wrap(request, creditset_id, *args, **kwargs):
        creditset = get_object_or_404(CreditSet, id=creditset_id)
        if creditset.is_locked:
            return HttpResponseRedirect(creditset.get_locked_url())
        else:
            return f(request, creditset_id, *args, **kwargs)            
    return wrap

def creditset_allows_post(f):
    """
        This decorator tests to see if the creditset is locked - 2nd arg. must be the creditset ID.
        Unlike creditset_is_unlocked, this one allows GET requests, just not POST requests
    """
    @wraps(f)
    def wrap(request, creditset_id, *args, **kwargs):
        creditset = get_object_or_404(CreditSet, id=creditset_id)
        if creditset.is_locked and request.method == 'POST':
            return HttpResponseRedirect(creditset.get_locked_url())
        else:
            return f(request, creditset_id, *args, **kwargs)            
    return wrap
