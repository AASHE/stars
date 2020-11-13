#!/usr/bin/env python

from stars.apps.institutions.models import *
from stars.apps.submissions.models import SubmissionSet
from stars.apps.submissions.tasks import send_certificate_pdf
from stars.apps.submissions.export.pdf import build_certificate_pdf

import sys

ss_id = raw_input("SubmissionSet id: ")
ss = SubmissionSet.objects.get(pk=int(ss_id))

outfile = "certificate.pdf"

pdf = build_certificate_pdf(ss)
f = open(outfile, 'w')
f.write(pdf.getvalue())
f.close()

# ss = SubmissionSet.objects.get(pk=60)
# print >> sys.stdout, "Running cert for %s" % ss
# send_certificate_pdf.delay(ss)
# print >> sys.stdout, "Done"
