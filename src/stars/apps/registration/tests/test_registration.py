from django.test import TestCase
from datetime import date

from stars.apps.registration.views import init_submissionset
from stars.apps.institutions.models import Institution
from stars.apps.submissions.models import PAYMENT_TYPE_CHOICES
from stars.test_factories.models import CreditSetFactory

from django.contrib.auth.models import User


class RegistrationTestCase(TestCase):
    """
        Tests:

    """

    def setUp(self):
        self.user = User.objects.create(
            username='tester__aashe_org', is_active=True)
        self.user.save()
        self.inst = Institution.objects.create(name='Test Institution',
                                               aashe_id=-1,
                                               contact_first_name='Test',
                                               )
        self.inst.save()
        self.creditset = CreditSetFactory()

    def test_init_submissionset(self):
        """
            Tests:
                init_submissionset(institution, user)
            (I might make this a doctest later...)
        """

        t1 = date(2010, 2, 26)
        one_year_hence = date(2011, 2, 26)
        submissionset = init_submissionset(self.inst, self.user, t1)

        self.assertEquals(submissionset.status, 'ps')
        self.assertEquals(submissionset.date_registered, t1)
        self.assertEquals(submissionset.registering_user, self.user)

        # leap year case
        t1 = date(2012, 2, 26)
        one_year_hence = date(2013, 2, 25)
        submissionset.delete()
        submissionset = init_submissionset(self.inst, self.user, t1)
