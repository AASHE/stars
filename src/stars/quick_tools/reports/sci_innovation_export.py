"""
    Hint:
        $ PYTHONIOENCODING=UTF-8 ./manage.py shell
        In [1]: %run stars/quick_tools/reports/sci_innovations_export.py
"""
import datetime
import unicodecsv as csv

from stars.apps.submissions.models import (SubmissionSet,
                                           SUBMISSION_STATUSES)
from stars.apps.credits.models import CreditSet


"""
- All published version 2.0 and 2.1 reports that are valid (i.e. not
Expired) at 11:59pm EST on June 30, 2017.
- Need to include reports that have been FINALIZED BUT NOT PUBLISHED,
i.e., those that submitted in May/June 2016 that have not yet addressed the
review results.
"""

"""
- CreditSet version
- Institution Name
- Submit Date
- Innovation Title
- Innovation Description
- Innovation measurable outcomes (2.0 only)
- Innovation Topics (institutions can select up to 5).
"""


DEADLINE = datetime.date(year=2017, month=6, day=30)

with open("sci_innovations_export.csv", "wb") as csvfile:

    fieldnames = ["Version", "Institution", "Submitted",
                  "Subcategory", "Identifier", "Title",
                  "Description", "Measurable Outcomes", "Topics"]

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    for creditset in CreditSet.objects.filter(version__startswith="2"):

        submissionsets = SubmissionSet.objects.filter(creditset=creditset)
        submissionsets = submissionsets.filter(
            status__in=[
                SUBMISSION_STATUSES["RATED"],
                SUBMISSION_STATUSES["REVIEW"]])

        submissionsets = submissionsets.filter(expired=False).filter(
            date_submitted__lte=DEADLINE)

        for submissionset in submissionsets:

            cat_sub = submissionset.categorysubmission_set.get(
                category__abbreviation="IN")

            for subcat_sub in cat_sub.subcategorysubmission_set.all():

                for credit_user_submission in \
                    subcat_sub.creditusersubmission_set.all():

                    row = {
                        "Version": creditset.version,
                        "Institution": str(submissionset.institution),
                        "Submitted": submissionset.date_submitted,
                        "Subcategory": subcat_sub.subcategory.category.title,
                        "Identifier": credit_user_submission.credit.identifier}

                    submission_fields = (
                        credit_user_submission.get_submission_fields())

                    try:
                        row["Title"] = submission_fields[0].value
                    except AttributeError:
                        row["Title"] = "?"
                    row["Description"] = submission_fields[1].value
                    row["Measurable Outcomes"] = submission_fields[2].value

                    try:
                        row["Topics"] = submission_fields[9].value
                    except AttributeError:
                        row["Topics"] = submission_fields[-2].value
                    except IndexError:
                        row["Topics"] = "?"

                    writer.writerow(row)


"""
- Institution Name
- Submit Date
- Innovation Title
- Innovation Description
- Innovation measurable outcomes (2.0 only)
- Innovation Topics (institutions can select up to 5).
"""
