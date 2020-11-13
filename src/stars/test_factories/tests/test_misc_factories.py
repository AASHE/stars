from django.test import TestCase

from stars.test_factories import misc_factories


class UserFactoryTest(TestCase):

    def test_password_is_hashed(self):
        """Is the password for a user hashed?"""
        plain_text_password = misc_factories.UserFactory.attributes('password')
        user = misc_factories.UserFactory()
        self.assertNotEqual(plain_text_password,
                            user.password)
