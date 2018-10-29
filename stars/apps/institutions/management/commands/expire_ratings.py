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
    for submissionset in SubmissionSet.objects.filter(
            status="r").exclude(expired=True):

        if submissionset.date_submitted + rating_good_for < today:
            logger.info("Expired: %s" % submissionset)
            logger.info("Date Submitted: %s" % submissionset.date_submitted)
            submissionset.expired = True
            submissionset.save()

            # update the institution if this is still their
            # latest rated submission
            institution = submissionset.institution
            if institution.rated_submission == submissionset:
                logger.info("**Only Rating (dropping current rating)")
                institution.rated_submission = None
                institution.current_rating = None
                institution.latest_expired_submission = submissionset
                institution.save()