#!/usr/bin/env python
"""Pre-check report for princeton sharing.

Produces 3 lists:

  - institutions and reports to be shared with princeton.
  - institutions from folks set up to share with princeton
    that don't have a report ready to share.
  - institutions with a report ready to share, but not
    sharing with princeton.

"""
import datetime

from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import SubmissionSet
from stars.apps.third_parties.models import ThirdParty


princeton = ThirdParty.objects.get(slug="princeton")

reports_set_to_go = {}
reports_not_shared = {}
institutions_sharing_with_no_report = []

start_date = datetime.date(year=2016, month=3, day=2)
end_date = datetime.date(year=2019, month=3, day=8)

for cs in [CreditSet.objects.get(version=2.0),
           CreditSet.objects.get(version=2.1)]:

    reports = SubmissionSet.objects.exclude(
        rating__isnull=True).filter(
            creditset=cs).filter(
                    date_submitted__gte=start_date).filter(
                        date_submitted__lte=end_date).order_by(
                            "institution__name", "-date_submitted", "-id")

    # reports to be shared with princeton
    reporting_institutions = []

    for report in reports.filter(
            institution__in=princeton.access_to_institutions.all()):
        # Just take first report for each institution.
        if report.institution in reporting_institutions:
            continue  # Not the first report for this institution.
        reporting_institutions.append(report.institution)
        reports_set_to_go[report.institution] = report

    # reports not shared with princeton
    institutions_not_sharing = []

    for report in reports.exclude(
            institution__in=princeton.access_to_institutions.all()):
        # Just take first report for each institution.
        if report.institution in institutions_not_sharing:
            continue  # Not the first report for this institution.
        institutions_not_sharing.append(report.institution)
        reports_not_shared[report.institution] = report

# institutions set up to share with princeton w/o a report to share
for institution in princeton.access_to_institutions.all():
    for cs in [CreditSet.objects.get(version=2.0),
               CreditSet.objects.get(version=2.1)]:

        reports = SubmissionSet.objects.exclude(
            rating__isnull=True).filter(
                creditset=cs).filter(
                    date_submitted__gte=start_date).filter(
                        date_submitted__lte=end_date).order_by(
                            "institution__name", "-date_submitted", "-id")

        if reports.count() == 0:
            institutions_sharing_with_no_report.append(institution)

print "Reports ready to be shared with Princeton"

for institution, report in reports_set_to_go.items():
    print '\t'.join([institution.name, str(report.date_submitted),
                     report.rating.name, report.creditset.version,
                     institution.contact_email])

print "^LReports ready to be shared but not set up to share with Princeton"

for institution, report in reports_not_shared.items():
    print '\t'.join([institution.name, str(report.date_submitted),
                     report.rating.name, report.creditset.version,
                     institution.contact_email])

print "^LInstitutions set up to share with Princeton w/o report to share"

for institutions in set(institutions_sharing_with_no_report):
    print('\t'.join(institution.name, institution.contact_email))
