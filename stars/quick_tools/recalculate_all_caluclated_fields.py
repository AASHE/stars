import datetime

from stars.apps.credits.models import DocumentationField


query = DocumentationField.objects.exclude(
    formula=None).exclude(
        formula='').filter(
            credit__subcategory__category__creditset__version="2.1")

total = query.count()

count = 1

for docfield in DocumentationField.objects.exclude(
        formula=None).exclude(
            formula='').filter(
                credit__subcategory__category__creditset__version="2.1"):

    print(
        "{timestamp}: recaluculating dependent submissions of docfield {count} of {total}".format(
            timestamp=datetime.datetime.now().isoformat(),
            count=count, total=total))

    docfield.recalculate_dependent_submissions()
