from django import template
from stars.apps.old_cms.models import HomepageUpdate

register = template.Library()

@register.inclusion_tag('old_cms/tags/homepage_updates.html')
def show_homepage_updates(count=5):
    """ Gets a list of homepage updates. """
    update_list = HomepageUpdate.objects.all()

    return {'update_list': update_list}
