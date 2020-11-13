from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import SubmissionSet

from datetime import date, timedelta

START_DATE = date(2016, 1, 1)
END_DATE = date(2017, 1, 1)

print "Start date: %s" % START_DATE
print "End date: %s" % END_DATE

# institutions who saved snapshots in 2016
snapshots_in_2016 = SubmissionSet.objects.filter(
    status='f').filter(date_submitted__year=2016)

institutions = Institution.objects.filter(
    id__in=snapshots_in_2016.values_list('institution_id').distinct())

# How many institutions submitted snapshots in 2016 (the period):
print "Total institutions with snapshots in period: %d" % institutions.count()

# Didn't have a valid or current STARS report in 2016 (the period)?
valid_start = START_DATE - timedelta(days=365*3)
print "Valid report period: %s" % valid_start
reports_valid_in_period = SubmissionSet.objects.filter(
    status='r').filter(
    date_submitted__gt=valid_start).filter(
    date_submitted__lte=END_DATE).filter(
    institution__in=institutions
    )

print "Had valid reports: %d" % reports_valid_in_period.count()

# Currently members
print "# that are currently members: %d" % (
    institutions.filter(is_member=True).count())
