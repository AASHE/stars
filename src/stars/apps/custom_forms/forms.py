from django.forms import ModelForm
from stars.apps.custom_forms.models import DataDisplayAccessRequest


class DataDisplayAccessRequestForm(ModelForm):

    class Meta:
        model = DataDisplayAccessRequest
        exclude = ['date']
