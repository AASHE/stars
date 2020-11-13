from stars.apps.institutions.models import *
from stars.apps.credits.models import *
from stars.apps.submissions.models import *
from stars.apps.migrations.utils import migrate_submission

ss = SubmissionSet.objects.get(pk=99)

cs = CreditSet.objects.get(pk=4)

new_ss = migrate_submission(ss, cs)