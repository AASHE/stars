from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView
from django.utils.html import mark_safe

from stars.apps.helpers.forms.views import MultiFormView
from stars.apps.credits.views import CreditNavMixin
from stars.apps.credits.models import CreditSet
from stars.apps.accounts.mixins import IsStaffMixin
from stars.apps.tool.credit_editor.forms import *


def home(request):
    """
        Forwards the user to the latest version.
    """
    # simply forward the visitor to the latest version
    latest_version = CreditSet.objects.order_by('-release_date')[0]
    return HttpResponseRedirect(latest_version.get_edit_url())


class CreditEditorNavMixin(CreditNavMixin):

    def get_category_url(self, category, url_prefix=None):
        """ The default link for a category. """
        return category.get_edit_url()

    def get_subcategory_url(self, subcategory, url_prefix=None):
        """ The default link for a category. """
        return subcategory.get_edit_url()

    def get_credit_url(self, credit, url_prefix=None):
        """ The default credit link. """
        return credit.get_edit_url()


class CreditEditorFormView(IsStaffMixin, MultiFormView, CreditEditorNavMixin):
    """
        The base class for all Credit Editor Views
        It inherits from MultiFormView, but mixes in IsStaffMixin and
        CreditNavMixin
    """

    @property
    def __name__(self):
        return self.__class__.__name__

    def get_extra_context(self, request, context, **kwargs):
        """ Expects arguments for
            /creditset_id/category_id/subcategory_id/credit_id """

        context = super(CreditEditorFormView,
                        self).get_extra_context(request, context, **kwargs)

        if kwargs.has_key('creditset_id'):
            context['creditset'] = get_object_or_404(
                CreditSet,
                pk=kwargs['creditset_id'])

            keys = ['category', 'subcategory', 'credit']

            values = self.get_creditset_selection(request,
                                                  context['creditset'],
                                                  **kwargs)

            context.update(dict(zip(keys, values)))

            # Add the selected field to the context
            if kwargs.has_key('field_id'):
                context['field'] = get_object_or_404(
                    DocumentationField,
                    pk=kwargs['field_id'],
                    credit=context['credit'])
                context['current'] = context['field']

            context['current'] = context['creditset']
            for key in reversed(keys):
                if context[key] is not None:
                    context['current'] = context[key]
                    break

            context['outline'] = self.get_creditset_navigation(
                context['creditset'],
                current=context['current'])

        context['available_sets'] = CreditSet.objects.all()

        return context

    def get_success_response(self, request, context):
        """
            Overriding to use the get_edit_url() method
            The only reason to use this is to ensure that the ordering form
            reloads
        """
        if context.has_key('current'):
            return HttpResponseRedirect(context['current'].get_edit_url())
        else:
            return None

    def generate_form_set(self, request, modelClass, modelFormClass, queryset,
                          prefix='object-ordering'):
        """
            Returns a formSet for ordering child items
        """

        if queryset.count() > 0:
            ObjectFormSet = modelformset_factory(modelClass,
                                                 form=modelFormClass,
                                                 extra=0)
            kwargs = {'queryset': queryset, 'prefix': prefix}

            if request.method == 'POST':
                kwargs['data'] = request.POST

            return ObjectFormSet(**kwargs)
        else:
            return None


class CreditReorderMixin(object):
    """
        Overrides extra_success_action to reorder the credits in the category
        after a successful save
    """

    def extra_success_action(self, request, context):

        context['category'].update_ordering()
        return context


class AddObject(CreditEditorFormView):
    """
        A basic form processor for a single form
    """

    def get_success_response(self, request, context):
        """
            Take to the parent after adding or to the latest
        """
        if context.has_key('current'):
            return HttpResponseRedirect(context['current'].get_edit_url())
        else:
            latest_version = CreditSet.objects.get_latest()
            return HttpResponseRedirect(latest_version.get_edit_url())

    def add_form_from_request(self, formKlass, instance, request):
        """
            A helper function to create a form and apply the POST if necessary
        """
        kwargs = {'instance': instance}
        if request.method == "POST":
            kwargs['data'] = request.POST

        form = formKlass(**kwargs)
        return form


class DeleteObject(CreditEditorFormView):
    """
        A basic confirmation for for deleting the current field
    """

    def get_success_response(self, request, context):
        pass


class AddCreditset(AddObject):
    """
        A view for editing a specific creditset
    """

    template = 'tool/credit_editor/add_creditset.html'
    form_class_list = [
        {'form_name': 'object_form',
         'form_class': NewCreditSetForm,
         'instance_name': None,
         'has_upload': False}
    ]


