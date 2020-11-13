from django.forms import ModelForm, Form
from django import forms

from extra_views import InlineFormSet

# from captcha.fields import ReCaptchaField

from stars.apps.submissions.models import (SubmissionInquiry,
                                           SubmissionSet,
                                           CreditSubmissionInquiry,
                                           DataCorrectionRequest)


class SubmissionSelectForm(Form):

    institution = forms.ModelChoiceField(
        queryset=SubmissionSet.objects.get_rated().order_by(
            'institution__name'),
        empty_label="Please Select an Institution's Submission")

    def __init__(self, *args, **kwargs):
        super(SubmissionSelectForm, self).__init__(*args, **kwargs)
        self.fields['institution'].widget.attrs['style'] = "width: 600px;"


class SubmissionInquiryForm(ModelForm):

    # captcha = ReCaptchaField(
    #     label='Please verify that you are a living, breathing human being.')

    class Meta:
        model = SubmissionInquiry
        exclude = ['submissionset', 'date']

    def __init__(self, *args, **kwargs):
        super(SubmissionInquiryForm, self).__init__(*args, **kwargs)
        self.fields['anonymous'].widget = forms.CheckboxInput(attrs={
            'onchange': 'toggleFormCollapse(this);'})
        self.fields['anonymous'].required = False
        self.fields['additional_comments'].widget.attrs['style'] = (
            "width: 600px;")


class CreditSubmissionInquiryForm(ModelForm):

    class Meta:
        model = CreditSubmissionInquiry
        exclude = ['submission_inquiry']

    def __init__(self, creditset=None, *args, **kwargs):
        """ Use a specific creditset to populate the choices """

        super(CreditSubmissionInquiryForm, self).__init__(*args, **kwargs)

        self.fields['credit'].choices = creditset.get_pulldown_credit_choices()
        self.fields['credit'].widget.attrs['style'] = "width: 600px;"
        self.fields['explanation'].widget.attrs['style'] = "width: 600px;"


class CreditSubmissionInquiryFormSet(InlineFormSet):
    model = CreditSubmissionInquiry
    extra = 1
    can_delete = False
    form_class = CreditSubmissionInquiryForm

    def get_extra_form_kwargs(self):
        """
        Returns extra keyword arguments to pass to each form in the formset
        """
        return {"creditset": self.view.get_creditset()}


class DataCorrectionRequestForm(ModelForm):

    class Meta:
        model = DataCorrectionRequest
        exclude = ['reporting_field', 'object_id', 'content_type',
                   'user', 'approved']

    def __init__(self, creditset=None, *args, **kwargs):

        super(DataCorrectionRequestForm, self).__init__(*args, **kwargs)

        self.fields['new_value'].label = "New Text:"
