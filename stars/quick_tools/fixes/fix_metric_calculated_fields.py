"""
Find all submissions for metric institutions within
the last year

Re-run the calculated fields

Re-score the submissions
"""

import datetime
import math

from stars.apps.institutions.models import Institution
from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import (
    SubmissionSet,
    CreditUserSubmission,
    NumericSubmission,
)


def fix_metric_submissions():
    for i in Institution.objects.filter(prefers_metric_system=True):
        # find all calculated fields for their current submission

        # submission_to_fix = i.current_submission

        submission_to_fix = i.get_latest_rated_submission()
        if submission_to_fix:
            fix_submission(submission_to_fix)


def fix_submission(submission_to_fix):

    i = submission_to_fix.institution

    print("*******************")
    print(submission_to_fix)
    print("(%d %d)" % (i.id, submission_to_fix.id))
    print("*******************")

    if submission_to_fix.status == "r":
        old_submission_score = submission_to_fix.score
        old_submission_rating = submission_to_fix.rating.name

    # for each credit submission, recalculate any calculated fields and recalculate score
    for cus in CreditUserSubmission.objects.filter(
        subcategory_submission__category_submission__submissionset=submission_to_fix
    ):
        calculated_fields = NumericSubmission.objects.filter(
            credit_submission=cus,
            documentation_field__type="calculated",
            documentation_field__units__isnull=False,
        )

        if calculated_fields:
            for cf in calculated_fields:
                current_val = cf.metric_value
                try:
                    cf.calculate()
                except:
                    print("\tformula failed: %s" % cf)
                calculated_val = cf.metric_value

                # if calculated_val != current_val:
                #     print("\t-------------------")
                #     print("\t%s" % cus)
                #     print("\t-------------------")
                #     print("\t\t%s" % cf)
                #     print(
                #         "\t\t\tcurrent: %d\t calculated: %d"
                #         % (current_val, calculated_val)
                #     )
                cf.save()
            current_points = cus.assessed_points
            cus.save()
            new_points = cus.assessed_points
            if current_points != new_points:
                print("\t######################")
                print("\t%s" % cus)
                print("\tPoints changed from %f to %f" % (current_points, new_points))
                print("\t######################")

    if submission_to_fix.status == "r":
        current_submission_score = submission_to_fix.get_STARS_score(recalculate=True)
        if math.floor(current_submission_score) != math.floor(old_submission_score):
            print(
                "\t------------------- Score Changed: [%f, %f]"
                % (old_submission_score, current_submission_score)
            )
        current_submission_rating = submission_to_fix.get_STARS_rating(recalculate=True)

        if str(old_submission_rating) != str(current_submission_rating.name):
            print(
                "\t!!!!!!!!!!!!!!!!!******* Rating Changed: [%s, %s]"
                % (old_submission_rating, current_submission_rating)
            )


fix_metric_submissions()
