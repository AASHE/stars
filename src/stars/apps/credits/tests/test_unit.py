"""Tests for apps.credits.models.Unit.
"""
from django.test import TestCase

from stars.apps.credits.models import Unit


class UnitTest(TestCase):

    fixtures = ['units.yaml']

    def __init__(self, *args, **kwargs):
        super(UnitTest, self).__init__(*args, **kwargs)
        self.unit = Unit()

    def test_ratio_cannot_be_None(self):
        """Is Unit.ratio == None disallowed?"""
        self.unit.ratio = None
        self.assertRaises(Exception, self.unit.save)

    def test_ratio_cannot_be_zero(self):
        """Is Unit.ratio == 0 disallowed?"""
        self.unit.ratio = 0
        self.assertRaises(Exception, self.unit.save)

    def test_revert_is_reverse_of_convert(self):
        """Is Unit.revert() the reverse of Unit.convert()?"""
        self.unit.ratio = 3.3
        self.unit.save()
        amount = 10
        self.assertEqual(amount,
                         self.unit.revert(self.unit.convert(amount)))

    def test_convert_is_reverse_of_revert(self):
        """Is Unit.convert() the reverse of Unit.revert()?"""
        self.unit.ratio = 3.3
        self.unit.save()
        amount = 10
        self.assertEqual(amount,
                         self.unit.convert(self.unit.revert(amount)))

    def test_convert_and_back_again(self):
        """
            Does converting from one to the other and back result in the
            original value?
        """
        self.unit.ratio = 0.092903
        self.unit.save()
        amount = 2000
        self.assertEqual(amount,
                         self.unit.convert(self.unit.revert(amount)))
        amount = 1999.99999
        self.assertEqual(2000,
                         self.unit.convert(self.unit.revert(amount)))
        amount = 2000.0000111
        self.assertEqual(2000,
                         self.unit.convert(self.unit.revert(amount)))

    def test_equivalent_conversion(self):
        """Is convert(X) == equivalent.convert(convert(X))?

        This is a test of data, really.  If the data's right
        (or at least symmetrically incorrect), the test will
        pass.  Data wrong?  Test fails.
        """
        amount = 1000
        result = ''
        for unit in Unit.objects.all():
            if unit.equivalent:
                unit_convert = unit.convert(amount)
                equivalent_convert = unit.equivalent.convert(unit_convert)
                if not round(equivalent_convert) == amount:
                    result += ('{unit}: {equivalent_convert} is not equal '
                               'to {amount}; ').format(
                                   unit=unit,
                                   equivalent_convert=equivalent_convert,
                                   amount=amount)
        self.assertEqual(result, '')
