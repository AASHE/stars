import datetime
import time

import factory

from misc_factories import UserFactory
from stars.apps.institutions.models import (ClimateZone, Institution,
                                            PendingAccount, StarsAccount,
                                            Subscription, SubscriptionPayment)


class ClimateZoneFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ClimateZone


class InstitutionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Institution

    enabled = True
    slug = factory.Sequence(
        lambda i: 'test-inst-{0}-{1}'.format(i, int(time.time())))
    name = factory.Sequence(
        lambda i: 'test institution {0}.{1}'.format(i, int(time.time())))
    aashe_id = factory.Sequence(
        lambda i: '%s' % i)


class PendingAccountFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PendingAccount

    institution = factory.SubFactory(InstitutionFactory)
    user_email = factory.Sequence(
        lambda i: 'testuser{0}{1}@example.com'.format(i, time.time()))


class StarsAccountFactory(factory.DjangoModelFactory):
    FACTORY_FOR = StarsAccount

    institution = factory.SubFactory(InstitutionFactory)
    user = factory.SubFactory(UserFactory)


class SubscriptionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Subscription

    institution = factory.SubFactory(InstitutionFactory)
    start_date = '1970-01-01'
    end_date = datetime.date.today()
    amount_due = 1000.00


class SubscriptionPaymentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = SubscriptionPayment

    subscription = factory.SubFactory(SubscriptionFactory)
    date = datetime.date.today()
    amount = 50.00
    user = factory.SubFactory(UserFactory)
