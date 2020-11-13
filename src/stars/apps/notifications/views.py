from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404

from stars.apps.notifications.models import EmailTemplate


class PreviewEmailTemplate(TemplateView):
    """
        Preview an Email Template
    """

    template_name = "notifications/preview.html"

    def get_context_data(self, **kwargs):
        context = super(PreviewEmailTemplate, self).get_context_data(**kwargs)
        et = get_object_or_404(EmailTemplate, slug=self.kwargs['slug'])
        context['message'] = et.get_message()
        context['title'] = et.title
        context['params'] = kwargs

        return context
