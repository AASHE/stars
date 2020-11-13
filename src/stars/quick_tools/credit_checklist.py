#!/usr/bin/env python

from stars.apps.credits.models import CreditSet

import csv

csvWriter = csv.writer(open('field_list.csv', 'wb'))

columns = [
    "Version",
    "Category",
    "Subcategory",
    "Credit",
    "Field"
    ]

csvWriter.writerow(columns)

cs = CreditSet.objects.get(pk=5)
for cat in cs.category_set.all():
    for sub in cat.subcategory_set.all():
        for credit in sub.credit_set.all():
            for f in credit.documentationfield_set.all():
                row = [cs.version, cat, sub, credit.identifier, f.title]
                csvWriter.writerow(row)
