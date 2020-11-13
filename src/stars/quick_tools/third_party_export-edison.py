#!/usr/bin/env python

"""
    Tool to export credits for Edison Energy.
"""
import os
import string

from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import Institution
from stars.apps.third_parties.utils import export_credit_csv


limit_inst_ids = [
    # if this has ids, then only these institutions will be exported
]

credit_sets = [CreditSet.objects.get(version=2.0),
               CreditSet.objects.get(version=2.1)]


for cs in credit_sets:

    export_these = []

    for institution in Institution.objects.all().order_by("name"):
        submissions = institution.get_submissions().filter(
            creditset=cs)
        if submissions:
            submission = submissions[0]
            print "Available snapshots for %s:" % submission.institution
            print [(i.date_submitted, i) for i in
                   institution.get_submissions()]
            print "Selected:", submission.date_submitted
            export_these.append(submission)

    for cat in cs.category_set.all():
        for sub in cat.subcategory_set.all():
            for credit in sub.credit_set.all():
                filename = 'edison/export/%s/%s.csv' % (
                    cs.version, string.replace("%s" % credit, "/", "-"))
                filename = string.replace(filename, ":", "")
                filename = string.replace(filename, " ", "_")

                export_credit_csv(credit,
                                  ss_qs=export_these,
                                  outfilename=filename)
