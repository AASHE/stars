from django import forms
from django.forms import widgets
from django.forms import ModelForm
from django.contrib.localflavor.us.forms import USStateField
from django.forms.util import ErrorList

import re

from stars.apps.institutions.models import *

class RegistrationSchoolChoiceForm(ModelForm):
    """
        A form for selecting an institution form institutionnames
    """
     
    class Meta:
        model = Institution
        fields = ['aashe_id']

    def __init__(self, *args, **kwargs):
        super(RegistrationSchoolChoiceForm, self).__init__(*args, **kwargs)
        self.fields['aashe_id'].label = "Institution"

class RegistrationForm(ModelForm):
    """
        Contact Information Form
    """
    #terms_of_service = forms.BooleanField(label="I agree to the terms of service", required=True)
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['contact_first_name'].label = "First Name"
        self.fields['contact_middle_name'].label = "Middle Name"
        self.fields['contact_last_name'].label = "Last Name"
        self.fields['contact_title'].label = "Title"
        self.fields['contact_department'].label = "Department/Office"
        self.fields['contact_phone'].label = "Phone"
        self.fields['contact_email'].label = "Email"
        self.fields['executive_contact_first_name'].label = "First Name"
        self.fields['executive_contact_middle_name'].label = "Middle Name"
        self.fields['executive_contact_last_name'].label = "Last Name"
        self.fields['executive_contact_title'].label = "Title"
        self.fields['executive_contact_department'].label = "Department/Office"
        self.fields['executive_contact_email'].label = "Email"
    
    class Meta:
        model = Institution
        exclude = ['name', 'enabled', 'aashe_id']
        
    def clean(self):
        cleaned_data = self.cleaned_data
        
        # confirm that the contact email and the executive email are not the same
        if cleaned_data.has_key("contact_email") and cleaned_data.has_key("executive_contact_email"):
            contact = cleaned_data.get("contact_email")
            executive = cleaned_data.get("executive_contact_email")

            if contact == executive:
                msg = u"Oops, you've entered the same information for both the primary and executive contact. Please make sure these contacts are two different individuals at your institution."
                self._errors["executive_contact_email"] = ErrorList([msg])

                # The executive field is no longer valid
                del cleaned_data["executive_contact_email"]

        return cleaned_data
        
class PayLaterForm(forms.Form):
    
    confirm = forms.BooleanField(label="Please bill me and I will pay later.", required=False)
        
class PaymentForm(forms.Form):
    """
        Credit Card Payment form
    """
    #name_on_card = forms.CharField(max_length=64)
    card_number = forms.CharField(max_length=17)
    exp_month = forms.CharField(max_length=2, initial='mm')
    exp_year = forms.CharField(max_length=4, initial='yyyy')
    cv_code = forms.CharField(max_length=3, label='CV Code', help_text='This is the 3-digit code on the back of your card')
    billing_address = forms.CharField(max_length=128)
    billing_address_line_2 = forms.CharField(max_length=128, required=False)
    billing_city = forms.CharField(max_length=32)
    billing_state = USStateField()
    billing_zipcode = forms.CharField(max_length=6, label='Billing ZIP code')
    
    def clean_exp_month(self):
        data = self.cleaned_data['exp_month']
        error_text = "Please enter a number between 1 and 12"
        
        if not self.is_numeric(data):
            raise forms.ValidationError(error_text)
        month = int(data)
        if month > 12 or month < 0:
            raise forms.ValidationError(error_text)
            
        return data

    def clean_exp_year(self):
        data = self.cleaned_data['exp_year']
        error_text = "Please enter a valid year"
        
        if not self.is_numeric(data):
            raise forms.ValidationError(error_text)

        return data

    def clean_billing_zipcode(self):
        data = self.cleaned_data['billing_zipcode']
        error_text = "Please enter a valid zip code"

        if not self.is_numeric(data):
            raise forms.ValidationError(error_text)

        return data
        
    def is_numeric(self, data):
        """ Helper function to indicate if data is numeric. """
        try:
            month = int(data)
        except:
            return False
        return True
    