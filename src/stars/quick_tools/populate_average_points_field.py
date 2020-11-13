"""
Save average_points cached value on the subcategory model.

Go through every rated submission and re-calculate these values.
"""
from stars.apps.credits.models import Subcategory
from stars.apps.submissions.models import SubcategorySubmission

subcategory_count = Subcategory.objects.count()
processed = 0

for subcategory in Subcategory.objects.all():
    subcategory_total_points = 0
    submission_count = 0
    for subcategory_submission in SubcategorySubmission.objects.filter(
            subcategory=subcategory):
        category_submission = subcategory_submission.category_submission
        if category_submission.submissionset.status == 'r':  # only rated
            subcategory_total_points += (
                subcategory_submission.get_claimed_points())
            submission_count += 1
    if submission_count:
        subcategory.average_points = (subcategory_total_points /
                                      submission_count)
        subcategory.save()
    processed += 1
    print '{processed}/{subcategory_count}: {average_points}'.format(
        processed=processed,
        subcategory_count=subcategory_count,
        average_points=subcategory.average_points)
