"""
Expiration dates:

    - Published reports submitted 03-01-2017 : 07-10-2018; set expiration to submission +  (365*3+180) days
    - Reports published on or after [RELEASE DATE TBD] expire three years from Publication Date.

"""

import datetime
import math

from stars.apps.institutions.models import Institution, InstitutionManager
from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import (
    SubmissionSet,
    SubmissionManager,
    CreditUserSubmission,
    NumericSubmission,
)


def set_expiration_on_rated_submissions():
    manager = SubmissionManager()
    report_headers = [
        "Extended Applied?",
        "Institution",
        "Report Submission Date",
        "Original Expiration Date",
        "New Expiration Date",
        "Liason Email Address",
    ]

    submissions_processed = []
    submissions_processed.append(u"\t".join(report_headers))

    for nextRatedSubmission in manager.get_rated():
        if nextRatedSubmission.date_submitted > datetime.date(
            2017, 03, 01
        ) and nextRatedSubmission.date_submitted < datetime.date(2017, 07, 10):
            date_expiration = nextRatedSubmission.date_submitted + datetime.timedelta(
                days=((365 * 3) + 180)
            )
            was_extended = True
        else:
            date_expiration = nextRatedSubmission.date_submitted + datetime.timedelta(
                days=(365 * 3)
            )
            was_extended = False

        nextRatedSubmission.date_expiration = date_expiration
        this_institution = Institution.objects.get(
            name=nextRatedSubmission.institution.name
        )

        extended = "Yes" if was_extended else "No"

        report_line = (
            u"\t".join(
                [
                    extended,
                    nextRatedSubmission.institution.name,
                    str(nextRatedSubmission.date_submitted),
                    str(
                        nextRatedSubmission.date_submitted
                        + datetime.timedelta(days=(365 * 3))
                    ),
                    str(date_expiration),
                    this_institution.contact_email,
                ]
            )
            .encode("utf-8")
            .strip()
        )
        submissions_processed.append(report_line)
        nextRatedSubmission.save()

    return submissions_processed


submissions_fixed = set_expiration_on_rated_submissions()

for nextFixed in submissions_fixed:
    print("\n %s" % nextFixed)
