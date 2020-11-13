#!/usr/bin/env python

from stars.apps.institutions.models import *
from stars.apps.submissions.models import SubmissionSet
from stars.apps.credits.models import CreditSet

cs = CreditSet.objects.get(pk=4)
row = "Institution"
for cat in cs.category_set.all():
    row = "%s,%s" % (row, cat.abbreviation)
print row

for ss in SubmissionSet.objects.filter(status='r'):
    row = ss.institution.name.replace(',', '')
    for cat in ss.categorysubmission_set.all():
        row = "%s,%s" % (row, round(cat.get_STARS_score(), 2))
    print row
    
    