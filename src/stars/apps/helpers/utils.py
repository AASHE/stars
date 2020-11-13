import re

from django.conf import settings
from django.core.cache import cache
from django.utils.html import escape
from django.utils.http import urlquote
from hashlib import md5


def invalidate_template_cache(fragment_name, *variables):
    joined_vars = u':'.join([urlquote(var) for var in variables])
    args = md5(joined_vars)
    cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
    cache.delete(cache_key)


def settings_context(request):
    """
        This custom template-context processor adds some basic settings
        access these variables in the templates with:

        {{ settings_context.analytics_id }}
    """

    context_dict = {}

    settings_list = ['ANALYTICS_ID', 'DEBUG', 'PYTHON_VERSION',
                     'DJANGO_VERSION', 'HG_REVISION', 'GOOGLE_MAPS_API_KEY']

    for s in settings_list:
        context_dict[s.lower()] = None
        if hasattr(settings, s):
            context_dict[s.lower()] = getattr(settings, s)

    return {'settings_context': context_dict}


class StripCookieMiddleware(object):
    """
        Remove Analytics cookies from request before caching middleware
        gets them.
        http://djangosnippets.org/snippets/1772/
        http://code.djangoproject.com/ticket/9249
    """
    strip_re = re.compile(r'(__utm.=.+?(?:; |$))')

    def process_request(self, request):
        try:
            cookie = self.strip_re.sub('', request.META['HTTP_COOKIE'])
            request.META['HTTP_COOKIE'] = cookie
        except:
            pass


def add_required_label_tag(original_function):
    """Adds the 'required' CSS class and an asterisks to required field labels.
    """

    def required_label_tag(self, contents=None, attrs=None):
        contents = contents or escape(self.label)
        if self.field.required:
            if not self.label.endswith(" *"):
                self.label + "* " + self.label
                contents = "* " + contents
            attrs = {'class': 'required'}
        return original_function(self, contents, attrs)
    return required_label_tag


def use_required_label_tag():
    """Decorates BoundField.label_tag with add_required_label_tag()."""
    from django.forms.forms import BoundField
    BoundField.label_tag = add_required_label_tag(BoundField.label_tag)
