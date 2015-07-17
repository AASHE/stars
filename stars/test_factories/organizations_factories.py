import datetime
import time

import factory

from issdjango.models import Organizations


class OrganizationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Organizations

    account_num = factory.Sequence(lambda i: '%s' % i)
    org_name = factory.Sequence(
        lambda i: 'test Organization {0}.{1}'.format(i, time.time()))
    exclude_from_website = False