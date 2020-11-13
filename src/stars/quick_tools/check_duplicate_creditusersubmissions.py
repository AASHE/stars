from stars.apps.institutions.models import *
from stars.apps.submissions.models import SubmissionSet, CreditUserSubmission

i = Institution.objects.get(aashe_id=17565)

for ss in SubmissionSet.objects.all().order_by('institution__name').filter(institution=i):
    
    dupes = []
    cus_qs = CreditUserSubmission.objects.filter(subcategory_submission__category_submission__submissionset=ss)
    for cs in cus_qs:
        
        # find any others that are submitting on the same credit
        if cs not in dupes:
            if cus_qs.filter(credit=cs.credit).count() > 1:
                dupes.append(cs)
                
    if dupes:
        print ss.institution
        for d in dupes:
            print "DUPE: %d %s %s %s" % (d.id, d.credit, d.credit.subcategory, d.subcategory_submission)
