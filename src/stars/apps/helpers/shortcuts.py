"""
Helper functions and classes that provide convient helpers
modelled on Django's shortcuts module
"""
from logging import getLogger

from django.template.loader import get_template, render_to_string

logger = getLogger('stars')


def render_to_any_response(HttpResponseClass, *args, **kwargs):
    """
    This is a version of Django's shortcut that takes the HttpResponse class
    as an argument, so we can render custom 404 or 500 pages.
    """
    httpresponse_kwargs = {'content_type': kwargs.pop('content_type', None)}
    return HttpResponseClass(render_to_string(*args, **kwargs),
                             **httpresponse_kwargs)


def render_help_text(help_text, as_tooltip=True):
    """ Use the template tag normally used to render help text in
    templates to render and return formatted help text """
    from stars.apps.helpers.templatetags.help import show_help_text

    template = get_template('helpers/tags/help_text.html')
    return help_template.render(show_help_text(help_text, as_tooltip))
