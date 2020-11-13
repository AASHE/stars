from stars.apps.institutions.models import SubscriptionPayment
from stars.apps.third_parties.utils import UnicodeWriter

from celery.decorators import task
from django.core.files.temp import NamedTemporaryFile

import csv


@task()
def build_accrual_report_csv(year):

    print "Starting Accrual CSV Export for %s" % year

    outfile = NamedTemporaryFile(suffix='.csv', delete=False)

    writer = UnicodeWriter(outfile)

    writer.writerow([
        "institution",
        "payment date",
        "amount",
        "subscription start",
        "subscription end",
        "payment method",
        "confirmation #"
    ])

    qs = SubscriptionPayment.objects.all()
    qs = qs.filter(date__year=year).order_by("date")

    for p in qs:
        writer.writerow([
            p.subscription.institution.name,
            unicode(p.date),
            "%d" % p.amount,
            unicode(p.subscription.start_date),
            unicode(p.subscription.end_date),
            p.method,
            p.confirmation
        ])

    outfile.close()

    print "Created accrual report for %s: %s" % (year, outfile.name)
    return outfile.name
