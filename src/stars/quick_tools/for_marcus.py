"""Custom export for Marcus Welker at BU.  Marcus uncovered a bug in the
institutions API that I've been unable to fix.  I offered a custom export
to him, useful until the API bug is fixed.

"""
import csv
import datetime

from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import SubmissionSet


START_DATE = datetime.date(year=2015, month=5, day=9)
END_DATE = datetime.date(year=2018, month=5, day=9)


with open("for-marcus.csv", "wb") as csvfile:

    fieldnames = ["institution", "rating", "date-submitted",
                  "version", "category", "subcategory",
                  "credit", "points"]

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    for cs in [CreditSet.objects.get(version=2.0),
               CreditSet.objects.get(version=2.1)]:

        reports = SubmissionSet.objects.exclude(
            rating__isnull=True).filter(
                creditset=cs).filter(
                    date_submitted__gte=START_DATE).filter(
                        date_submitted__lte=END_DATE).order_by(
                            "institution__name", "-date_submitted", "-id")

        institutions = []
        latest_reports = []  # only use the latest report

        for report in reports:
            # Just take first report for each institution.
            if report.institution in institutions:
                continue  # Not the first report for this institution.
            latest_reports.append(report)
            institutions.append(report.institution)

        for report in latest_reports:

            row = {"institution": str(report.institution),
                   "rating": str(report.rating),
                   "date-submitted": report.date_submitted,
                   "version": report.creditset.version}

            for category_submission in report.categorysubmission_set.all():
                row["category"] = str(category_submission.category)

                for subcategory_submission in category_submission.subcategorysubmission_set.all():  # noqa
                    row["subcategory"] = str(subcategory_submission.subcategory)  # noqa

                    for credit_submission in subcategory_submission.creditusersubmission_set.all():  # noqa
                        row["credit"] = str(credit_submission.credit)
                        row["points"] = credit_submission.assessed_points

                        writer.writerow(row)
