#!/usr/bin/env python

from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.tasks import send_certificate_pdf

from django.conf import settings

from datetime import date
import sys

ss_list = SubmissionSet.objects.filter(date_submitted__gte=date(year=2014, month=1, day=1), status='r').order_by('date_submitted')

settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
settings.CELERY_ALWAYS_EAGER = True

for ss in ss_list:
    print >> sys.stdout, ss
    print >> sys.stdout, "%s - %s" % (ss.date_submitted, ss.rating)
    send_certificate_pdf.delay(ss.id)
#     print >> sys.stdout, "Done"
