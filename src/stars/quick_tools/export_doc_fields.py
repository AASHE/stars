#!/usr/bin/env python

"""
    Tool to export all credits from a particular CreditSet
"""

from stars.apps.institutions.models import *
from stars.apps.credits.models import CreditSet
from stars.tests.html2text import html2text

import csv

csvWriter = csv.writer(open('documentation_field_list.csv', 'wb'))

columns = [
            "CreditSet Version",
            "Category Title",
            "Subcategory Title",
            "Credit #",
            "Credit Title",
            "Documentation Field",
            "Field Type",
            "Required?"
           ]

csvWriter.writerow(columns)  

cs = CreditSet.objects.get(pk=2)
for cat in cs.category_set.all():
    for sub in cat.subcategory_set.all():
        for c in sub.credit_set.all():
            for df in c.documentationfield_set.all():
                row = [
                        "\"%s\"" % cs.version,
                        cat.title,
                        sub.title,
                        c.get_identifier(),
                        c.title,
                        df.title,
                        df.type,
                        df.required,
                ]
                csvWriter.writerow(row)
