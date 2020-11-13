from logging import getLogger
import re

from django import template
from django.utils.html import strip_spaces_between_tags, escape
from django.utils.safestring import mark_safe
from django.core import urlresolvers


from stars.apps.helpers.models import HelpContext

logger = getLogger('stars')

register = template.Library()


def lookup_help_context(context_name):
    """ Pulls the help text from the DB if it's available """
    try:
        return HelpContext.objects.get(name=context_name)
    except HelpContext.DoesNotExist:
        logger.info("HelpContext, '%s', not found." % context_name)
        return None


@register.inclusion_tag('helpers/tags/help_text.html')
def show_help_context(context_name, as_tooltip=True, icon='icon-question-sign'):
    """ Displays a tool-tip for the help text for the given context. """
    help_context = lookup_help_context(context_name)

    if help_context:
        return {
            # _clean(help_context.help_text, as_tooltip),
            'help_text': re.sub(r'\r\n|\r|\n', ' ', help_context.help_text.replace("\"", "'")),
            'tooltip': as_tooltip,
            'id': context_name,
            'help_text_title': help_context.title,
            'icon': icon
        }
    else:
        return {
            'help_text': None
        }


@register.simple_tag
def get_help_context(context_name):
    """ Simply returns the helptext, unstyled. """
    help_context = lookup_help_context(context_name)

    if not help_context:
        #        return "<a href='%s?key=%s'>Add Help Context</a>" % (urlresolvers.reverse('admin:helpers_helpcontext_add'), context_name)
        return "..."
    return mark_safe(help_context.help_text)


@register.inclusion_tag('helpers/tags/help_text.html')
def show_help_text(help_text, as_tooltip=True, id=None, icon='icon-question-sign'):
    """ Displays a tool-tip for the given help text with quotes properly escaped. """
    return {'help_text': re.sub(r'\r\n|\r|\n', ' ', help_text.replace("\"", "'")),
            "tooltip": as_tooltip,
            "id": id,
            'icon': icon}


def _clean(text, as_tooltip):
    """ Helper to prepare the help text """
    if not text:
        return None
    js_encoded = strip_spaces_between_tags(text.strip())
    if as_tooltip:
        js_encoded = escape(js_encoded)
        js_encoded = re.sub(r'\r\n|\r|\n', '', js_encoded)
        js_encoded = re.sub(r'\"', "'", js_encoded)
        js_encoded = js_encoded.replace('&quot;', '\&quot;').replace(
            "&amp;", '\&amp;').replace("&#39;", '\&#39;')
    return mark_safe(js_encoded)
