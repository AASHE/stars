"""Tests for apps.institutions.models.Subscription.
"""
from datetime import date, timedelta
from functools import wraps
from logging import getLogger, CRITICAL
import re

from django.conf import settings
from django.core import mail
from django.test import TestCase
import testfixtures

from stars.apps.institutions.models import (Subscription,
                                            SubscriptionPayment,
                                            SubscriptionPurchaseError,
                                            SUBSCRIPTION_DURATION)

from stars.apps.registration.models import (ExpiredDiscountCodeError,
                                            InvalidDiscountCodeError,
                                            ValueDiscount)
from stars.test_factories.models import (InstitutionFactory, SubscriptionFactory,
                                         UserFactory, ValueDiscountFactory)

# Don't bother me:
logger = getLogger('stars')
logger.setLevel(CRITICAL)


class SubscriptionTest(TestCase):

    fixtures = ['email_templates.json']

    def setUp(self):
        self.subscription = SubscriptionFactory(
            institution=InstitutionFactory())
        self.member = InstitutionFactory(is_member=True)
        self.nonmember = InstitutionFactory(is_member=False)

    ###################################################################
    # test that the email templates get the context they're expecting:
    ###################################################################

    def _invalid_template_strings(self, text, marker=None):
        marker = marker or settings.TEMPLATE_STRING_IF_INVALID
        invalid_strings = []
        for match in re.finditer(marker.replace('%s', '(.*)'),
                                 text):
            invalid_strings.append(match.groups()[0])
        return invalid_strings or None

    def _test_email_templates_ok(actual_test):
        @wraps(actual_test)
        def _test(self):
            settings.TEMPLATE_STRING_IF_INVALID = (
                'INVALID TEMPLATE STRING %s /INVALID TEMPLATE STRING')

            actual_test(self)

            for message in mail.outbox:
                invalid_strings = self._invalid_template_strings(message.body)
                self.assertIsNone(invalid_strings,
                                  msg=("invalid template string(s): " +
                                       str(invalid_strings)))
        return _test
