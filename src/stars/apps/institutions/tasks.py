from __future__ import absolute_import

import logging
from celery import shared_task
from dateutil.relativedelta import relativedelta
from datetime import date

from .utils import update_all_institution_properties
from .models import Institution
from stars.apps.notifications.models import EmailTemplate


logger = logging.getLogger()


@shared_task(name='institutions.monitor_subscription')
def monitor_subscription():
    update_all_institution_properties()


@shared_task(name='institutions.update_from_iss')
def update_from_iss():
    for i in Institution.objects.all():
        i.update_from_iss()
        try:
            i.save()
        except Exception as exc:
            logger.error(
                "Can't save institution {}: {}".format(
                    i.name, exc))


@shared_task(name='institutions.email_expiring_ratings')
def email_expiring_ratings():
    date_to_check = date.today() + relativedelta(days=+30)
    qs = Institution.objects.filter(
        rating_expires__year=date_to_check.year,
        rating_expires__month=date_to_check.month,
        rating_expires__day=date_to_check.day
    )

    for ob in qs:
        email_to = [ob.contact_email]
        if ob.access_level is "Full":
            email_slug = "exp_rating_reminder_participant"
        else:
            email_slug = "exp_rating_reminder_nonparticipa"

        et = EmailTemplate.objects.get(slug=email_slug)
        email_context = {
            "contact_first_name": ob.contact_first_name,
        }
        et.send_email(email_to, email_context)
