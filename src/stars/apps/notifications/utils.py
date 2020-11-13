from django.template import Template, Context
from django.utils.safestring import mark_safe


def build_message(content, context):
    """
        A simple method to build a message from
        `content` - a string template
        `context` - the context to be applied to the template
    """
    t = Template("{%% autoescape off %%}%s{%% endautoescape %%}" % content)
    c = Context(context)
    return t.render(c)
