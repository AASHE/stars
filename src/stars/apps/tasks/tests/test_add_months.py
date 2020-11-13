from django.test import TestCase

from stars.apps.tasks.notifications import add_months
from datetime import date


class AddMonthsTest(TestCase):

    def setUp(self):
        pass

    def test_adding(self):
        d = date(year=2010, month=10, day=1)

        d = add_months(d, 1)
        self.assertEqual(d, date(year=2010, month=11, day=1))

        d = add_months(d, 1)
        self.assertEqual(d, date(year=2010, month=12, day=1))

        d = add_months(d, 1)
        self.assertEqual(d, date(year=2011, month=1, day=1))

        d = add_months(d, 13)
        self.assertEqual(d, date(year=2012, month=2, day=1))

        d = add_months(d, -13)
        self.assertEqual(d, date(year=2011, month=1, day=1))

        d = add_months(d, -1)
        self.assertEqual(d, date(year=2010, month=12, day=1))
