#!/usr/bin/env python

"""
    Tool to export all rated reports for AASHE
"""
import csv
import datetime
import string


from stars.apps.institutions.models import *
from stars.apps.submissions.models import *
from stars.apps.credits.models import Credit
from stars.apps.third_parties.utils import export_credit_csv


# - 2.0: IC 1, IC 2, IC 3, OP 18, OP 19, OP 20, and OP 21
# - 2.1: IC 1, IC 2, IC 3, OP 15, OP 16, OP 17, and OP 18

cs_id_list = {
    6: ['IC-1', 'IC-2', 'IC-3', 'OP-18', 'OP-19', 'OP-20', 'OP-21'],
    7: ['IC-1', 'IC-2', 'IC-3', 'OP-15', 'OP-16', 'OP-17', 'OP-18'],
}

for cs_id, limit_to_credit_ids in cs_id_list.items():

    cs = CreditSet.objects.get(pk=cs_id)

    ss_list = SubmissionSet.objects.filter(status='r')
    ss_list = ss_list.order_by("institution__name")
    ss_list = ss_list.filter(creditset=cs)

    # inst_list = []
    # latest_snapshot_list = [] # only use the latest snapshot
    # for ss in snapshot_list:
    #     if ss.institution.id not in inst_list:
    #         inst_list.append(ss.institution.id)
    #         i_ss_list = ss.institution.submissionset_set.filter(status='f').order_by('-date_submitted', '-id').filter(date_submitted__lte=deadline)
    #         print "Available snapshots for %s" % ss.institution
    #         for __ss in i_ss_list:
    #             print "%s, %d" % (__ss.date_submitted, __ss.id)
    #         if i_ss_list[0].creditset == cs:
    #             latest_snapshot_list.append(i_ss_list[0])
    #         else:
    #             print "newer snapshot in version: %s" % i_ss_list[0].creditset
    #         print "Selected snapshot: %s, %d" % (i_ss_list[0].date_submitted, i_ss_list[0].id)
    #
    # print "%d Snapshots" % len(latest_snapshot_list)

    for cat in cs.category_set.all():
        for sub in cat.subcategory_set.all():
            for c in sub.credit_set.all():
                if not limit_to_credit_ids or c.identifier in limit_to_credit_ids:
                    filename = 'export/%s/%s.csv' % (cs.version, string.replace("%s" % c, "/", "-"))
                    filename = string.replace(filename, ":", "")
                    filename = string.replace(filename, " ", "_")

                    export_credit_csv(c, ss_qs=ss_list, outfilename=filename)
