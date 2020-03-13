#!/usr/bin/env python

"""
    Tool to export snapshots for Sierra.
"""
import datetime
import os
import string

from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import (CreditUserSubmission,
                                           SubcategorySubmission,
                                           SubmissionSet,
                                           SUBMISSION_STATUSES)
from stars.apps.third_parties.models import ThirdParty
from stars.apps.third_parties.utils import export_credit_csv


START_DATE = datetime.date(year=2017, month=3, day=2)
END_DATE = datetime.date(year=2020, month=3, day=1)


"""
Sierra needs
- summary scores for each category and subcategory
  (presented as points earned over points possible and
  including Innovation & Leadership) and
- all credit-level data from every rated report submitted between
  March 2, 2015 and March 30, 2018
  by institutions who have opted in to have their data shared with Sierra.
- Data from Reporter-level reports should not be included
  nor should data from reports that are still in review and revision mode.
"""


def get_institution_institution_type_from_submission_set(submission_set):

    credit_user_submission = CreditUserSubmission.objects.get(
        credit__identifier="IC-1",
        subcategory_submission__category_submission__submissionset=submission_set)  # noqa

    field = credit_user_submission.get_submission_fields()[0]

    return str(field.value)


sierra = ThirdParty.objects.get(slug="sierra")

summaries = {}


for creditset in [CreditSet.objects.get(version="2.0"),
                  CreditSet.objects.get(version="2.1"),
                  CreditSet.objects.get(version="2.2")]:

    reports = SubmissionSet.objects.filter(
        institution__in=sierra.access_to_institutions.all()).exclude(
            rating__isnull=True).filter(
                creditset=creditset).filter(
                    date_submitted__gte=START_DATE).filter(
                        date_submitted__lte=END_DATE).order_by(
                            "institution__name",
                            "-date_submitted",
                            "-id").filter(
                                status=SUBMISSION_STATUSES["RATED"]).exclude(
                                    institution__name="AASHE Test Campus").exclude(  # noqa
                                        rating__name="Reporter")
    institutions = []
    latest_reports = []  # only use the latest report

    for report in reports:
        # Just take first report for each institution.
        if report.institution in institutions:
            continue  # Not the first report for this institution.

        if creditset.version == "2.0":
            # if this inst has a 2.1 report, don't include the 2.0 one.
            if SubmissionSet.objects.filter(
                institution=report.institution).exclude(
                    rating__isnull=True).filter(
                        creditset=CreditSet.objects.get(version="2.1")).filter(  # noqa
                            date_submitted__gte=START_DATE).filter(
                                date_submitted__lte=END_DATE).filter(
                                    status=SUBMISSION_STATUSES["RATED"]).exclude(  # noqa
                                        institution__name="AASHE Test Campus").exclude(  # noqa
                                            rating__name="Reporter").count():  # noqa
                continue
        latest_reports.append(report)
        institutions.append(report.institution)
        summaries[report.institution] = report

    for cat in creditset.category_set.all():
        for subcategory in cat.subcategory_set.all():
            for credit in subcategory.credit_set.all():
                filename = 'sierra/export/%s/%s.csv' % (
                    creditset.version, string.replace("%s" % credit,
                                                      "/", "-"))
                filename = string.replace(filename, ":", "")
                filename = string.replace(filename, " ", "_")

                export_credit_csv(credit,
                                  ss_qs=latest_reports,
                                  outfilename=filename)

    # export subcategory score sheets
    filename = "%s_subcategory_scores.tsv" % creditset.version
    outfile = open(filename, 'w+')

    subcategory_headers = [
        "Institution Name",
        "Status",
        "Submit Date",
        "STARS version",
        "Overall Score",
        "Rating",
        "Institution Type",
        "Country",
        "Nth Report (includes expired)",
        "# Reports Submitted (includes expired)",
    ]

    # Add the subcategories
    subcategories = []  # stored for later reference
    for category in creditset.category_set.all():
        for subcategory in category.subcategory_set.all():
            subcategories.append(subcategory)
            subcategory_headers.append(
                "%s points claimed" % subcategory.title)
            subcategory_headers.append(
                "%s points available" % subcategory.title)

    print >>outfile, "\t".join(subcategory_headers)

    for report in latest_reports:
        row = []
        row.append(report.institution.name)
        row.append(report.status)
        row.append(unicode(report.date_submitted))
        row.append(report.creditset.version)
        row.append("%f.2" % report.score if report.score else "0.00")
        row.append(report.rating.name)
        row.append(
            get_institution_institution_type_from_submission_set(report))
        row.append(report.institution.country)

        # calculated total reports submitted
        all_reports = report.institution.submissionset_set.filter(
            status=SUBMISSION_STATUSES["RATED"]).exclude(
                rating__name="Reporter").order_by(
                    'date_submitted').values_list(
                        'id', 'date_submitted')
        index = [x[0] for x in all_reports].index(report.id)

        row.append(unicode(index + 1))
        row.append(unicode(len(all_reports)))

        for sub in subcategories:
            subcatsub = SubcategorySubmission.objects.filter(
                subcategory=sub).get(category_submission__submissionset=report)
            row.append(unicode(subcatsub.get_claimed_points()))
            row.append(unicode(subcatsub.get_adjusted_available_points()))

        print >>outfile, u"\t".join(row)

    outfile.close()

print '\t'.join(("Institution", "Date Submitted", "Rating",
                 "Version", "Liaison Email"))

for institution, report in summaries.items():
    print '\t'.join([institution.name, str(report.date_submitted),
                     report.rating.name, report.creditset.version,
                     institution.contact_email])
