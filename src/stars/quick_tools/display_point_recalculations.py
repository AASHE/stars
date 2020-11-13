"""
    display_point_recalculations.py

    Shows what a group of institutions scores would be if scores were
    recalculated. This is useful for seeing the effects of a scoring formula
    change, or even to detect inconsistencies.
"""

from stars.apps.submissions.models import SubmissionSet, CreditUserSubmission
from stars.apps.credits.models import Credit

# get the list of submissionsets
ss_list = SubmissionSet.objects.filter(status='r')
ss_list = ss_list.filter(creditset__version="2.0")

# specific credit to recalculate
credit = Credit.objects.get(pk=538) # op-22

# list every submission with old score and new score
for ss in ss_list:
    cus = CreditUserSubmission.objects.get(
        credit=credit,
        subcategory_submission__category_submission__submissionset=ss)
    if cus.assessed_points != cus._calculate_points():
        print "%s %f %f" % (ss, cus.assessed_points, cus._calculate_points())
