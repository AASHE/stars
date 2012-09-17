import datetime
import time

import factory

from misc_factories import UserFactory
from stars.apps.institutions.models import Institution, StarsAccount, \
     Subscription, SubscriptionPayment


class InstitutionFactory(factory.Factory):
    FACTORY_FOR = Institution

    enabled = True
    slug = factory.Sequence(
        lambda i: 'test-inst-{0}-{1}'.format(i, time.time()))


class StarsAccountFactory(factory.Factory):
    FACTORY_FOR = StarsAccount

    institution = factory.SubFactory(InstitutionFactory)
    user = factory.SubFactory(UserFactory)


class SubscriptionFactory(factory.Factory):
    FACTORY_FOR = Subscription

    institution = factory.SubFactory(InstitutionFactory)
    start_date = '1970-01-01'
    end_date = datetime.date.today()
    amount_due = 1000.00


class SubscriptionPaymentFactory(factory.Factory):
    FACTORY_FOR = SubscriptionPayment

    subscription = factory.SubFactory(SubscriptionFactory)
    date = datetime.date.today()
    amount = 50.00
    user = factory.SubFactory(UserFactory)
