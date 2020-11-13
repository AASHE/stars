import datetime

from django.test import TestCase

from stars.apps.institutions.data_displays.models import AuthorizedUser


class AuthorizedUserTestCase(TestCase):

    def test_authorized_user_can_be_created(self):
        """Can an AuthorizedUser be created?
        Because we have to test *some*thing, and
        AuthorizedUser doesn't *do* anything.
        """
        AuthorizedUser.objects.create(
            start_date=datetime.date.today(),
            end_date=datetime.date.today())
