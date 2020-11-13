from django.core.management.base import BaseCommand

from stars.apps.credits.models import DocumentationField


class Command(BaseCommand):

    help = ('One-time script to save formulas of calculated fields.')

    def handle(self, *args, **kwargs):
        """
            One-time script to save formulas of calculated fields.
            This should only be required after a new creditset is created.
        """
        calculated_fields = DocumentationField.objects.filter(
            type='calculated')
        for d in calculated_fields:
            if d.get_creditset().version == '2.2':
                d.update_formula_terms()
                d.recalculate_dependent_submissions()
