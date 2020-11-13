"""
    Fixing a mass email that went out accidentally
"""

import re
from datetime import date, timedelta

from stars.apps.institutions.models import Institution


def eval_participant_status(i):
    """
        Does the evaluation of participant status, instead of using
        the is_participant field

        returns (is_participant, current_subscription)
    """

    # see if there is a current subscription
    for sub in i.subscription_set.order_by('start_date'):
        if sub.start_date <= date.today() and sub.end_date >= date.today():
            return (True, sub)

    return (False, None)


filename = "institution_list.txt"

institution_list = []
exp_institutions = []
late_institutions = []

with open(filename) as f:
    institution_list = f.readlines()

exp_pattern = "(.*) subscription expired"
late_pattern = "Late payment: (.*) \(\d{4}-\d{2}-\d{2} - \d{4}-\d{2}-\d{2}\)"
for i in institution_list:
    m = re.match(exp_pattern, i)
    if m:
        exp_institutions.append(m.groups(1)[0])
    else:
        m = re.match(late_pattern, i)
        if m:
            late_institutions.append(m.groups(1)[0])
        else:
            print "not parsed: %s" % i

print "expired: %d" % len(exp_institutions)
print "late: %d" % len(late_institutions)

thirty = timedelta(days=31)

# for i in late_institutions:
#     inst = Institution.objects.get(name=i)
#     sub = inst.current_subscription
#     if not sub:
#         print inst 
#     elif sub.start_date < date.today() and sub.end_date > date.today():
#         if sub.start_date < (date.today() - timedelta(days=30)):
#             if sub.paid_in_full == False:
# #                 print "*****LATE"
#                 print sub
#                 print 

# fix those institutions that aren't really late...
# print "Not really late: "
not_really_late = []
really_late = []
for i in late_institutions:
    inst = Institution.objects.get(name=i)
    sub = inst.current_subscription
    if not sub or sub.paid_in_full:
        not_really_late.append(inst)
    else:
        really_late.append(inst)

print "Late total: %d" % len(really_late)
print "Not late total: %d" % len(not_really_late)

print "Not late emails"
for i in not_really_late:
    p, sub = eval_participant_status(i)
    i.is_participant = p
    sub.late = False
    sub.save()
    i.current_subscription = sub
    i.save()
