#!/usr/bin/env python

from stars.apps.credits.models import CreditSet
from stars.apps.migrations.utils import migrate_creditset

from datetime import date

cs = CreditSet.objects.get(pk=2)
new_cs = migrate_creditset(cs, '1.1', date(year=2011, month=2, day=9))
