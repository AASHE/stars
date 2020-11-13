"""
Save all cached values on the submission model:
`percentage_score` and `adjusted_available_points`

Go through every rated submission and re-calculate these values
"""

from stars.apps.submissions.models import SubmissionSet

total_subs = 0
empty_available_points = 0
empty_claimed_points = 0

ss_list = SubmissionSet.objects.filter(status='r')
for ss in ss_list:
    for cat in ss.categorysubmission_set.all():
        for sub in cat.subcategorysubmission_set.all():
            total_subs += 1
            if sub.adjusted_available_points == None:
                empty_available_points += 1
            sub.get_adjusted_available_points()
            if sub.points == None:
                empty_claimed_points += 1
            sub.get_claimed_points()

print "total subcategories: %d" % total_subs
print "available point fields filled: %d" % empty_available_points
print "claimed point fields filled: %d" % empty_claimed_points
