from stars.apps.institutions.models import Institution

print "Institution, First Signup Date, Subscriptions"

for i in Institution.objects.order_by('name'):
    row = [i.name,]
    if i.date_created:
        row.append(i.date_created.date())
    else:
        row.append("--")
    for s in i.subscription_set.all():
        row.append(s.start_date)
    
    line = ""
    for cell in row:
        line += "%s," % cell
        
    print line
