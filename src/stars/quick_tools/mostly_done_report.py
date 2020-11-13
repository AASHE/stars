"""
A list of Submissions that

- are "current" (i.e., "My Submission")

- are >= 80% finished

Percent finished is calculated as

    (# not started credits + # in progress credits) / num-credits

When that's >= .2, >= 80% is done.

"""
import csv

from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import (NOT_STARTED,
                                           IN_PROGRESS)

credit_totals = {}


for creditset in CreditSet.objects.all():

    num_credits = 0

    for category in creditset.category_set.all():
        for subcategory in category.subcategory_set.all():
            for credit in subcategory.credit_set.all():
                num_credits += 1

    credit_totals[creditset] = num_credits


with open("/tmp/mostly_done.csv", "wb") as csvfile:

    csv_writer = csv.writer(csvfile)

    for institution in Institution.objects.all():

        if institution.current_submission is None:
            continue

        num_not_started = num_in_progress = 0

        last_category_updated = None

        for category_submission in (
                institution.current_submission.categorysubmission_set.all()):

            for subcategory_submission in (
                 category_submission.subcategorysubmission_set.all()):

                num_not_started += (
                    subcategory_submission.creditusersubmission_set.filter(
                        submission_status=NOT_STARTED).count())

                num_in_progress += (
                    subcategory_submission.creditusersubmission_set.filter(
                        submission_status=IN_PROGRESS).count())

                last_subcategory_updated = (
                    subcategory_submission.creditusersubmission_set.order_by(
                        "-last_updated"
                    ))[0].last_updated

            # Excuse me while I suck.
            if ((last_category_updated is not None and
                 last_category_updated < last_subcategory_updated) or
                last_category_updated is None):

                last_category_updated = last_subcategory_updated

        num_credits = credit_totals[institution.current_submission.creditset]

        percent_incomplete = (
            (float(num_not_started + num_in_progress) / num_credits) * 100)

        percent_complete = 100.0 - percent_incomplete

        csv_writer.writerow([institution.name.encode("utf-8"),
                             percent_complete,
                             percent_incomplete,
                             last_category_updated,
                             num_credits,
                             num_not_started])
