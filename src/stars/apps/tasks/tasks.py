from __future__ import absolute_import

from celery import shared_task

from stars.apps.tasks.notifications import (send_welcome_email,
                                            send_post_submission_survey)


@shared_task(name='tasks.send_notifications')
def send_notifications():

    # Welcome
    print "Sending Welcome Emails"
    send_welcome_email()

    # After Submission
    print "Sending Post Submission Survey"
    send_post_submission_survey()
