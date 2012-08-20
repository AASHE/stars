"""
Helper functions and classes that provide convient helpers
modelled on Django's shortcuts module
"""
import logging

from django.template import loader, Context
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from stars.apps.helpers import exceptions

logger = logging.getLogger('stars')

def render_to_any_response(HttpResponseClass, *args, **kwargs):
    """
    This is a version of Django's shortcut that takes the HttpResponse class
    as an argument, so we can render custom 404 or 500 pages.
    """
    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    return HttpResponseClass(loader.render_to_string(*args, **kwargs), **httpresponse_kwargs)


def get_cmsobject_or_404(klass, *args, **kwargs):
    """
    Uses xml-rpc call to return an object, or raises a Http404 exception if the object
    does not exist.

    klass should be a CMS model (Article, ArticleList, or ArticleMenu). All other
    arguments and keyword arguments are passed through to the constructor.
    """
    try:
        object = klass(*args, **kwargs)
        if (object == None):
            logger.info("Attempt to get %s object (%s, %s) failed" %
                        (klass.__name__, args, kwargs))
            raise ObjectDoesNotExist("Requested resource was not found.")

    except Exception, e:
        logger.exception(e)
        raise Http404(e)

    return object


def render_help_text(help_text, as_tooltip=True):
    """ Use the template tag normally used to render help text in templates to render and return formatted help text """
    from stars.apps.helpers.templatetags.help import show_help_text

    help_template = loader.get_template('helpers/tags/help_text.html')
    return help_template.render(Context(show_help_text(help_text, as_tooltip)))
