from stars.apps.submissions.models import SubmissionSet

for ss in SubmissionSet.objects.get_rated():
    print "%s, %s, %s, %s" % (ss.institution.contact_first_name, ss.institution.contact_last_name, ss.institution.contact_email, ss.rating)