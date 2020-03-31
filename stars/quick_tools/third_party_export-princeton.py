#!/usr/bin/env python
import datetime
import string

from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import SubmissionSet
from stars.apps.third_parties.models import ThirdParty
from stars.apps.third_parties.utils import export_credit_csv


tp = ThirdParty.objects.get(slug="princeton")

summaries = {}
institutions = []
institutions_to_exclude = [
    8217,  # AASHE Test Campus
    427,  # University of Missouri, Kansas City
    795,  # University of North Carolina, Wilmington
]

# Reports to force into export, by version
hard_coded_reports = [
    SubmissionSet.objects.get(pk=7315),  # Ball State University
    SubmissionSet.objects.get(pk=6798),  # Baldwin Wallace University
]

# Add the hard coded report institutions to avoid duplicates
for ss in hard_coded_reports:
    institutions.append(ss.institution)

for cs in [
    CreditSet.objects.get(version=2.2),
    CreditSet.objects.get(version=2.1),
    CreditSet.objects.get(version=2.0),
]:

    latest_reports = []  # only use the latest report

    def add_report(r):
        latest_reports.append(r)
        summaries[r.institution] = r

    # add these reports in first
    for ss in hard_coded_reports:
        if ss.creditset.version == cs.version:
            add_report(ss)

    start_date = datetime.date(year=2017, month=3, day=8)
    end_date = datetime.date(year=2020, month=3, day=25)

    reports = (
        SubmissionSet.objects.filter(institution__in=tp.access_to_institutions.all())
        .exclude(rating__isnull=True)
        .filter(creditset=cs)
        .filter(date_submitted__gte=start_date)
        .filter(date_submitted__lte=end_date)
        .order_by("institution__name", "-date_submitted", "-id")
    )

    for report in reports:
        # Just take first report for each institution.
        if (
            report.institution in institutions
            or report.institution.id in institutions_to_exclude
        ):
            continue  # Not the first report for this institution
        add_report(report)
        institutions.append(report.institution)

    for cat in cs.category_set.all():
        for sub in cat.subcategory_set.all():
            for c in sub.credit_set.all():
                filename = "princeton/export/%s/%s.csv" % (
                    cs.version,
                    string.replace("%s" % c, "/", "-"),
                )
                filename = string.replace(filename, ":", "")
                filename = string.replace(filename, " ", "_")

                export_credit_csv(c, ss_qs=latest_reports, outfilename=filename)

for institution, report in summaries.items():
    print(
        "\t".join(
            [
                institution.name,
                str(report.date_submitted),
                report.rating.name,
                report.creditset.version,
                institution.contact_email,
            ]
        )
    )
