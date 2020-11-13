from django.db import models
from stars.apps.submissions.models import SubmissionSet

class EmailNotification(models.Model):
    """
        Represents a scheduled email

        - One month after registration, send an email if they still haven't
        paid
    """

    EMAIL_TYPES = (
        ('4wk', '4 Weeks Late'),
        ('6mn', "6 months left"),
        ('wel', 'Welcome'))

    sent_date = models.DateTimeField(auto_now_add=True)
    sent_to = models.CharField(max_length=128)
    subject = models.CharField(max_length=128)
    notification_type = models.CharField(max_length=7, choices=EMAIL_TYPES)
    identifier = models.CharField(max_length=16)
