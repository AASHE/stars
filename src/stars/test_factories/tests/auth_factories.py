import django.test import TestCase

from django.contrib.auth.models import User

from stars.test_factories import auth_factories


class AASHEAccountFactoryTest(TestCase):

    def test_user_is_created(self):
        """Does AASHEAccountFactory create a user?"""
        aashe_account = auth_factories.AASHEAccountFactory()
        self.assertIsInstance(aashe_account.user, User)

    def test_user_is_assigned(self):
        """If supplied, is a user connected to the AASHEAccount?"""
        user = User.objects.create_user(
            username='jimmyd',
            email='jimmyd@milfordnoname.org',
            password='please not a stripper!')
        aashe_account = auth_factories.AASHEAccountFactory(
            user=user)
        self.assertIs(user, aashe_account.user)
