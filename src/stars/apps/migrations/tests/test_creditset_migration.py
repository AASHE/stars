"""
    Test for migrating a creditset
"""

from django.test import TestCase

from stars.apps.credits.models import (ApplicabilityReason,
                                       Choice,
                                       Credit,
                                       CreditSet,
                                       DocumentationField,
                                       Subcategory)
from stars.apps.migrations.utils import migrate_creditset
from stars.apps.submissions.models import CreditTestSubmission
from stars.test_factories.models import (CategoryFactory,
                                         CreditFactory,
                                         CreditSetFactory,
                                         DocumentationFieldFactory,
                                         SubcategoryFactory)

from datetime import date


class CreditSetMigrationTest(TestCase):

    def test_get_latest_creditset(self):
        """Does Creditset.objects.get_latest() work?
        """
        CreditSetFactory(release_date='1970-01-01')
        latest_creditset = CreditSetFactory(
            release_date='2000-01-01')
        CreditSetFactory(release_date='1975-01-01')
        self.assertEqual(latest_creditset.id,
                         CreditSet.objects.get_latest().id)

    def test_migrate_creditset(self):
        """Does migrate_creditset make a faithful copy of a Creditset?
        """
        # One CreditSet.
        cs = CreditSetFactory()
        # Three Categories.
        first_category = CategoryFactory(creditset=cs)
        second_category = CategoryFactory(creditset=cs)
        CategoryFactory(creditset=cs)
        # Three Subcategories.
        first_subcategory = SubcategoryFactory(category=first_category)
        second_subcategory = SubcategoryFactory(category=second_category)
        SubcategoryFactory(category=second_category)
        # Two Credits.
        first_credit = CreditFactory(subcategory=first_subcategory)
        second_credit = CreditFactory(subcategory=second_subcategory)
        # Four Documentation Fields.
        DocumentationFieldFactory(credit=first_credit)
        DocumentationFieldFactory(credit=first_credit)
        DocumentationFieldFactory(credit=second_credit)
        DocumentationFieldFactory(credit=second_credit)

        new_cs = migrate_creditset(cs, "99.0", date.today())

        self.assertEqual(new_cs.category_set.count(),
                         cs.category_set.count())

        self.assertEqual(
            Subcategory.objects.filter(category__creditset=new_cs).count(),
            Subcategory.objects.filter(category__creditset=cs).count())

        self.assertEqual(
            Credit.objects.filter(
                subcategory__category__creditset=new_cs).count(),
            Credit.objects.filter(
                subcategory__category__creditset=cs).count())

        self.assertEqual(
            ApplicabilityReason.objects.filter(
                credit__subcategory__category__creditset=new_cs).count(),
            ApplicabilityReason.objects.filter(
                credit__subcategory__category__creditset=cs).count())

        self.assertEqual(
            DocumentationField.objects.filter(
                credit__subcategory__category__creditset=new_cs).count(),
            DocumentationField.objects.filter(
                credit__subcategory__category__creditset=cs).count())

        self.assertEqual(
            Choice.objects.filter(
                documentation_field__credit__subcategory__category__creditset=new_cs).count(),
            Choice.objects.filter(
                documentation_field__credit__subcategory__category__creditset=cs).count())

        self.assertEqual(
            CreditTestSubmission.objects.filter(
                credit__subcategory__category__creditset=new_cs).count(),
            CreditTestSubmission.objects.filter(
                credit__subcategory__category__creditset=cs).count())
