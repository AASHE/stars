from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import messages


class TemplateView(object):
    """
        A generic class view that all other views can extend
    """
    def __init__(self, template):
        self.template = template

    def __call__(self, request, *args, **kwargs):
        """ Simply calls render """
        return self.render(request, *args, **kwargs)

    @property
    def __name__(self):
        return self.__class__.__name__

    def render(self, request, *args, **kwargs):
        """ Renders the response """

        return render_to_response(self.template,
                                  self.get_context(request, *args, **kwargs),
                                  context_instance=RequestContext(request))

    def get_context(self, request, *args, **kwargs):
        """ Add/update any context variables """
        _context = {}
        return _context

class FormActionView(object):
    """
        This callable class can be extended to handle any form submission
    """

    def __init__(self, template, formClass, has_upload=False, form_name='form', instance_name=None, init_context=None):
        """ Initializes the class with a formclass and template """
        self.formClass = formClass
        self.template = template
        self.has_upload = has_upload
        self.form_name = form_name
        self.instance_name = 'instance'
        if instance_name:
            self.instance_name = instance_name
        if not init_context:
            self.context_dict = {}
        else:
            self.context_dict = init_context

    @property
    def __name__(self):
        return self.__class__.__name__

    def __call__(self, request, *args, **kwargs):
        """ Call the class as if it were a function """

        return self.render(request, *args, **kwargs)

    def render(self, request, *args, **kwargs):
        """ Where all the work is done """

        context = self.get_context(request, *args, **kwargs)
        response = self.process_form(request, context)

        if response:
            return response

        return render_to_response(self.template, RequestContext(request, context))

    def get_instance(self, request, context, *args, **kwargs):
        """ Provides a way for the class to get the model instance from the request object """
        if context.has_key(self.instance_name):
            return context[self.instance_name]
        elif kwargs.has_key('instance'):
            context[self.instance_name] = kwargs['instance']
        return None

    def get_context(self, request, *args, **kwargs):
        """ Adding any additional context items to the context. Uses ``RequestContext`` """

        _context = {}
        _context.update(self.context_dict)
        _context.update(self.get_extra_context(request, *args, **kwargs))

        instance = self.get_instance(request, _context, *args, **kwargs)

        if instance:
            if self.instance_name:
                _context[self.instance_name] = instance
            else:
                _context['instance'] = instance

        return _context

    def get_extra_context(self, request, *args, **kwargs):
        """ Extend this method to add any additional items to the context """
        return {}

    def process_form(self, request, context):
        """ Returns a response or raises a redirect exception """

        form = self.get_form(request, context)

        if request.method == 'POST':
            if form.is_valid():
                r = self.get_success_action(request, context, form)
                if r:
                    return r
            else:
                messages.error(request, "Please correct the errors below.")

        context[self.form_name] = form
        return None

    def get_form(self, request, context):

        _formClass = self.get_form_class(context)
        kwargs = self.get_form_kwargs(request, context)
        return _formClass(**kwargs)

    def save_form(self, form, request, context):
        """ Saves the form to a instance if available """
        context[self.instance_name] = form.save()

    def get_form_class(self, context, *args, **kwargs):
        """ Here you can perform any changes to the form class """
        return self.formClass

    def get_success_action(self, request, context, form):
        """
            On successful submission of the form, redirect to the returned URL
            Returns None if redirect not necessary
        """

        self.save_form(form, request, context)

        if context[self.instance_name] and hasattr(context[self.instance_name], 'get_absolute_url'):
            return HttpResponseRedirect(context[self.instance_name].get_absolute_url())
        else:
            return None

    def get_form_kwargs(self, request, context):
        """ Get the parameters for the form class """
        kwargs = {}
        if request.method == 'POST':
            kwargs['data'] = request.POST
            if self.has_upload and request.FILES:
                kwargs['files'] = request.FILES
        if context.has_key(self.instance_name):
            kwargs['instance'] = context[self.instance_name]
        return kwargs

