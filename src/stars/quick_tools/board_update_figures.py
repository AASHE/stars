from stars.apps.institutions.models import Institution, Subscription, SubscriptionPayment

import datetime

print "Total institutions with paid subscriptions (to date)"
inst_count = 0
renewals = 0
basic = 0
for i in Institution.objects.all():
    count = i.subscription_set.count()
    if count:
        inst_count += 1
    else:
        basic += 1
    if count > 1:
        renewals += 1
print inst_count

print "Total subscriptions - new & renewing (to date)"
print Subscription.objects.count()

print "Total subscription renewals (to date)"
print renewals

print "Total basic registrants (to date)"
print basic

print "Total STARS-rated institutions"
print Institution.objects.filter(current_rating__isnull=False).count()

total_participants = Institution.objects.filter(is_participant=True).count()
print "Current active subscriptions"
print total_participants

td = datetime.timedelta(days=365)
d = datetime.date.today() - td
total_last_year = Subscription.objects.filter(start_date__lte=d).filter(end_date__gte=d).count()
print "Active subscriptions on this date last year (%s)" % d
print total_last_year

renewal_count = 0
first_time_count = 0
for i in Institution.objects.filter(is_participant=True):
    sc = i.subscription_set.count()
    if sc > 1:
        renewal_count += 1
    else:
        first_time_count += 1

renewal_percent = float(renewal_count) / total_participants * 100
first_time_percent = float(first_time_count) / total_participants * 100

print "Current active subscriptions - renewals"
print "%d (%d%%)" % (renewal_count, renewal_percent)

print "Current active subscriptions - first-time subscribers"
print "%d (%d%%)" % (first_time_count, first_time_percent)

print "Canadian overal participants (to date)"
canada_count = 0
for i in Institution.objects.filter(country="Canada"):
    if i.subscription_set.count():
        canada_count += 1
print canada_count

print "Current Canadian Participants"
canada_count = 0
for i in Institution.objects.filter(country="Canada"):
    if i.is_participant:
        canada_count += 1
print canada_count

print "Canadian Rated Institutions"
canada_count = 0
for i in Institution.objects.filter(country="Canada"):
    if i.current_rating:
        canada_count += 1
print canada_count

this_year = datetime.datetime.now().year
last_year = this_year - 1

print "%d subscription revenue" % last_year
d_last = datetime.date(year=last_year, day=1, month=1)
d_this = datetime.date(year=this_year, day=1, month=1)
revenue = 0
for p in SubscriptionPayment.objects.filter(date__gte=d_last).filter(date__lt=d_this):
    revenue += p.amount
print revenue

print "%d subscription revenue (to date)" % this_year
revenue = 0
for p in SubscriptionPayment.objects.filter(date__gte=d_this):
    revenue += p.amount
print revenue
# $137,100
