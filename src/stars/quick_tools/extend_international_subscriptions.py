from stars.apps.institutions.models import Institution, Subscription
from stars.apps.notifications.models import EmailTemplate

from datetime import date

DEADLINE = date(year=2013, day=31, month=12)

for i in Institution.objects.filter(international=True):

    # if they have a current subscription, extend it
    if i.current_subscription:
        i.current_subscription.end_date = DEADLINE

    # if they don't have a current subscription, extend the most recent one
    else:
        try:
            i.current_subscription = i.subscription_set.all().order_by('-end_date')[0]
        except IndexError:
            # they don't have any subscriptions, so create one
            i.current_subscription = Subscription(start_date=date.today(),
                                                  end_date=DEADLINE,
                                                  institution=i,
                                                  amount_due=0,
                                                  paid_in_full=True)
        i.is_participant = True

    i.current_subscription.save()
    i.save()

    # remove any subscriptions that extend into 2014
    i.subscription_set.filter(end_date__gt=DEADLINE).delete()

    # send email notification
    et = EmailTemplate.objects.get(slug='international_extension')
    et.send_email([i.contact_email], {})
