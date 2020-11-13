from stars.apps.credits.models import Credit
from stars.apps.submissions.models import CreditUserSubmission

c = Credit.objects.get(pk=538)
count = 0
qs = CreditUserSubmission.objects.filter(credit=c).filter(
    submission_status='c')
cus_set = []

# find the submissions with point changes
for cus in qs:
    try:
        calculated_points = cus._calculate_points()
    except:
        calculated_points = 0

    if calculated_points != cus.assessed_points:
        print cus.get_submissionset()
        print "assessed: %f" % cus.assessed_points
        print "calculated: %f" % calculated_points
        count += 1
        cus_set.append(cus)

print "total: %d" % count

# how many are rated?
rated_count = 0
for cus in cus_set:
    if cus.get_submissionset().status == 'r':
        rated_count += 1

print "total rated: %d" % rated_count

# how could we get the
