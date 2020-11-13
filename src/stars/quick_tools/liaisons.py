#!/usr/bin/env python

from stars.apps.institutions.models import Institution

for i in Institution.objects.all():
    print i.contact_email
