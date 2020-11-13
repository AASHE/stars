#!/usr/bin/env python

from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.tasks import send_certificate_pdf

from django.conf import settings

import sys

settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
settings.CELERY_ALWAYS_EAGER = True

ss_id = raw_input("SubmissionSet id: ")
ss = SubmissionSet.objects.get(pk=int(ss_id))

print >> sys.stdout, ss
print >> sys.stdout, "%s - %s" % (ss.date_submitted, ss.rating)
send_certificate_pdf.delay(ss.id)
