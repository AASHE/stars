#!/usr/bin/env python

"""
    Tool to export all content for a specific credit
"""

from stars.apps.institutions.models import *
from stars.apps.submissions.models import *
from stars.apps.credits.models import Credit

from django.utils.encoding import smart_unicode, smart_str

import csv, string

def export_credit_content(credit, ss_qs=None):

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
                "City",
                "State",
                "Country",
                "Org type",
                "FTE-Enrollment",
                "Version",
                "Status",
                "Score",
               ]

    for df in df_list:
        columns.append(df)

    columns.append('Public Notes')

    csvWriter.writerow(columns)

    # Create Rows
    for cus in cus_list:

        ss = cus.subcategory_submission.category_submission.submissionset
        institution = ss.institution
        profile = institution.profile

        row = [
                institution.name,
                ss.date_submitted,
                profile.city,
                profile.state,
                institution.country,
                institution.institution_type,
                institution.fte,
                cus.subcategory_submission.category_submission.submissionset.creditset.version
                ]

        # Status and Score
        if cus.subcategory_submission.category_submission.submissionset.rating.publish_score:
            if cus.submission_status == "na":
                row.append("Not Applicable")
                row.append("Not Applicable")
            elif cus.submission_status == 'np' or cus.submission_status == 'ns':
                row.append("Not Pursuing")
                row.append(0)
            else:
                row.append("Pursuing")
                row.append(cus.assessed_points)
        else:
            row.append("Reporter")
            row.append("Reporter")

        for df in df_list:

            if (cus.submission_status == "na" or
                cus.submission_status == 'np' or
                cus.submission_status == 'ns'):
                row.append("--")
            else:
                field_class = DocumentationFieldSubmission.get_field_class(df)
                try:
                    dfs = field_class.objects.get(credit_submission=cus, documentation_field=df.get_for_creditset(cus.subcategory_submission.category_submission.submissionset.creditset))
                except:
                    row.append('**')
                else:
                    if df.type == 'upload':
                        if dfs.value:
                            row.append("http://stars.aashe.org%s"
                                       % dfs.value.url)
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

credit_id_list = [402, 403, 404, 405, 406, 407]
for cid in credit_id_list:
    credit = Credit.objects.get(pk=cid)
    export_credit_content(credit)
