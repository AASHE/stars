"""
    This is an adaption of the form wizard
    library from django
"""

from formtools.wizard.views import SessionWizardView


class RevalidationFailure(Exception):

    def __init__(self, message, form_key, form_obj, **kwargs):

        Exception.__init__(self, message)
        self.form_key = form_key
        self.form_obj = form_obj
        self.kwargs = kwargs


class BetterWizardView(SessionWizardView):

    def post(self, *args, **kwargs):

        try:
            return super(BetterWizardView, self).post(self, *args, **kwargs)
        except RevalidationFailure, e:
            return self.render_revalidation_failure(e.form_key, e.form_obj, **e.kwargs)

    def render_done(self, form, **kwargs):
        """
        This method gets called when all forms passed. The method should also
        re-validate all steps to prevent manipulation. If any form don't
        validate, `render_revalidation_failure` should get called.
        If everything is fine call `done`.
        """
        final_form_list = []
        # walk through the form list and try to validate the data again.
        for form_key in self.get_form_list():
            form_obj = self.get_form(step=form_key,
                                     data=self.storage.get_step_data(form_key),
                                     files=self.storage.get_step_files(form_key))
            if not form_obj.is_valid():
                raise RevalidationFailure(
                    "revalidate", form_key, form_obj, **kwargs)
#                return self.render_revalidation_failure(form_key, form_obj, **kwargs)
            final_form_list.append(form_obj)

        # render the done view and reset the wizard before returning the
        # response. This is needed to prevent from rendering done with the
        # same data twice.
        done_response = self.done(final_form_list, **kwargs)
        self.storage.reset()
        return done_response
