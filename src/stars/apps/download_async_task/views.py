from django.views.generic import TemplateView
from django.http import HttpResponse

from celery.result import AsyncResult


class StartExportView(TemplateView):
    """
        Triggers the task for creating an excel export and provides
        a waiting page that polls for completion
        requires self.export_method
    """
    template_name = "download_async_task/modal_export.html"
    url_prefix = ""

    def get_url_prefix(self):
        return self.url_prefix

    def get_task_params(self):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        _c = super(StartExportView, self).get_context_data(**kwargs)
        _c['url_prefix'] = self.get_url_prefix()
        _c['task'] = self.export_method.delay(self.get_task_params())
        return _c


class DownloadExportView(TemplateView):
    """
        Extend and define content_type and extension

        The generic View class doesn't have a get method, so this is it.
    """

    def get_filename(self):
        raise NotImplementedError

    def render_to_response(self, context, **response_kwargs):
        """ Renders the excel file as a response """

        task_id = self.kwargs['task']
        result = AsyncResult(task_id)
        f = open(result.result, 'r')
        response = HttpResponse(f, content_type=self.content_type)
        response['Content-Disposition'] = ('attachment; filename=%s.%s' %
                                           (self.get_filename(),
                                            self.extension))
        return response
