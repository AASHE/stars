#!/usr/bin/env python

from stars.apps.institutions.models import *
from stars.apps.submissions.models import SubmissionSet
from stars.apps.credits.models import CreditSet

cs = CreditSet.objects.get(pk=4)
row = "Institution"
for cat in cs.category_set.all():
    for sub in cat.subcategory_set.all():
        for credit in sub.credit_set.all():
            row = "%s,%s" % (row, credit.title)
print row

for ss in SubmissionSet.objects.filter(status='r'):
    row = ss.institution.name.replace(',', '')
    for cat in ss.categorysubmission_set.all():
        for sub in cat.subcategorysubmission_set.all():
            for credit in sub.creditusersubmission_set.all():
                row = "%s,%s" % (row, round(credit.assessed_points, 2))
    print row
    
    