class CreditsetDetail(CreditEditorFormView):
    """
        A view for editing a specific creditset
    """

    template = 'tool/credit_editor/creditset_detail.html'
    form_class_list = [
        {'form_name': 'object_form',
         'form_class': CreditSetForm,
         'instance_name': 'creditset',
         'has_upload': False}
    ]

    def get_form_list(self, request, context):
        """
            Extends the form list to include a formset of Categories to order
        """
        form_list, _context = super(CreditsetDetail,
                                    self).get_form_list(request, context)

        # Create the Category forms to order the categories
        creditset = context['creditset']
        form_list['object_ordering'] = self.generate_form_set(
            request,
            Category,
            CategoryOrderForm,
            creditset.category_set.all())

        # Add a new category form to the context
        _context['new_category_form'] = CategoryForm()
        _context['show_delete_button'] = True

        return form_list, _context


class AddCategory(AddObject):
    """
        A view for editing a specific category
    """
    template = 'tool/credit_editor/add_category.html'
    form_class_list = []

    def get_form_list(self, request, context):
        """
            Adds some init data to the form.
        """
        form_list, _context = super(AddCategory,
                                    self).get_form_list(request, context)
        form = self.add_form_from_request(
            CategoryForm,
            Category(creditset=_context['creditset']),
            request)

        form_list['object_form'] = form

        return form_list, _context


class CategoryDetail(CreditEditorFormView):
    """
        A view for editing a specific category
    """

    template = 'tool/credit_editor/category_detail.html'
    form_class_list = [
        {'form_name': 'object_form',
         'form_class': CategoryForm,
         'instance_name': 'category',
         'has_upload': False}
    ]

    def get_form_list(self, request, context):
        """
            Extends the form list to include a formset of Categories to order
        """
        form_list, _context = super(CategoryDetail,
                                    self).get_form_list(request, context)

        # Create the Category forms to order the categories
        category = context['category']
        form_list.update({'object_ordering': self.generate_form_set(
            request,
            Subcategory,
            SubcategoryOrderForm,
            category.subcategory_set.all())})

        # Add a new category form to the context
        _context['new_subcategory_form'] = NewSubcategoryForm()
        _context['show_delete_button'] = True

        return form_list, _context


class AddSubcategory(AddObject):
    """
        A view for adding a specific subcategory
    """
    template = 'tool/credit_editor/add_category.html'
    form_class_list = []

    def get_form_list(self, request, context):
        """
            Adds some init data to the form.
        """
        form_list, _context = super(AddSubcategory,
                                    self).get_form_list(request, context)
        form = self.add_form_from_request(
            NewSubcategoryForm,
            Subcategory(category=_context['category']),
            request)

        form_list['object_form'] = form

        return form_list, _context


class SubcategoryDetail(CreditReorderMixin, CreditEditorFormView):
    """
        A view for editing a specific subcategory
    """

    template = 'tool/credit_editor/subcategory_detail.html'
    form_class_list = [
        {'form_name': 'object_form',
         'form_class': SubcategoryForm,
         'instance_name': 'subcategory',
         'has_upload': False}
    ]

    def get_form_list(self, request, context):
        """
            Extends the form list to include a formset of Categories to order
        """
        form_list, _context = super(SubcategoryDetail,
                                    self).get_form_list(request, context)

        # Create the forms to order the credits
        subcategory = context['subcategory']
        if subcategory.credit_set.filter(type='t1').count() > 0:
            form_list['t1_ordering'] = self.generate_form_set(
                request,
                Credit,
                CreditOrderForm,
                subcategory.credit_set.filter(type='t1'),
                prefix='t1_ordering')

        if subcategory.credit_set.filter(type='t2').count() > 0:
            form_list['t2_ordering'] = self.generate_form_set(
                request,
                Credit,
                CreditOrderForm,
                subcategory.credit_set.filter(type='t2'),
                prefix='t2_ordering')

        _context['show_delete_button'] = True

        return form_list, _context


class AddT1Credit(CreditReorderMixin, AddObject):
    """
        A view for adding a T1 Credit
    """
    template = 'tool/credit_editor/add_credit.html'
    form_class_list = []

    def get_form_list(self, request, context):
        """
            Adds some init data to the form.
        """
        form_list, _context = super(AddT1Credit,
                                    self).get_form_list(request, context)
        instance = Credit(subcategory=_context['subcategory'], type='t1')
        form = self.add_form_from_request(NewCreditForm, instance, request)

        form_list['object_form'] = form

        return form_list, _context


class AddT2Credit(CreditReorderMixin, AddObject):
    """
        Add a T2 credit
        @Todo: More duplication here than I'd like
    """
    template = 'tool/credit_editor/add_t2_credit.html'
    form_class_list = []

    def get_form_list(self, request, context):
        """
            Adds some init data to the form.
        """
        form_list, _context = super(AddT2Credit,
                                    self).get_form_list(request, context)
        instance = Credit(subcategory=_context['subcategory'], type='t2')
        form = self.add_form_from_request(NewT2CreditForm, instance, request)

        form_list['object_form'] = form

        return form_list, _context


