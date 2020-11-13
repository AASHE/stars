#!/usr/bin/env python

from stars.apps.institutions.models import *
from stars.apps.credits.models import CreditSet
from stars.tests.html2text import html2text

import csv

csvWriter = csv.writer(open('credit_list.csv', 'wb'))

"""
>>> import csv
>>> spamWriter = csv.writer(open('eggs.csv', 'wb'), delimiter=' ',
...                         quotechar='|', quoting=csv.QUOTE_MINIMAL)
>>> spamWriter.writerow(['Spam'] * 5 + ['Baked Beans'])
>>> spamWriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])
"""

columns = [
            "CreditSet ID",
            "CreditSet Version",
            "Category ID",
            "Category Title",
            "Subcategory ID",
            "Subcategory Title",
            "Credit ID",
            "Credit #",
            "Credit Title",
            "Available Points",
            "Criteria",
            "Scoring",
            "Applicability",
            "Measurement",
            "Link to STARS Reporting Tool"
           ]

csvWriter.writerow(columns)  

cs = CreditSet.objects.get(pk=2)
for cat in cs.category_set.all():
    for sub in cat.subcategory_set.all():
        for c in sub.credit_set.all():
            if c.measurement:
                m = "\"%s\"" % c.measurement
            else:
                m = ""
            row = [
                    cs.id,
                    "\"%s\"" % cs.version,
                    cat.id,
                    cat.title,
                    sub.id,
                    sub.title,
                    c.id,
                    c.get_identifier(),
                    c.title,
                    c.point_value,
                    "\"%s\"" % c.criteria,
                    "\"%s\"" % c.scoring,
                    "\"%s\"" % c.applicability,
                    m,
                    "http://stars.aashe.org%s" % c.get_submit_url()
            ]
            csvWriter.writerow(row)
