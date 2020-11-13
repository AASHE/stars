import sys

from django.forms import ModelForm
from django import forms
from django.forms import widgets

from codemirror.widgets import CodeMirrorTextarea

from stars.apps.credits.models import (CreditSet,
                                       Category,
                                       Subcategory,
                                       Credit,
                                       DocumentationField,
                                       ApplicabilityReason,
                                       Rating,
                                       compile_formula,
                                       Choice,
                                       Unit)
from stars.apps.credits.widgets import (CategorySelectTree,
                                        SubcategorySelectTree,
                                        CreditSelectTree,
                                        DocumentationFieldSelectTree)
from stars.apps.submissions.models import CreditTestSubmission
from stars.apps.tool.my_submission.forms import CreditSubmissionForm
from widgets import TabularFieldEdit

from datetime import date


class RightSizeInputModelForm(ModelForm):
    """A ModelForm upon which every TextInput and Textarea widget
    is sized according to its max_length.

    Asks Bootstrap to do the right-sizing by adding 'input-{size}'
    to the class attribute of the widgets.
    """
    WIDGETS_TO_RIGHTSIZE = [widgets.TextInput,
                            widgets.Textarea]

    # Bootstrap input size classes
    WIDGET_SIZES = {(0, 6): 'input-mini',
                    (7, 9): 'input-small',
                    (10, 13): 'input-medium',
                    (14, 19): 'input-large',
                    (20, 24): 'input-xlarge',
                    (25, sys.maxint): 'input-xxlarge'}

    DEFAULT_WIDGET_SIZES = {widgets.TextInput: 'input-xlarge',
                            widgets.Textarea: 'input-xxlarge'}

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.rightsize_widgets()

    def rightsize_widgets(self):
        """Adjusts the size of all widgets in WIDGETS_TO_RIGHTSIZE.
        """
        for field in self.fields.values():
            if any([isinstance(field.widget, widget_to_rightsize)
                    for widget_to_rightsize in self.WIDGETS_TO_RIGHTSIZE]):
                self.rightsize(field)

    def rightsize(self, field):
        """Adjust the size of `field`.widget."""
        size = self.get_right_size(field)
        field.widget.attrs['class'] = (field.widget.attrs.get('class', '') +
                                       ' ' +
                                       size).strip()

    def get_right_size(self, field):
        """Returns the Bootstrap input class name appropriate for `field`."""
        if getattr(field, 'max_length', None):
            for range_, class_name in self.WIDGET_SIZES.items():
                if range_[0] <= field.max_length <= range_[1]:
                    return class_name
        else:
            return self.get_default_size(field)

    def get_default_size(self, field):
        """Returns the default size for field.widget."""
        for widget in self.DEFAULT_WIDGET_SIZES:
            if isinstance(field.widget, widget):
                return self.DEFAULT_WIDGET_SIZES[widget]


class CreditSetForm(RightSizeInputModelForm):
    release_date = forms.DateField(widget=widgets.SelectDateWidget())

    class Meta:
        model = CreditSet
        exclude = ('scoring_method', 'tier_2_points')

    def __init__(self, *args, **kwargs):
        super(CreditSetForm, self).__init__(*args, **kwargs)

        # opt for the last 10 years and next 2
        year = date.today().year
        widget = widgets.SelectDateWidget(years=range(year-15, year+2))
        self.fields['release_date'].widget = widget


class NewCreditSetForm(CreditSetForm):
    class Meta:
        model = CreditSet
        fields = '__all__'


class CreditSetScoringForm(RightSizeInputModelForm):
    class Meta:
        model = CreditSet
        # exactly the fields excluded on CreditSetForm:
        fields = ('scoring_method', 'tier_2_points')


class CreditSetRatingForm(RightSizeInputModelForm):
    minimal_score = forms.IntegerField(min_value=0, max_value=100)

    class Meta:
        model = Rating
        exclude = ('creditset', 'previous_version')


class CategoryForm(RightSizeInputModelForm):
    class Meta:
        model = Category
        exclude = ('creditset', 'ordinal', 'max_point_value')

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'size': 50})
        self.fields['previous_version'].widget = CategorySelectTree()


class CategoryOrderForm(RightSizeInputModelForm):

    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'class': 'ordinal'}))
    id = forms.IntegerField(widget=widgets.HiddenInput())

    class Meta:
        model = Category
        fields = ('ordinal', 'id')