class MultiFormView(object):
    """
        A class based view used to process multiple forms on a page

        Extending classes must define a form_class_list property
        form_class_list = [
            {'form_name': 'form_name', 'form_class': FormClass, 'instance_name': 'instance', 'has_upload': False,}
        ]
        ... and a template property (these can both be passed as keyword parameters if necessary
    """

    form_class_list = []

    @property
    def __name__(self):
        return self.__class__.__name__

    def __init__(self, template=None, form_class_list=None, extra_context=None):
        """
            Initializes the view with a template, list of forms and some initial context
            The form_list is a list of dictionaries that can be added to self.form_list
                {'form_name': 'form_name', 'form_class': FormClass, 'instance_name': 'instance', 'has_upload': False,}
            The view will tie a form to an instance by assuming that the instance is in the context
            ... that is context[instance_name]
        """
        if template:
            self.template = template

        if form_class_list:
            self.form_class_list.append(form_class_list)

        if extra_context:
            self.init_context = extra_context
        else:
            self.init_context = {}

    def __call__(self, request, *args, **kwargs):
        """
            Typically just calls render.
            **kwargs will contain the data from the parsed URL
        """

        return self.render(request, *args, **kwargs)

    def render(self, request, *args, **kwargs):
        """
            Render returns the HttpResponse object after getting the context and processing the forms
        """
        context = self.get_context(request, **kwargs)

        context, response = self.process_forms(request, context)
        if response:
            return response

        return render_to_response(self.template, context, context_instance=RequestContext(request))

    def get_context(self, request, **kwargs):
        """
            Returns a context dictionary with self.extra_context applied
        """
        context = {}
        context.update(self.init_context)

        context.update(self.get_extra_context(request, context, **kwargs))

        return context

    def get_extra_context(self, request, context, **kwargs):
        """
            A place where extending classes can update the context given the context so far
        """
        return {}

    def process_forms(self, request, context):
        """
            Calls get_form_list to initialize the forms and then
            processes them all

            Returns an updated context and a response object

            The response is None, or a response object on success
            using `get_success_response`
        """

        form_list, context = self.get_form_list(request, context)

        # Validate Forms
        validated = True
        for form_name, form in form_list.iteritems():
            context[form_name] = form
            if request.method == 'POST':
                if not form.is_valid():
                    validated = False

        # Save Forms
        if request.method == 'POST':
            if validated:
                for form_name, form in form_list.iteritems():
                    form.save()

                context = self.extra_success_action(request, context)
                return context, self.get_success_response(request, context)
            else:
                messages.error(request, "Please correct the errors below.")

        return context, None

    def get_form_list(self, request, context):
        """
            Creates forms for all the form dictionaries in
            self.form_class_list Uses the 'instance_name' to search
            the context for the instance if the instance isn't found
            it assumes that there is no instance for this form (new
            object)

            Returns a form_list and an updated context
        """
        form_list = {}

        for form_class in self.form_class_list:
            klass = form_class['form_class']
            kwargs = self.get_form_kwargs(form_class, request, context,
                                          prefix=form_class['form_name'])
            form_list[form_class['form_name']] = klass(**kwargs)
        return form_list, context

    def extra_success_action(self, request, context):
        """
            An access point for performing an action after a successful form completion
        """
        return context

    def get_success_response(self, request, context):
        """
            On successful submission of the form, redirect to the returned URL
            Returns None if redirect not necessary
        """
        return None

    def get_form_kwargs(self, form_dict, request, context, prefix=None):
        """
            Get the parameters for the form classes. If there was a post request add 'data'
            and if there are file_uploads required, add files.

            form_dict:
            {'form_name': 'form_name', 'form_class': FormClass, 'instance_name': 'instance', 'has_upload': False,}
        """
        kwargs = {}
        if context.has_key(form_dict['instance_name']):
            kwargs['instance'] = context[form_dict['instance_name']]
        if request.method == "POST":
            kwargs['data'] = request.POST
            if form_dict['has_upload']:
                kwargs['files'] = request.FILES
        if prefix:
            kwargs['prefix'] = prefix

        return kwargs
