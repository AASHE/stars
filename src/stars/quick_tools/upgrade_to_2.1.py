from django.contrib.auth.models import User

from stars.apps.submissions.tasks import perform_migration
from stars.apps.credits.models import CreditSet
from stars.apps.institutions.models import Institution

user = User.objects.get(email="bob.erb@aashe.org")
cs2_1 = CreditSet.objects.get(version="2.1")

qs = Institution.objects.all()

print "Total Institutions: %d" % qs.count()

count = 0

for i in qs.order_by("name"):
    if i.current_submission.creditset.version != "2.1":
        print i.current_submission
        count += 1
        perform_migration.delay(i.current_submission.id, cs2_1.id, user.email)

print "Queued: %d" % count