class SubcategoryForm(RightSizeInputModelForm):

    class Meta:
        model = Subcategory
        exclude = ('ordinal', 'max_point_value')

    def __init__(self, *args, **kwargs):
        """ Only allow categories from the same creditset """
        super(SubcategoryForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = [
            (cat.id, cat.title) for cat in
            self.instance.category.creditset.category_set.all()
        ]
        self.fields['title'].widget.attrs.update({'size': 50})
        self.fields['previous_version'].widget = SubcategorySelectTree()


class NewSubcategoryForm(RightSizeInputModelForm):

    class Meta:
        model = Subcategory
        exclude = ('ordinal', 'max_point_value', 'category',
                   'previous_version')


class SubcategoryOrderForm(RightSizeInputModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'class': 'ordinal'}))

    class Meta:
        model = Subcategory
        fields = ('ordinal',)


class CreditForm(RightSizeInputModelForm):
    title = forms.CharField(widget=widgets.TextInput(attrs={'size': '32'}))

    class Meta:
        model = Credit
        exclude = ('ordinal', 'formula', 'validation_rules', 'number',
                   'type', 'identifier', 'point_value_formula')

    def __init__(self, *args, **kwargs):
        super(CreditForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'size': 50})
        self.fields['previous_version'].widget = CreditSelectTree()

        cs = self.instance.subcategory.category.creditset
        self.fields['subcategory'].queryset = Subcategory.objects.filter(
            category__creditset=cs)


class T2CreditForm(RightSizeInputModelForm):

    class Meta:
        model = Credit
        exclude = ('ordinal', 'formula', 'validation_rules', 'number',
                   'type', 'point_value', 'scoring', 'measurement',
                   'previous_version')

    def __init__(self, *args, **kwargs):
        super(T2CreditForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'size': 50})


class NewCreditForm(CreditForm):

    class Meta(CreditForm.Meta):
        exclude = ('subcategory', 'ordinal', 'formula', 'number',
                   'validation_rules', 'type', 'previous_version',
                   'identifier')

    def __init__(self, *args, **kwargs):
        super(CreditForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'size': 50})


class NewT2CreditForm(NewCreditForm):

    class Meta(NewCreditForm.Meta):
        exclude = ('subcategory', 'ordinal', 'formula', 'validation_rules',
                   'number', 'type', 'point_value', 'scoring', 'measurement',
                   'previous_version', 'identifier')


class AbstractFormWithFormula(object):

    class Meta:
        abstract = True

    def clean_formula(self):
        return self._clean_code_field('formula')

    def clean_validation_rules(self):
        return self._clean_code_field('validation_rules')

    def clean_point_value_formula(self):
        return self._clean_code_field('point_value_formula')

    def _clean_code_field(self, key):
        code = self.cleaned_data[key]
        # remove any funky (Mac and MS) newlines and replace tabs with spaces
        code = code.replace("\r\n", "\n")
        code = code.replace("\t", "    ")
        (success, message) = compile_formula(code, key)
        if not success:
            raise forms.ValidationError(message)
        return code


class CreditFormulaForm(AbstractFormWithFormula,
                        RightSizeInputModelForm):
    formula = forms.CharField(
        widget=CodeMirrorTextarea(mode='python',
                                  config={'lineNumbers': True},),
        required=False,
        help_text=('Must set <em>points</em><br/>AVAILABLE_POINTS '
                   'has a value if this varies'))
    validation_rules = forms.CharField(
        widget=CodeMirrorTextarea(mode='python',
                                  config={'lineNumbers': True},),
        required=False)
    point_value_formula = forms.CharField(
        widget=CodeMirrorTextarea(mode='python',
                                  config={'lineNumbers': True},),
        required=False,
        help_text=('Must set <em>available_points</em><br/>MIN_POINTS '
                   'and MAX_POINTS variables are available if this varies'))

    class Meta:
        model = Credit
        fields = ('formula', 'validation_rules', 'point_value_formula')


class CreditTestSubmissionForm(CreditSubmissionForm):

    class Meta:
        model = CreditTestSubmission
        fields = ['expected_value']


class CreditOrderForm(RightSizeInputModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'class': 'ordinal'}))

    class Meta:
        model = Credit
        fields = ('ordinal',)


