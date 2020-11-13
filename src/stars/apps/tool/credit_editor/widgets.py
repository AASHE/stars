from django.forms.widgets import Textarea
from django.template.loader import get_template

import json


class TabularFieldEdit(Textarea):

    template_name = "tool/credit_editor/widgets/tabular_input_field.html"

    def __init__(self, attrs=None, fields_in_credit=[]):
        super(TabularFieldEdit, self).__init__(attrs)

        self.fields_in_credit = fields_in_credit

    def render(self, name, value, attrs=None):

        template = get_template(self.template_name)
        context_dict = {
            'fields': self.fields_in_credit,
            'name': name,
            'value': json.dumps(value)
        }
        return template.render(context_dict)
