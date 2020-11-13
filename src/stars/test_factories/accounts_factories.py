import factory

from stars.apps.accounts.models import UserProfile
from stars.test_factories.misc_factories import UserFactory


class UserProfileFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserProfile

    user = factory.SubFactory(UserFactory)
