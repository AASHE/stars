from django.contrib.auth.models import User

from stars.apps.submissions.tasks import perform_migration
from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import Institution

user = User.objects.get(email="ben@aashe.org")
cs2 = CreditSet.objects.get(pk=6)

# Find all the institutions that need to be migrated, and migrate them
# exclude the ITESM institutions

qs = Institution.objects.all()

print "Total Institutions: %d" % qs.count()

qs = qs.exclude(name__startswith="Instituto Tecno")
qs = qs.exclude(name="ITESM")

count = 0
for i in qs.order_by("name"):
    if i.current_submission.creditset.version != "2.0":
        print i.current_submission
        count += 1
        perform_migration.delay(i.current_submission.id, cs2.id, user.email)
print "Queued: %d" % count
