from django.forms import ModelForm, ValidationError

from stars.apps.helpers.forms.forms import LocalizedModelFormMixin
from stars.apps.institutions.models import SubscriptionPayment


class PaymentForm(LocalizedModelFormMixin, ModelForm):
    """
        This form allows STARS admins to edit or create a payment
        record for a given subscription

        - an instance with valid subscription->institution must be
          specified when form is created.
    """
    class Meta:
        model = SubscriptionPayment
        exclude = ('subscription',)

    def __init__(self, *args, **kwargs):
        """
            Accepts the current user, to be sure that it's
            included in the pull-down list
        """
        current_user = kwargs.pop('current_user', None)
        super(PaymentForm, self).__init__(*args, **kwargs)
        institution = self.instance.subscription.institution
        self.fields['user'].choices = (
            [('', '----------')] +
            [(account.user.id, account.user.email) for account
             in institution.starsaccount_set.all()])

        # ensure the original payee is in the list
        if self.instance and self.instance.user_id:
            self._add_user(self.instance.user)

        # also ensure that the current user is in the list
        self._add_user(current_user)

    def _add_user(self, user):
        """ Add the user to the list of users available as payees """
        # Only add the user if they are not already there...
        for uid, __ in self.fields['user'].choices:
            if uid == user.id:
                return
        # assert:  user is not yet listed in the choices.
        self.fields['user'].choices.append((user.id, user.email))

    def clean_amount(self):
        """
            Confirm that if this is a new payment then the amount is not
            more than the amount due
        """
        amount = self.cleaned_data['amount']

        if (not hasattr(self.instance, 'id') and
            amount > self.instance.subscription.amount_due):
            raise ValidationError("This amount is more than is due: $%s" %
                                  self.instance.subscription.amount_due)

        return amount
