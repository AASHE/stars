"""
    Run daily to determine if any notifications need to be sent to
    institutions who haven't paid

    Institutions get a notification after 4 weeks indicating that they
    haven't paid.
"""
import logging
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta

# required for execfile management func
from stars.apps.institutions.models import *
from stars.apps.submissions.models import (Payment,
                                           PENDING_SUBMISSION_STATUS,
                                           SubmissionSet)
from stars.apps.tasks.models import EmailNotification
from stars.apps.notifications.models import EmailTemplate


logger = logging.getLogger()


def get_new_institutions(current_date):
    """
        Return a list of all institutions that paid more than a week ago.

        The notification handler ensures that these won't get sent to every
        time. I also limit the window to a week, so we're not running a ton of
        extra queries down the line
    """
    one_week = timedelta(weeks=1)
    date_start = current_date - one_week
    date_end = date_start - one_week

    i_list = []
    qs = Payment.objects.filter(date__lte=date_start)
    qs = qs.filter(date__gte=date_end).exclude(type='later')
    for p in qs:
        if (not p.submissionset.institution.charter_participant and
           p.submissionset.status == PENDING_SUBMISSION_STATUS):
            i_list.append(p.submissionset.institution)

    return i_list


def send_welcome_email(current_date=date.today()):
    """
        This is separated from `get_new_institutions` for testing purposes
    """

    for i in get_new_institutions(current_date):

        send_notification(
            n_type='wel',
            identifier="wel-%d" % i.id,
            mail_to=[i.contact_email],
            template_slug="welcome_one_week",
            email_context={'institution': i}
        )


def get_overdue_payments(weeks, current_date=date.today()):
    """
        Return a list of all submission sets that were registered
        more than `weeks` before the current and still have not paid
    """
    td = timedelta(weeks=weeks)
    date_limit = current_date - td

    ss_list = []
    qs = SubmissionSet.objects.filter(date_registered__lte=date_limit)
    qs = qs.filter(is_visible=True).order_by('institution__name')
    for ss in qs:
        if ss.get_amount_due() > 0 and ss.institution.aashe_id != 15889:
            # don't send to CSB
            ss_list.append(ss)

    return ss_list


def send_post_submission_survey(current_date=None):
    """
        Gets the submission sets that were submitted 2 weeks or more ago
        current_date is optional for debugging

        Don't send if more than 60 days old
    """

    if not current_date:
        current_date = date.today()

    td_14 = current_date - timedelta(days=14)
    td_60 = current_date - timedelta(days=60)
    message_list = []

    qs = SubmissionSet.objects.filter(status='r')
    qs = qs.filter(date_submitted__lte=td_14)
    qs = qs.filter(date_submitted__gte=td_60)

    for ss in qs:
        m = {
            'mail_to': [ss.institution.contact_email],
            'template_slug': "post_submission_survey",
            'email_context': {'ss': ss},
            'n_type': PENDING_SUBMISSION_STATUS,
            'identifier': 'ps-%d' % ss.id,
        }
        message_list.append(m)

    send_notification_set(message_list)


def send_notification_set(notification_set):
    """
        Sends a set of notifications
        set structure:
        (
            {'mail_to': [], 'message': '', 'n_type': '', 'identifier': '',
            'subject': ''},
            ...
        )
    """

    for n in notification_set:
        send_notification(
            n_type=n['n_type'],
            identifier=n['identifier'],
            mail_to=n['mail_to'],
            template_slug=n['template_slug'],
            email_context=n['email_context']
        )


def add_months(d, months):
    """
        Returns a number of months after the given date
        negative months are ok
    """

    return d + relativedelta(months=months)


def send_notification(n_type, identifier, mail_to, template_slug,
                      email_context, count=1):
    """
        Send a notification of a particular type, identifier and mail_to
        If this notification has already been sent `count` times, ignore it.
    """

    if EmailNotification.objects.filter(identifier=identifier).count() < count:

        try:
            et = EmailTemplate.objects.get(slug=template_slug)
            et.send_email(mail_to, email_context)

            en = EmailNotification(
                identifier=identifier,
                notification_type=n_type,
                sent_to=mail_to,
                subject=et.title)
            en.save()
        except Exception, e:
            logger.error("Message Send Failed: %s (%s) [%s]" % (
                mail_to, template_slug, e))
