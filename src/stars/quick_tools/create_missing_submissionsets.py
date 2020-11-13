"""
    A quick tool to create any SubmissionSets for institution
    that doesn't have a current one
    
    Current Participants
        - migrate last submissionset data
    
    Expired Participants
        - create blank submissionset
"""

from stars.apps.institutions.models import Institution
from stars.apps.migrations.utils import create_ss_mirror
from stars.apps.submissions.utils import init_credit_submissions
from stars.apps.submissions.models import SubmissionSet
from stars.apps.credits.models import CreditSet

from datetime import date

need_migration = []
need_new_ss = []

for i in Institution.objects.all():
    i.update_status()
    i.save()
    # If their current submission is rated we need to create a new one
    if i.current_submission == None or i.current_submission.status == 'r':
        if i.is_participant:
            # if they're a current participant migrate
            need_migration.append(i)
        else:
            # otherwise just create a new one
            need_new_ss.append(i)
            
        if i.current_submission == None:
            print "NO current submission: %s" % i
            
print "Need Migration (%d)" % len(need_migration)
print "--------------------"
for i in need_migration:
#    print i
    print "Migrating: %s" % i
    new_ss = create_ss_mirror(i.current_submission)
    new_ss.is_locked = False
    new_ss.is_visible = True
    new_ss.save()
    i.current_submission = new_ss
    i.save()
print ""
print "Need new SS (%d)" % len(need_new_ss)
print "--------------------"
for i in need_new_ss:
    print i
    ss = SubmissionSet(
                        institution=i,
                        creditset=CreditSet.objects.get_latest(),
                        registering_user=i.current_submission.registering_user,
                        status='ps',
                        date_registered=date.today(),
                        )
    ss.save()
    init_credit_submissions(ss)
    i.current_submission = ss
    i.save()