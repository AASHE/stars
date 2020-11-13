from django.test import TestCase

from stars.apps import credits
from stars.test_factories import credits_factories


class CreditSetFactoryTest(TestCase):

    def test_creditset_has_unique_version(self):
        """Does each CreditSet get a unique version?"""
        first_creditset = credits_factories.CreditSetFactory()
        second_creditset = credits_factories.CreditSetFactory()
        self.assertNotEqual(first_creditset.version,
                            second_creditset.version)


class CategoryFactoryTest(TestCase):

    def test_creditset_is_produced(self):
        """Is a CreditSet produced when a Category is?"""
        category = credits_factories.CategoryFactory()
        self.assertIsInstance(category.creditset,
                              credits.models.CreditSet)


class SubCategoryFactoryTest(TestCase):

    def test_category_is_produced(self):
        """Is a Category produced when a Subcategory is?"""
        subcategory = credits_factories.SubcategoryFactory()
        self.assertIsInstance(subcategory.category,
                              credits.models.Category)


class CreditFactoryTest(TestCase):

    def test_subcategory_is_produced(self):
        """Is a Subcategory produced when a Credit is?"""
        credit = credits_factories.CreditFactory()
        self.assertIsInstance(credit.subcategory,
                              credits.models.Subcategory)


class ApplicabilityreasonFactoryTest(TestCase):

    def test_credit_is_produced(self):
        """Is a Credit produced when a ApplicabilityReason is?"""
        applicability_reason = credits_factories.ApplicabilityReasonFactory()
        self.assertIsInstance(applicability_reason.credit,
                              credits.models.Credit)


class RatingFactoryTest(TestCase):

    def test_creditset_is_produced(self):
        """Is a CreditSet produced when a Rating is?"""
        rating = credits_factories.RatingFactory()
        self.assertIsInstance(rating.creditset,
                              credits.models.CreditSet)
