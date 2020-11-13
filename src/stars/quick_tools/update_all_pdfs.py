from stars.apps.submissions.models import SubmissionSet

for ss in SubmissionSet.objects.filter(status='r'):
    pdf = ss.get_pdf(save=True)