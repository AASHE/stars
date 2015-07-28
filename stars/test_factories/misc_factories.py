import time

from aashe.aasheauth.models import AASHEUser
from django.contrib.auth.models import User
import factory


class AASHEUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = AASHEUser

    drupal_id = factory.Sequence(lambda i: i)


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    username = factory.Sequence(
        lambda i: 'testuser-{0}.{1}'.format(i, time.time()))
    password = 'test'
    email = factory.LazyAttribute(
        lambda o: '{0}@example.com'.format(o.username))
    aasheuser = factory.RelatedFactory(AASHEUserFactory,
                                       'user')

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user
