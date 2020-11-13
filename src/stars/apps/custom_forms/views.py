from django.shortcuts import render
from django.views.generic.edit import FormView

from stars.apps.custom_forms.forms import DataDisplayAccessRequestForm
from stars.apps.helpers.mixins import ValidationMessageFormMixin
from stars.apps.notifications.models import EmailTemplate


class BaseCustomFormView(ValidationMessageFormMixin, FormView):
    """
        Base view for custom forms

        define:
            form_class
            template_name
            success_template_name
            email_template_slug
            form_title
            block_content_slug
    """
    success_template_name = "custom_forms/form_success.html"
    template_name = 'custom_forms/form.html'
    email_template_slug = None
    staff_template_slug = None

    def form_valid(self, form):
        form.save()
        self.send_confirmation_email(form)
        return render(request=self.request,
                      template_name=self.success_template_name,
                      dictionary=self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(BaseCustomFormView,
                        self).get_context_data(**kwargs)
        context['form_title'] = self.form_title
        if self.block_content_slug:
            context['block_content_slug'] = self.block_content_slug
        return context

    def get_confirmation_email_to(self, form):
        """
            Uses the existing user, but fallback to a "email" field in the form
            if the user isn't logged in
        """
        if self.request.user.is_authenticated():
            return self.request.user.email
        if "email" in form.cleaned_data.keys():
            return form.cleaned_data['email']
        return None

    def get_staff_email_to(self):
        return "ben@aashe.org"

    def send_confirmation_email(self, form):
        """
            Send emails to the requesting user and staff
        """
        if self.email_template_slug:
            et = EmailTemplate.objects.get(slug=self.email_template_slug)
            et.send_email([self.get_confirmation_email_to(form)],
                          form.cleaned_data)

        if self.staff_template_slug:
            et = EmailTemplate.objects.get(slug=self.staff_template_slug)
            et.send_email(['ben@aashe.org'], form.cleaned_data)
            # see feature request:
            # https://bitbucket.org/aashe/stars/issue/9/emailtemplatesend_email-should-take-to


class DataDisplaysAccessRequestView(BaseCustomFormView):
    """
        People can request access to the Data Displays
    """
    form_class = DataDisplayAccessRequestForm
    email_template_slug = "dd_application"
    staff_template_slug = "dd_application_staff"
    form_title = 'Request Access to the Data Displays'
    block_content_slug = "dd_app"

    def get_staff_email_to(self):
        return "ben@aashe.org"
