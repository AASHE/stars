from stars.apps.submissions.models import SubmissionSet

for ss in SubmissionSet.objects.all():
    c = ss.categorysubmission_set.count()
    if c > 4:
        print ss