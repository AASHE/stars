from django.core.management.base import BaseCommand

from stars.apps.credits.models import DocumentationField


class Command(BaseCommand):

    help = ('One-time script to set the ordinal value of tabular field children.')

    def handle(self, *args, **kwargs):
        """
            One-time script to set the ordinal value of tabular field children.
        """
        tabular_doc_fields = DocumentationField.objects.filter(type='tabular')
        i = 0
        for field in tabular_doc_fields:
            field.reorder_tabular_children()
            print i
            i += 1
