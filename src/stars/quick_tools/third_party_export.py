#!/usr/bin/env python

"""
    Tool to export all content for a specific credit
"""

from stars.apps.institutions.models import *
from stars.apps.submissions.models import *
from stars.apps.credits.models import Credit
from stars.apps.third_parties.models import ThirdParty

from django.utils.encoding import smart_unicode, smart_str

import csv, string
import datetime


def export_credit_content(credit, ss_qs=None):

    print ss_qs

    filename = 'export/%s.csv' % string.replace("%s" % credit, "/", "-")
    filename = string.replace(filename, ":", "")
    filename = string.replace(filename, " ", "_")
    print filename
    csvWriter = csv.writer(open(filename, 'wb'))

    # Get the list of submissions for columns
    if not ss_qs:
        ss_qs = SubmissionSet.objects.filter(status='r').order_by("institution__name")
    ss_list = []
    cus_list = []
    for ss in ss_qs:
        print ss.id
        ss_list.append(ss)
        cus = CreditUserSubmission.objects.get(credit=credit.get_for_creditset(ss.creditset), subcategory_submission__category_submission__submissionset=ss)
        cus_list.append(cus)

    # Get the list of fields in the credit for rows
    df_list = []
    for df in credit.documentationfield_set.all():
        df_list.append(df)

    # Create Columns

    columns = [
                "Institution",
                "Date Submitted",
                "Last Updated",
                "Liason Email",
#                "City",
#                "State",
#                "Country",
#                "Org type",
#                "FTE-Enrollment",
                "Version",
                "Status",
               ]

    for df in df_list:
        columns.append(df)

    columns.append('Public Notes')

    csvWriter.writerow(columns)

    # Create Rows
    for cus in cus_list:

        institution = cus.get_institution()
        ss = cus.subcategory_submission.category_submission.submissionset

        row = [
                institution.name,
                ss.date_submitted,
                cus.last_updated,
                institution.contact_email,
#                profile.city,
#                profile.state,
#                institution.country,
#                institution.institution_type,
#                institution.fte,
                ss.creditset.version
                ]

        # Status and Score
        if cus.submission_status == "na":
            row.append("Not Applicable")
        elif cus.submission_status == 'np' or cus.submission_status == 'ns':
            row.append("Not Pursuing")
        else:
            row.append("Pursuing")

        for df in df_list:

            if (cus.submission_status == "na" or
                cus.submission_status == 'np' or
                cus.submission_status == 'ns'):
                row.append("--")
            else:
                field_class = DocumentationFieldSubmission.get_field_class(df)
                try:
                    _df = df.get_for_creditset(ss.creditset)
                    dfs = field_class.objects.get(credit_submission=cus,
                                                  documentation_field=_df)
                except:
                    row.append('**')
                else:
                    if df.type == 'upload':
                        if dfs.value:
                            row.append("http://stars.aashe.org%s" %
                                       dfs.value.url)
                        else:
                            row.append("")
                    else:
                        # long text has to be truncated for excel
                        if dfs.documentation_field.type == 'long_text':
                            if dfs.value:
                                str_val = dfs.value.replace("\r\n", "\n")
                                if len(str_val) > 32000:
                                    str_val = ("%s [TRUNCATED]" %
                                               str_val[:32000])
                            else:
                                str_val = ""
                            row.append(smart_str(str_val))

                        else:
                            row.append(smart_str(dfs.value))
        row.append(smart_str(cus.submission_notes))
        csvWriter.writerow(row)

cs = CreditSet.objects.get(pk=5)

tp = ThirdParty.objects.get(slug="sierra")
print "EXPORTING: %s" % tp

deadline = datetime.date(year=2013, month=4, day=15)

# snapshot_list = tp.get_snapshots().exclude(institution__id=447).order_by("institution__name")
# snapshot_list = snapshot_list.filter(date_submitted__gt=deadline)
# snapshot_list = snapshot_list | tp.get_snapshots().filter(id='1528')

latest_snapshot_list = tp.get_snapshots().filter(institution__id=267)

# inst_list = []
# latest_snapshot_list = [] # only use the latest snapshot
# for ss in snapshot_list:
#     if ss.institution.id not in inst_list:
#         inst_list.append(ss.institution.id)
#         i_ss_list = ss.institution.submissionset_set.filter(status='f').order_by('-date_submitted', '-id')
#         print "Available snapshots for %s" % ss.institution
#         for __ss in i_ss_list:
#             print "%s, %d" % (__ss.date_submitted, __ss.id)
#         latest_snapshot_list.append(i_ss_list[0])
#         print "Selected snapshot: %s, %d" % (i_ss_list[0].date_submitted, i_ss_list[0].id)
# print snapshot_list

for cat in cs.category_set.all():
    for sub in cat.subcategory_set.all():
        for c in sub.credit_set.all():
            export_credit_content(c, latest_snapshot_list)
