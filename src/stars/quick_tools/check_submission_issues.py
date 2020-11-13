print "latest rated submission isn't tied to the institution"

from stars.apps.institutions.models import Institution

to_fix = []

for i in Institution.objects.all():
    qs = i.submissionset_set.filter(status='r')
    if qs.count() > 0:
        ss = qs.order_by('-date_submitted')[0]
        if i.rated_submission != ss:
            print i
            print ss.date_submitted
            to_fix.append((i, ss))

print "rated submissions that aren't visisble"

from stars.apps.submissions.models import SubmissionSet

for ss in SubmissionSet.objects.filter(status='r').filter(is_visible=False):
    print ss

print "fixing submisison issues"

from datetime import timedelta, date

td = timedelta(days=365*3)
for i,ss in to_fix:
    i.current_rating = ss.rating
    i.rated_submission = ss
    i.rating_expires = date.today() + td
    i.save()