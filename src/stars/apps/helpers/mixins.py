from django.contrib import messages


# @todo - Should this be based on FormView rather than object?

class ValidationMessageFormMixin(object):
    """
        A custom mixin to add a message upon form validation.
    """
    valid_message = "Changes saved."
    invalid_message = "Please correct the errors below."

    def get_valid_message(self):
        return self.valid_message

    def get_invalid_message(self):
        return self.invalid_message

    def form_valid(self, form):
        messages.success(self.request, self.get_valid_message())
        return super(ValidationMessageFormMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, self.get_invalid_message())
        return super(ValidationMessageFormMixin, self).form_invalid(form)
