from django import template
register = template.Library()


@register.simple_tag()
def get_list_index(l, i):
    try:
        return l[i]
    except:
        return None
