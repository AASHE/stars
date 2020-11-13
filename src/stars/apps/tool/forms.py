import django.forms

from stars.apps.helpers.forms.forms import LocalizedModelFormMixin
from stars.apps.institutions.models import Institution


class SettingsUpdateForm(LocalizedModelFormMixin):
    """
        A Form to update Settings.

        For now, there's only one setting, prefers_metric_system, stored
        on Institution.
    """
    prefers_metric_system = django.forms.BooleanField(
        label=("Use metric system. When checked, the Reporting Tool treats "
               "measured amounts as metric quantities. This is a system-"
               "wide setting; changing it effects all users. If others are "
               "using the Reporting Tool now, they should log out before "
               "you change this setting. You should be the only one "
               "logged into STARS when you change this."),
        required=False)

    class Meta:
        model = Institution
        fields = ['prefers_metric_system']
