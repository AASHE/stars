from django.forms import ModelForm, RadioSelect

from stars.apps.submissions.models import (CreditUserSubmission,
                                           CREDIT_SUBMISSION_STATUS_CHOICES)


class CreditSubmissionStatusUpdateForm(ModelForm):

    class Meta:
        model = CreditUserSubmission
        fields = ['submission_status']
        widgets = {'submission_status':
                   RadioSelect(choices=CREDIT_SUBMISSION_STATUS_CHOICES)}
