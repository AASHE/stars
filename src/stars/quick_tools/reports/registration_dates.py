from stars.apps.institutions.models import Institution

print "Institution\tAccount Created\tFirst Subscription Date\tFirst Snapshot Date"

for i in Institution.objects.order_by('name'):
    sub = ""
    if i.subscription_set.all():
        sub = i.subscription_set.order_by('start_date')[0].start_date
    
    snap = ""    
    if i.submissionset_set.filter(status='f').order_by('date_submitted'):
        snap = i.submissionset_set.filter(status='f').order_by('date_submitted')[0].date_submitted
        
    if not i.date_created:
        create_date = sub
    else:
        create_date = i.date_created.date()
    
    print "%s\t%s\t%s\t%s" % (i, create_date, sub, snap) 