class DocumentationFieldForm(AbstractFormWithFormula,
                             RightSizeInputModelForm):
    header = forms.CharField(
        widget=widgets.Textarea(attrs={'rows': '2'}),
        required=False)
    formula = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'noMCE'}),
        required=False,
        help_text='Must set <em>value</em>')
    tooltip_help_text = forms.CharField(
        widget=widgets.Textarea(attrs={'rows': '2'}),
        required=False)
    inline_help_text = forms.CharField(
        widget=widgets.Textarea(attrs={'rows': '4'}),
        required=False)

    class Meta:
        model = DocumentationField
        exclude = ('formula_terms',
                   'identifier',
                   'imperial_formula_text',
                   'last_choice_is_other',
                   'metric_formula_text',
                   'ordinal',
                   'type')

    def __init__(self, *args, **kwargs):
        super(DocumentationFieldForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs["size"] = 60

        cs = self.instance.credit.get_creditset()
        self.fields['credit'].choices = cs.get_pulldown_credit_choices()
        fields = self.instance.credit.documentationfield_set.exclude(
            type='tabular')
        self.fields['tabular_fields'].widget = TabularFieldEdit(
            fields_in_credit=fields)
        self.fields['previous_version'].widget = DocumentationFieldSelectTree()
        self.fields['copy_from_field'].widget = DocumentationFieldSelectTree(
            attrs={'ordinal': 1})

    def clean(self):
        cleaned_data = self.cleaned_data

        # detect if we are moving between credits
        if (self.instance.credit and
                self.instance.credit != cleaned_data['credit']):

            self.instance.identifier = None
            self.instance.ordinal = -1

        # @todo: validate that choice-type fields actually specify choices

        return cleaned_data


class NewDocumentationFieldForm(DocumentationFieldForm):
    class Meta(DocumentationFieldForm.Meta):
        exclude = ('formula_terms',
                   'identifier',
                   'imperial_formula_text',
                   'last_choice_is_other',
                   'max_range',
                   'metric_formula_text',
                   'min_range',
                   'ordinal')


class DocumentationFieldOrderingForm(RightSizeInputModelForm):
    ordinal = forms.FloatField(widget=widgets.HiddenInput(
        attrs={'size': '3', 'class': 'ordinal'}))
    value = forms.CharField()

    class Meta:
        model = DocumentationField
        fields = ('ordinal',)

    DEFAULT_WIDGET_SIZES = {widgets.TextInput: 'input-xxlarge',
                            widgets.Textarea: 'input-xxlarge'}

    def __init__(self, *args, **kwargs):
        super(DocumentationFieldOrderingForm, self).__init__(*args, **kwargs)

        self.fields['value'].widget.attrs['disabled'] = 'disabled'
        self.fields['value'].widget.attrs['class'] = (
            self.fields['value'].widget.attrs.get('class', '') +
            ' noMCE').strip()
        self.fields['value'].required = False
        if self.instance.type == 'choice':
            self.fields['value'].widget.choices = (
                (r.id, r.choice) for r in self.instance.choice_set.all()
            )


class ChoiceForm(RightSizeInputModelForm):
    class Meta:
        model = Choice
        fields = ('choice',)


class ChoiceOrderingForm(RightSizeInputModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'size': '3', 'class': 'ordinal'}))

    class Meta:
        model = Choice
        fields = ('ordinal', 'choice')


class ApplicabilityReasonForm(RightSizeInputModelForm):

    class Meta:
        model = ApplicabilityReason
        exclude = ('credit', 'ordinal', 'previous_version')

    def __init__(self, *args, **kwargs):
        super(ApplicabilityReasonForm, self).__init__(*args, **kwargs)
        self.fields['reason'].widget.attrs['class'] = 'input-xxlarge'


class ApplicabilityReasonOrderingForm(RightSizeInputModelForm):
    ordinal = forms.IntegerField(widget=widgets.HiddenInput(
        attrs={'size': '3', 'class': 'ordinal'}))

    class Meta:
        model = ApplicabilityReason
        fields = ('ordinal',)


class UnitForm(RightSizeInputModelForm):
    """
        When adding a new Credit Field Unit
    """
    class Meta:
        model = Unit
        fields = '__all__'
