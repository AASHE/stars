"""
    Allison has requested accrual reporting from STARS
    This generates the report she has requested.

    STARS members and their renewal dates for all payments received in 2014
    through July 31st of 2014 - then I can calculate how much of their
    subscription we have "earned" thus far and how much I should defer to
    future dates.
"""

from stars.apps.institutions.models import Subscription, SubscriptionPayment

from datetime import date

start = date(year=2014, month=1, day=1)
end = date.today()

print "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
    "institution",
    "payment date",
    "amount",
    "subscription start",
    "subscription end",
    "payment method",
    "confirmation #")

for p in SubscriptionPayment.objects.filter(date__gte=start).filter(date__lt=end).order_by("date"):
    try:
        print "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
            p.subscription.institution.name,
            p.date,
            p.amount,
            p.subscription.start_date,
            p.subscription.end_date,
            p.method,
            p.confirmation)
    except:
        print "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
            "*",
            p.subscription.start_date,
            p.subscription.end_date,
            p.amount,
            p.method,
            p.confirmation)
