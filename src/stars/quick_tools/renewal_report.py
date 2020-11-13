"""
    Allison has requested this report:

    "Is there any quick way to run STARS reports for October, November &
    December to show who is due for renewal and the dollar amounts associated
    if they all did renew on time at renewal date?"

    Columns:
        Institution name
        Subscription Renewal date (if all were to renew when they "should")
        Amount due upon renewal
        Date of the Last time they paid/subscribed

    Assumptions:
     - amount due will be the same as they paid last time
     - that they will renew. we don't have a high renewal rate
        (I should figure out what that is)
"""

from stars.apps.institutions.models import Subscription, SubscriptionPayment

from datetime import date

start = date.today()
end = date(year=2015, month=1, day=1)

print "%s\t%s\t%s\t%s\t%s" % (
    "institution",
    "renewal date",
    "amount due",
    "date of last payment",
    "subscription start date")

qs = Subscription.objects.all()
qs = qs.filter(end_date__gte=start).filter(end_date__lt=end)


for s in qs.order_by("end_date"):

    # get last payment
    if s.subscriptionpayment_set.count() > 2:
        assert(False, "MORE THAN TWO")

    print "%s\t%s\t%s\t%s\t%s" % (
        s.institution.name,
        s.end_date,
        s.subscriptionpayment_set.all()[0].amount,
        s.subscriptionpayment_set.all()[0].date,
        s.start_date
    )
    # try:
    #     print "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
    #         p.subscription.institution.name,
    #         p.date,
    #         p.amount,
    #         p.subscription.start_date,
    #         p.subscription.end_date,
    #         p.method,
    #         p.confirmation)
    # except:
    #     print "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
    #         "*",
    #         p.subscription.start_date,
    #         p.subscription.end_date,
    #         p.amount,
    #         p.method,
    #         p.confirmation)