class CreditDetail(CreditReorderMixin, CreditEditorFormView):
    """
        A view for editing a specific credit
    """

    template = 'tool/credit_editor/credits/detail.html'
    form_class_list = [
        {'form_name': 'object_form',
         'form_class': CreditForm,
         'instance_name': 'credit',
         'has_upload': False}
    ]


class CreditReportingFields(CreditEditorFormView):
    """
        Editing the reporting tools for a specific credit
    """

    template = 'tool/credit_editor/credits/fields.html'
    form_class_list = []

    def get_form_list(self, request, context):
        """
            Extends the form list to include a formset DocumentationFields
        """
        form_list, _context = super(CreditReportingFields,
                                    self).get_form_list(request, context)

        # Create the DocumentationField forms
        credit = context['credit']

        form_list.update({'object_ordering': self.generate_form_set(
            request,
            DocumentationField,
            DocumentationFieldOrderingForm,
            credit.get_nested_documentation_fields())})

        # Add a new category form to the context
        _context['new_field_form'] = NewDocumentationFieldForm(
            instance=DocumentationField(credit=_context['credit']))
        _context['show_edit_button'] = True
        _context['show_delete_button'] = True

        return form_list, _context

    def get_success_response(self, request, context):
        return HttpResponseRedirect("%sfields/" %
                                    context['credit'].get_edit_url())


class AddReportingField(AddObject):
    """
        A view for adding a new Reporting Field
    """
    template = 'tool/credit_editor/credits/add_field.html'
    form_class_list = []

    def get_form_list(self, request, context):
        """
            Adds some init data to the form.
        """
        form_list, _context = super(AddReportingField,
                                    self).get_form_list(request, context)
        form = self.add_form_from_request(
            NewDocumentationFieldForm,
            DocumentationField(credit=_context['credit']),
            request)

        form_list['object_form'] = form

        return form_list, _context

    def get_success_response(self, request, context):
        return HttpResponseRedirect("%sfields/" %
                                    context['credit'].get_edit_url())


class EditReportingField(CreditEditorFormView):
    """
        A view for editing a specific reporting field
    """

    template = 'tool/credit_editor/credits/field_detail.html'
    form_class_list = [
        {'form_name': 'object_form',
         'form_class': DocumentationFieldForm,
         'instance_name': 'field',
         'has_upload': False}
    ]

    def get_success_response(self, request, context):
        return HttpResponseRedirect("%sfields/" %
                                    context['field'].credit.get_edit_url())


class ApplicabilityReasons(CreditEditorFormView):
    """
        A view for editing a specific Credit's Applicablity Reasons
    """

    template = 'tool/credit_editor/credits/applicability.html'
    form_class_list = []

    def get_form_list(self, request, context):
        """
            Extends the form list to include a formset of Applicability
            Reasons
        """
        form_list, _context = super(ApplicabilityReasons,
                                    self).get_form_list(request, context)

        # Create the Category forms to order the categories
        credit = context['credit']
        form_list.update({'object_ordering': self.generate_form_set(
            request,
            ApplicabilityReason,
            ApplicabilityReasonOrderingForm,
            credit.applicabilityreason_set.all())})

        # Add a new category form to the context
        _context['new_reason_form'] = ApplicabilityReasonForm()

        return form_list, _context

    def get_success_response(self, request, context):
        return HttpResponseRedirect("%sapplicability/" %
                                    context['credit'].get_edit_url())

    def get_extra_context(self, *args, **kwargs):
        _context = super(ApplicabilityReasons, self).get_extra_context(
            *args, **kwargs)
        _context['show_delete_button'] = True
        return _context


class AddApplicabilityReason(AddObject):
    """
        A view for adding a new Applicability Reason
    """
    template = 'tool/credit_editor/credits/add_reason.html'
    form_class_list = []

    def get_form_list(self, request, context):
        """
            Adds some init data to the form.
        """
        form_list, _context = super(AddApplicabilityReason,
                                    self).get_form_list(request, context)
        form = self.add_form_from_request(
            ApplicabilityReasonForm,
            ApplicabilityReason(credit=_context['credit'], ordinal=-1),
            request)

        form_list['object_form'] = form

        return form_list, _context

    def get_success_response(self, request, context):
        return HttpResponseRedirect("%sapplicability/" %
                                    context['credit'].get_edit_url())


