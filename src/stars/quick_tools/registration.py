from stars.apps.registration.utils import *

print "Orphaned SubmissionSets:"
for ss in get_orphaned_submissionsets():
    print ss.id
print ""

print "Orphaned Payments:"
orphaned_payments = get_orphaned_payments()
for p in orphaned_payments:
    print p.id
print ""

print "Payment IDs and Institution"
for p in Payment.objects.all():
    try:
        print "%d, %s, %s, %s, %s" % (p.id, p.submissionset.institution, p.user, p.date, p.amount)
    except:
        print "%d, , %s, %s, %s" % (p.id, p.user, p.date, p.amount)
