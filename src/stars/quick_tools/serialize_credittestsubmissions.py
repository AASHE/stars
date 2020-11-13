#!/usr/bin/env python

from django.core import serializers
from django.db.models.query import CollectedObjects

from stars.apps.institutions.models import *
from stars.apps.submissions.models import *
#from stars.apps.credits import *

cts_list = []
cs_list = []
field_list = []

for cts in CreditTestSubmission.objects.all():
    cts_list.append(cts)
    cs = CreditSubmission.objects.get(pk=cts.creditsubmission_ptr_id)
    cs_list.append(cs)
    
    for field in cts.get_submission_fields():
        field_list.append(field)
    
objs = cts_list + cs_list + field_list

json = serializers.serialize("json", objs, indent=4) 

print json