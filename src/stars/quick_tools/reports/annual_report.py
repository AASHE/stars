from stars.apps.institutions.models import \
    Institution, Subscription, SubscriptionPayment
from stars.apps.submissions.models import SubmissionSet

"""
    Ratings Earned in 2016 (1/1 - 12/31):
    Lifetime Ratings:  647 (as of Oct. 16)
    Total Active Ratings: 286
    Registrations in 2016 (1/1 - 12/31):
    Renewals:
    New Registrants:
    Lifetime Registrations: 789 (as of Oct. 21)
    STARS Participants By Country:
    US:
    Canada:
    International:
    To view a full list of STARS Participants, browse all reports.
"""

YEAR = 2016


print "Ratings Earned in %d (1/1 - 12/31): %d" % (
    YEAR,
    SubmissionSet.objects.filter(status='r').filter(
        date_submitted__year=YEAR).count())

print "Lifetime Ratings: %d" % SubmissionSet.objects.filter(status='r').count()

print "Total Active Ratings: %d" % (
    Institution.objects.filter(current_rating__isnull=False).count())

print "Lifetime Registrations (unique institutions): %d" % (
    Subscription.objects.values_list(
        'institution', flat=True).distinct().count())

print "Registrations in %d (1/1 - 12/31):" % YEAR
print "\tRenewals: %d" % Subscription.objects.filter(
    start_date__year=YEAR).filter(reason__contains='_renew').count()
print "\tNew Registrants: %d" % Subscription.objects.filter(
    start_date__year=YEAR).filter(reason__contains='_reg').count()

print "STARS (paid) Participants By Country:"
print "US: %d" % Institution.objects.filter(
    current_subscription__isnull=False).filter(
        country='United States of America').count()
print "Canada: %d" % Institution.objects.filter(
    current_subscription__isnull=False).filter(country='Canada').count()
print "International: %d" % Institution.objects.filter(
    current_subscription__isnull=False).filter(international=True).count()
