"""
    Sometimes an institution will check the "reporter" option when submitting
    by mistake and want to get their rating updated. This does that.
"""

from stars.apps.submissions.models import SubmissionSet

ssid = raw_input('SubmissionSet ID: ')

ss = SubmissionSet.objects.get(pk=ssid)
print "updating rating for: %s" % ss

ss.reporter_status = False
ss.save()
ss.rating = ss.get_STARS_rating(recalculate=True)
ss.save()

ss.institution.current_rating = ss.rating
ss.institution.save()

print "new rating: %s" % ss.rating
