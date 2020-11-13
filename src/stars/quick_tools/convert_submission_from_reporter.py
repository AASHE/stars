from stars.apps.submissions.models import SubmissionSet

ssid = raw_input('SubmissionSet ID: ')

ss = SubmissionSet.objects.get(pk=ssid)
print ss

if not ss.reporter_status:
    print "This submission wasn't submitted with 'reporter_status'"
else:
    ss.reporter_status = False
    ss.pdf_report = None
    ss.save()
    ss.rating = ss.get_STARS_rating(recalculate=True)
    print "New Rating: %s" % ss.rating
    ss.save()
    # Update the institution if this is the currently rated submission
    if ss.institution.rated_submission == ss:
        ss.institution.current_rating = ss.rating
        ss.institution.save()