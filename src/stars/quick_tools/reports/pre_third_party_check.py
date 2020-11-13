"""
    A report that attempts to catch issues with third party submissions
    before they arise:

        - Recent Reports (including in review) w/out snapshots
        - Recent Snapshots w/ no sharing
        - Sharing w/ no recent Snapshot

    "recent" means since the last deadline
"""
# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import datetime
from django.db.models import Q
from stars.apps.submissions.models import SubmissionSet
from stars.apps.institutions.models import Institution

LAST_DEADLINE = datetime.date(2016, 4, 1)

# recent reports w/out Snapshots
print
print "******************"
print "Institutions with reports submitted since last year with no snapshots:"
print "******************"
institution_with_reports = []
qs = SubmissionSet.objects.filter(Q(status='r') | Q(status='rv'))
qs = qs.filter(date_submitted__gt=LAST_DEADLINE).order_by('institution__name')
for ss in qs:
    if ss.institution not in institution_with_reports:
        institution_with_reports.append(ss.institution)
for i in institution_with_reports:
    snapshot_qs = i.submissionset_set.all().filter(status='f')
    if not snapshot_qs.filter(date_submitted__gt=LAST_DEADLINE).count():
        print "%s, %s" % (i, i.contact_email)

# Recent Snapshots w/ no sharing
print
print "******************"
print "Institutions who have a recent snapshot w/out any sharing setting:"
print "******************"
institution_with_snapshots = []
qs = SubmissionSet.objects.filter(status='f')
qs = qs.filter(date_submitted__gt=LAST_DEADLINE).order_by('institution__name')
for ss in qs:
    if ss.institution not in institution_with_snapshots:
        institution_with_snapshots.append(ss.institution)
for i in institution_with_snapshots:
    if not i.third_parties.count():
        print "%s, %s" % (i, i.contact_email)

# Sharing w/ no recent Snapshot
print
print "******************"
print "Institutions who are sharing, but don't have a recent snapshot:"
print "******************"
institutions_with_sharing = Institution.objects.exclude(third_parties=None)
for i in institutions_with_sharing.order_by('name'):
    snapshots = i.submissionset_set.filter(status='f')
    if not snapshots.filter(date_submitted__gt=LAST_DEADLINE).count():
        print "%s, %s" % (i, i.contact_email)
