from django.test import TestCase
from datetime import date, timedelta

from stars.test_factories.models import (
    CategoryFactory, CreditSetFactory, CreditFactory, NumericSubmissionFactory,
    DocumentationFieldFactory, SubcategoryFactory, SubmissionSetFactory,
    UnitFactory)

from stars.apps.credits.models import Category, Subcategory
from stars.apps.migrations.utils import migrate_creditset, create_ss_mirror
from stars.apps.submissions.models import (
    CreditSubmission, CreditUserSubmission,
    NumericSubmission, SubcategorySubmission)

from ..submissionvalues import (
    get_cat_etl_obj, get_sub_etl_obj, get_credit_etl_obj, get_df_etl_obj)


class SubmissionValuesTestCase(TestCase):

    def setUp(self):

        # create an initial creditset and submission
        self.cs1 = CreditSetFactory(
            version="2.0",
            release_date=date.today() - timedelta(days=2))
        self.cat1 = CategoryFactory(creditset=self.cs1)
        self.sub1 = SubcategoryFactory(category=self.cat1)
        self.cred1 = CreditFactory(subcategory=self.sub1)
        self.df1 = DocumentationFieldFactory(
            credit=self.cred1, type='numeric', title="doc field 1")
        self.ss1 = SubmissionSetFactory(creditset=self.cs1)

        self.m_unit = UnitFactory(
            name="met",
            equivalent=self.df1.units,
            is_metric=True
        )
        self.df1.units.name = "imp"
        self.df1.units.equivalent = self.m_unit
        self.df1.units.save()

        # SubmissionSetFactory doesn't seem to create a numeric submission
        # self.assertEqual(NumericSubmission.objects.count(), 1)  # fails
        self.ns1 = NumericSubmissionFactory(
            documentation_field=self.df1,
            credit_submission=CreditSubmission.objects.all()[0]
        )

        # Now created a migrated version of both
        self.cs2 = migrate_creditset(
            self.cs1, '2.1', date.today() - timedelta(days=1))
        self.ss2 = create_ss_mirror(
            self.ss1, new_creditset=self.cs2)

        # create some old one that won't have versions with others
        # create an initial creditset and submission
        self.cs0 = CreditSetFactory(
            version="1.2",
            release_date=date.today() - timedelta(days=3))
        self.cat0 = CategoryFactory(creditset=self.cs0)
        self.sub0 = SubcategoryFactory(category=self.cat0)
        self.cred0 = CreditFactory(subcategory=self.sub0)
        self.df0 = DocumentationFieldFactory(
            credit=self.cred0, type='numeric', title="doc field 1")
        self.ss0 = SubmissionSetFactory(creditset=self.cs0)
        self.ns0 = NumericSubmissionFactory(
            documentation_field=self.df0,
            credit_submission=CreditSubmission.objects.all()[2]
        )

        self.setUpScores()

    def tearDown(self):
        self.cs1.delete()
        self.cs2.delete()
        self.cs0.delete()

    def setUpScores(self):

        # these need to be rated.
        self.ss1.status = self.ss2.status = 'r'
        self.ss1.save()
        self.ss2.rating = self.ss1.rating
        self.ss2.save()

        self.ss1.institution.rated_submission = self.ss2
        self.ss1.institution.save()

        # Set up subcategories
        self.subsub1 = SubcategorySubmission.objects.all()[0]
        self.subsub2 = SubcategorySubmission.objects.all()[1]

        self.assertEqual(
            self.subsub1.category_submission.submissionset, self.ss1)
        self.assertEqual(
            self.subsub2.category_submission.submissionset, self.ss2)

        self.subsub1.points = 10
        self.subsub1.adjusted_available_points = 20
        self.subsub1.percentage_score = .5
        self.subsub1.save()

        self.subsub2.points = 12
        self.subsub2.adjusted_available_points = 15
        self.subsub2.percentage_score = .8
        self.subsub2.save()

        # set up credits
        self.credsub1 = CreditSubmission.objects.all()[0]
        self.credsub2 = CreditSubmission.objects.all()[1]
        self.cus1 = self.credsub1.creditusersubmission
        self.cus2 = self.credsub2.creditusersubmission

        self.assertEqual(self.cus1.get_submissionset(), self.ss1)
        self.assertEqual(self.cus2.get_submissionset(), self.ss2)

        self.cus1.available_point_cache = 20
        self.cus1.assessed_points = 10
        self.cus1.save(calculate_points=False)

        self.cus2.available_point_cache = 15
        self.cus2.assessed_points = 12
        self.cus2.save(calculate_points=False)

        # finally the documentation fields
        self.ns2 = NumericSubmission.objects.all()[1]
        self.df2 = self.ns2.documentation_field
        self.df2.title = "doc field 2"
        self.df2.save()
        self.ns2.value = 4
        self.ns2.metric_value = 8
        self.ns2.save()
        self.ns1.value = 5
        self.ns1.metric_value = 8
        self.ns1.save()

    def testCategoryETLObj(self):

        # more readable titles
        self.cat1.title = "Category 1 v2.0"
        self.cat1.save()
        self.cat2 = self.cs2.category_set.all()[0]
        self.cat2.title = "Category 1 v2.1"
        self.cat2.save()

        # Test using the latest category and the latest submissionset
        etl_obj = get_cat_etl_obj(self.cat2, self.ss2)
        f = etl_obj['fields']

        self.assertEqual(etl_obj['model'], 'stars_content.submissionvalue')
        self.assertEqual(f['data_point_key'], "cat_%d" % self.cat2.id)
        self.assertEqual(f['report_version'], self.ss2.creditset.version)
        self.assertTrue(self.cat2.title in f['title'])
        self.assertEqual(f['imperial_units'], '%')
        self.assertEqual(f['metric_units'], '%')
        self.assertEqual(f['imperial_value'], 80)
        self.assertEqual(f['metric_value'], 80)
        self.assertTrue(f['is_current'])
        self.assertTrue(f['is_latest'])

        # Test using the latest category and an older submissionset
        etl_obj = get_cat_etl_obj(self.cat2, self.ss1)
        f = etl_obj['fields']

        self.assertEqual(etl_obj['model'], 'stars_content.submissionvalue')
        self.assertEqual(f['data_point_key'], "cat_%d" % self.cat2.id)
        self.assertEqual(f['report_version'], self.ss1.creditset.version)
        self.assertTrue(self.cat2.title in f['title'])
        self.assertEqual(f['imperial_units'], '%')
        self.assertEqual(f['metric_units'], '%')
        self.assertEqual(f['imperial_value'], 50)
        self.assertEqual(f['metric_value'], 50)
        self.assertFalse(f['is_current'])
        self.assertFalse(f['is_latest'])

        # will it work with an older cat and newer submissionset?
        etl_obj = get_cat_etl_obj(self.cat1, self.ss2)
        f = etl_obj['fields']

        self.assertEqual(etl_obj['model'], 'stars_content.submissionvalue')
        self.assertEqual(f['data_point_key'], "cat_%d" % self.cat2.id)
        self.assertEqual(f['report_version'], self.ss2.creditset.version)
        self.assertTrue(self.cat1.title in f['title'])
        self.assertEqual(f['imperial_units'], '%')
        self.assertEqual(f['metric_units'], '%')
        self.assertEqual(f['imperial_value'], 80)
        self.assertEqual(f['metric_value'], 80)
        self.assertTrue(f['is_current'])
        self.assertTrue(f['is_latest'])

        # should be none for unlinked version
        etl_obj = get_cat_etl_obj(self.cat2, self.ss0)
        self.assertEqual(etl_obj, None)

    def testSubcategoryETLObj(self):

        # more readable titles
        self.sub1.title = "Subategory 1 v2.0"
        self.sub1.save()
        self.sub2 = Subcategory.objects.all()[1]
        self.sub2.title = "Subcategory 1 v2.1"
        self.sub2.save()

        # Test using the latest subcategory and the latest submissionset
        etl_obj = get_sub_etl_obj(self.sub2, self.ss2)
        f = etl_obj['fields']

        self.assertEqual(etl_obj['model'], 'stars_content.submissionvalue')
        self.assertEqual(f['data_point_key'], "sub_%d" % self.sub2.id)
        self.assertEqual(f['report_version'], self.ss2.creditset.version)
        self.assertTrue(self.sub2.title in f['title'])
        self.assertEqual(f['imperial_units'], '%')
        self.assertEqual(f['metric_units'], '%')
        self.assertEqual(f['imperial_value'], 80)
        self.assertEqual(f['metric_value'], 80)
        self.assertTrue(f['is_current'])
        self.assertTrue(f['is_latest'])

        # Test using the latest subcategory and an older submissionset
        etl_obj = get_sub_etl_obj(self.sub2, self.ss1)
        f = etl_obj['fields']

        self.assertEqual(etl_obj['model'], 'stars_content.submissionvalue')
        self.assertEqual(f['data_point_key'], "sub_%d" % self.sub2.id)
        self.assertEqual(f['report_version'], self.ss1.creditset.version)
        self.assertTrue(self.sub2.title in f['title'])
        self.assertEqual(f['imperial_units'], '%')
        self.assertEqual(f['metric_units'], '%')
        self.assertEqual(f['imperial_value'], 50)
        self.assertEqual(f['metric_value'], 50)
        self.assertFalse(f['is_current'])
        self.assertFalse(f['is_latest'])

        # will it work with an older subcategory and newer submissionset?
        etl_obj = get_sub_etl_obj(self.sub1, self.ss2)
        f = etl_obj['fields']

        self.assertEqual(etl_obj['model'], 'stars_content.submissionvalue')
        self.assertEqual(f['data_point_key'], "sub_%d" % self.sub2.id)
        self.assertEqual(f['report_version'], self.ss2.creditset.version)
        self.assertTrue(self.sub1.title in f['title'])
        self.assertEqual(f['imperial_units'], '%')
        self.assertEqual(f['metric_units'], '%')
        self.assertEqual(f['imperial_value'], 80)
        self.assertEqual(f['metric_value'], 80)
        self.assertTrue(f['is_current'])
        self.assertTrue(f['is_latest'])

        # should be none for unlinked version
        etl_obj = get_sub_etl_obj(self.sub2, self.ss0)
        self.assertEqual(etl_obj, None)

    def testCreditETLObj(self):

        cred1 = self.cus1.credit
        cred2 = self.cus2.credit
        # Test using the latest credit and the latest submissionset
        etl_obj = get_cat_etl_obj(cred2, self.ss2)
        f = etl_obj['fields']

        self.assertEqual(etl_obj['model'], 'stars_content.submissionvalue')
        self.assertEqual(f['data_point_key'], "cred_%d" % cred2.id)
        self.assertEqual(f['report_version'], self.ss2.creditset.version)
        self.assertTrue(cred2.title in f['title'])
        self.assertEqual(f['imperial_units'], '%')
        self.assertEqual(f['metric_units'], '%')
        v = 100 * float(self.cus2.assessed_points) / \
            self.cus2.get_available_points(use_cache=True)
        self.assertEqual(f['imperial_value'], v)
        self.assertEqual(f['metric_value'], v)
        self.assertTrue(f['is_current'])
        self.assertTrue(f['is_latest'])

        # Test using the latest subcategory and an older submissionset
        etl_obj = get_cat_etl_obj(cred2, self.ss1)
        f = etl_obj['fields']

        self.assertEqual(etl_obj['model'], 'stars_content.submissionvalue')
        self.assertEqual(f['data_point_key'], "cred_%d" % cred2.id)
        self.assertEqual(f['report_version'], self.ss1.creditset.version)
        self.assertTrue(cred2.title in f['title'])
        self.assertEqual(f['imperial_units'], '%')
        self.assertEqual(f['metric_units'], '%')
        v = 100 * float(self.cus1.assessed_points) / \
            self.cus1.get_available_points(use_cache=True)
        self.assertEqual(f['imperial_value'], v)
        self.assertEqual(f['metric_value'], v)
        self.assertFalse(f['is_current'])
        self.assertFalse(f['is_latest'])

        # will it work with an older subcategory and newer submissionset?
        etl_obj = get_cat_etl_obj(cred1, self.ss2)
        f = etl_obj['fields']

        self.assertEqual(etl_obj['model'], 'stars_content.submissionvalue')
        self.assertEqual(f['data_point_key'], "cred_%d" % cred2.id)
        self.assertEqual(f['report_version'], self.ss2.creditset.version)
        self.assertTrue(cred1.title in f['title'])
        self.assertEqual(f['imperial_units'], '%')
        self.assertEqual(f['metric_units'], '%')
        v = 100 * float(self.cus2.assessed_points) / \
            self.cus2.get_available_points(use_cache=True)
        self.assertEqual(f['imperial_value'], v)
        self.assertEqual(f['metric_value'], v)
        self.assertTrue(f['is_current'])
        self.assertTrue(f['is_latest'])

        # should be none for unlinked version
        etl_obj = get_cat_etl_obj(cred2, self.ss0)
        self.assertEqual(etl_obj, None)

    def testFieldETLObj(self):

        # Test using the latest credit and the latest submissionset
        etl_obj = get_df_etl_obj(self.df2, self.ss2)
        f = etl_obj['fields']

        self.assertEqual(etl_obj['model'], 'stars_content.submissionvalue')
        self.assertEqual(f['data_point_key'], "field_%d" % self.df2.id)
        self.assertEqual(f['report_version'], self.ss2.creditset.version)
        self.assertTrue(self.df2.title in f['title'])
        self.assertEqual(f['imperial_units'], 'imp')
        self.assertEqual(f['imperial_value'], self.ns2.value)
        self.assertEqual(f['metric_units'], 'met')
        self.assertEqual(f['metric_value'], self.ns2.metric_value)
        self.assertTrue(f['is_current'])
        self.assertTrue(f['is_latest'])

        # Test using the latest field and an older submissionset
        etl_obj = get_df_etl_obj(self.df2, self.ss1)
        f = etl_obj['fields']

        self.assertEqual(etl_obj['model'], 'stars_content.submissionvalue')
        self.assertEqual(f['data_point_key'], "field_%d" % self.df2.id)
        self.assertEqual(f['report_version'], self.ss1.creditset.version)
        self.assertTrue(self.df2.title in f['title'])
        self.assertEqual(f['imperial_units'], 'imp')
        self.assertEqual(f['imperial_value'], self.ns1.value)
        self.assertEqual(f['metric_units'], 'met')
        self.assertEqual(f['metric_value'], self.ns1.metric_value)
        self.assertFalse(f['is_current'])
        self.assertFalse(f['is_latest'])

        # will it work with an older field and newer submissionset?
        etl_obj = get_df_etl_obj(self.df1, self.ss2)
        f = etl_obj['fields']

        self.assertEqual(etl_obj['model'], 'stars_content.submissionvalue')
        self.assertEqual(f['data_point_key'], "field_%d" % self.df2.id)
        self.assertEqual(f['report_version'], self.ss2.creditset.version)
        self.assertTrue(self.df1.title in f['title'])
        self.assertEqual(f['imperial_units'], 'imp')
        self.assertEqual(f['imperial_value'], self.ns2.value)
        self.assertEqual(f['metric_units'], 'met')
        self.assertEqual(f['metric_value'], self.ns2.metric_value)
        self.assertTrue(f['is_current'])
        self.assertTrue(f['is_latest'])

        # should be none for unlinked version
        etl_obj = get_df_etl_obj(self.df2, self.ss0)
        self.assertEqual(etl_obj, None)