class EditApplicabilityReason(CreditEditorFormView):
    """
        A view for editing a specific applicability reason
    """

    template = 'tool/credit_editor/credits/applicability_detail.html'
    form_class_list = [
        {'form_name': 'object_form',
         'form_class': ApplicabilityReasonForm,
         'instance_name': 'applicability_reason',
         'has_upload': False}
    ]

    def get_extra_context(self, request, context, **kwargs):
        """ Expects arguments for
            /creditset_id/category_id/subcategory_id/credit_id """

        _context = super(EditApplicabilityReason,
                         self).get_extra_context(request, context, **kwargs)

        _context['applicability_reason'] = get_object_or_404(
            ApplicabilityReason,
            pk=kwargs['reason_id'])

        return _context

    def get_success_response(self, request, context):
        return HttpResponseRedirect("%sapplicability/" %
                                    context['credit'].get_edit_url())


class DeleteApplicabilityReason(DeleteView, IsStaffMixin):

    model = ApplicabilityReason
    success_url_name = 'tool:credit_editor:applicability-reason-list'
    tab_content_title = 'delete an applicability reason'
    template_name = ('tool/credit_editor/'
                     'applicability_reason_confirm_delete.html')

    def get_success_url(self):
        credit = self.object.credit
        return reverse(
            self.success_url_name,
            kwargs={'creditset_id': credit.get_creditset().id,
                    'category_id': credit.subcategory.category.id,
                    'subcategory_id': credit.subcategory.id,
                    'credit_id': credit.id})


class FormulaAndValidation(CreditEditorFormView):
    """
        A view for editing a Credit's Scoring Formula and add custom
        Validation
    """

    template = 'tool/credit_editor/credits/formula.html'
    form_class_list = [
        {'form_name': 'object_form',
         'form_class': CreditFormulaForm,
         'instance_name': 'credit',
         'has_upload': False}
    ]

    def get_extra_context(self, request, context, **kwargs):

        _context = super(FormulaAndValidation,
                         self).get_extra_context(request, context, **kwargs)
        _context['show_delete_button'] = True
        _context['test_case_list'] = CreditTestSubmission.objects.filter(
            credit=_context['credit'])
        debug_list = []
        for case in _context['test_case_list']:
            __msg_count, __messages, debugging = case.run_test()
            debug_list.append(mark_safe(debugging))
        _context['debug_list'] = debug_list

        return _context

    def extra_success_action(self, request, context):
        """
            Re-run the test cases after the form is processed
        """

        context['test_case_list'] = CreditTestSubmission.objects.filter(
            credit=context['credit'])
        for case in context['test_case_list']:
            case.run_test()

        return context

    def get_form_list(self, request, context):
        """
            Adds some init data to the form.
        """
        form_list, _context = super(FormulaAndValidation,
                                    self).get_form_list(request, context)

        cts = CreditTestSubmission(credit=_context['credit'])
        _context['new_test_case_form'] = CreditTestSubmissionForm(
            instance=cts)

        return form_list, _context

    def get_success_response(self, request, context):
        return None  # will return to self.


class AddTestCase(AddObject):
    """
        A view for adding a new Test Case
    """
    template = 'tool/credit_editor/credits/add_test_case.html'
    form_class_list = []

    def get_form_list(self, request, context):
        """
            Adds some init data to the form.
        """
        form_list, _context = super(AddTestCase,
                                    self).get_form_list(request, context)
        form = self.add_form_from_request(
            CreditTestSubmissionForm,
            CreditTestSubmission(credit=_context['credit']),
            request)

        form_list['object_form'] = form

        return form_list, _context

    def get_success_response(self, request, context):
        return HttpResponseRedirect("%sformula/" %
                                    context['credit'].get_edit_url())


class EditTestCase(CreditEditorFormView):
    """
        A view for editing a specific reporting field
    """

    template = 'tool/credit_editor/credits/add_test_case.html'
    form_class_list = [
        {'form_name': 'object_form',
         'form_class': CreditTestSubmissionForm,
         'instance_name': 'test_case',
         'has_upload': False}
    ]

    def get_extra_context(self, request, context, **kwargs):
        """ Expects arguments for
            /creditset_id/category_id/subcategory_id/credit_id """

        _context = super(EditTestCase,
                         self).get_extra_context(request, context, **kwargs)

        _context['test_case'] = get_object_or_404(CreditTestSubmission,
                                                  pk=kwargs['test_id'])

        return _context

    def get_success_response(self, request, context):
        return HttpResponseRedirect("%sformula/" %
                                    context['credit'].get_edit_url())


class DeleteTestCase(DeleteView, CreditNavMixin, IsStaffMixin):
    model = CreditTestSubmission

    @property
    def credit(self):
        return get_object_or_404(Credit,
                                 pk=self.kwargs['credit_id'])

    def get_success_url(self):
        return self.credit.get_formula_url()

    def get_context_data(self, **kwargs):
        context = super(DeleteTestCase, self).get_context_data(**kwargs)
        context['credit'] = self.credit
        return context
