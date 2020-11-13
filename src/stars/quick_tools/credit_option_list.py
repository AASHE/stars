#!/usr/bin/env python

"""
    Print an option list of credits
"""

from stars.apps.credits.models import *

cs = CreditSet.objects.get(pk=2)

print "<select>"
for cat in cs.category_set.all():
    print "<option>%s</option>" % cat.upper()
    print "<option disabled='disabled'>-----------------</option>"
    
    for sub in cat.subcategory_set.all():
        print "<option>-&nbsp;%s</option>" % sub
        
        for c in sub.get_t1_credits():
            print "<option>