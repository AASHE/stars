import time

import factory

from iss.models import Organization


class OrganizationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Organization

    account_num = factory.Sequence(lambda i: '%s' % i)
    org_name = factory.Sequence(
        lambda i: 'test Organization {0}.{1}'.format(i, time.time()))
    exclude_from_website = False
