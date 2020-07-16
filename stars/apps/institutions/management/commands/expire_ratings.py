#!/usr/bin/env python
"""
    Mark submissions as expired if they are over 3 years old
    and adjust the institution's current rating appropriately
"""
import datetime
import logging

from django.core.management.base import BaseCommand
from stars.apps.submissions.models import SubmissionSet


logger = logging.getLogger()


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("expire_ratings started")
        expire_ratings()
        logger.info("expire_ratings done")


def expire_ratings():

    today = datetime.date.today()
    rating_good_for = datetime.timedelta(days=365 * 3)

    # all rated submissions that haven't already expired
    for submissionset in (
        SubmissionSet.objects.filter(status="r")
        .exclude(expired=True)
        .exclude(date_expiration=None)
        .order_by("-date_submitted")
    ):

        if submissionset.date_expiration < datetime.date.today():
            logger.info("Expired: %s" % submissionset)
            logger.info("Date Submitted: %s" % submissionset.date_submitted)
            logger.info("Date Expiration: %s" % submissionset.date_expiration)
            submissionset.expired = True
            submissionset.save()

            institution = submissionset.institution

            institution.latest_expired_submission = submissionset

            if institution.rated_submission == submissionset:
                logger.info("**Only Rating (dropping current rating)")
                # This line is affecting the participants and reports table
                # institution.rated_submission = None
                institution.current_rating = None

            institution.save()
