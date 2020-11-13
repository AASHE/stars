"""
    Find all subscriptions that have been unpaid for 30d or more
"""

from stars.apps.institutions.models import Subscription, Institution

from datetime import date, timedelta

thirty_days = timedelta(days=30)

for i in Institution.objects.filter(is_participant=True):
    if not i.current_subscription.paid_in_full:
        if i.current_subscription.start_date < date.today() - thirty_days:
            print i.current_subscription
            print "%d days past due" % (date.today() - i.current_subscription.start_date).days
            print i.current_subscription.amount_due
