from stars.tests.export_credit_content import export_credit_content

from stars.apps.credits.models import CreditSet
from stars.apps.third_parties.models import ThirdParty

cs = CreditSet.objects.get(pk=4)
ss = ThirdParty.objects.get(pk=2).get_snapshots().order_by("institution__name")

for cat in cs.category_set.all():
    for sub in cat.subcategory_set.all():
        for c in sub.credit_set.all():
            export_credit_content(c, ss=ss)