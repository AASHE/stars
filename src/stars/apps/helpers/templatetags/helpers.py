from django import template
from django.template.defaultfilters import stringfilter

"""
    Helper tags and filters.
"""

register = template.Library()

@register.filter
@stringfilter
def split(value, token):
    """ Split the string value using a double colon, ::, (see Python split) and return the i'th token or '' if no such """
    list = value.split('::')
    if len(list) > token:
        return list[token]
    else:
        return ''

@register.filter
def truncchar(value, arg):
    """ 
        truncate string after a certain number of characters (arg)
        Example usage: {{ string|truncchar:20 }}
    """
    if len(value) < arg:
        return value
    else:
        return value[:arg] + '...'
