from django.views.generic import TemplateView

from stars.apps.old_cms.models import NewArticle as Article
from stars.apps.tool.mixins import InstitutionToolMixin


class MyResourcesView(InstitutionToolMixin, TemplateView):
    """
        Shows the my resources section of the tool
    """
    template_name = "tool/submissions/my_resources.html"

    def update_logical_rules(self):
        super(MyResourcesView, self).update_logical_rules()
        self.add_logical_rule({'name': 'institution_has_my_resources',
                                'param_callbacks': [
                                    ('institution', 'get_institution')]})

    def get_context_data(self, **kwargs):
        _context = super(MyResourcesView, self).get_context_data(**kwargs)
        _context['node'] = Article.objects.get(pk=83)
        return _context
