from stars.apps.api.test import StarsApiTestCase
from stars.apps.credits.models import *
from stars.apps.submissions.models import *
from stars.apps.institutions.models import Institution


class FixturesTest(StarsApiTestCase):

    def testIncrementalFeatureLoad(self):
        self.assertTrue(IncrementalFeature.objects.all() > 0)

    def testRatingLoad(self):
        self.assertTrue(Rating.objects.all() > 0)

    def testInstitutionLoad(self):
        self.assertTrue(Institution.objects.all() > 0)

    def testCategoryLoad(self):
        self.assertTrue(Category.objects.all() > 0)

    def testSubcategoryLoad(self):
        self.assertTrue(Subcategory.objects.all() > 0)

    def testCreditLoad(self):
        self.assertTrue(Credit.objects.all() > 0)

    def testDocumentationFieldLoad(self):
        self.assertTrue(DocumentationField.objects.all() > 0)

    def testCategorySubmissionLoad(self):
        self.assertTrue(CategorySubmission.objects.all() > 0)

    def testSubcategorySubmissionLoad(self):
        self.assertTrue(SubcategorySubmission.objects.all() > 0)

    def testCreditSubmissionLoad(self):
        self.assertTrue(CreditSubmission.objects.all() > 0)

    def testDocumentationfieldSubmissionLoad(self):
        self.assertTrue(NumericSubmission.objects.all() > 0)

    def testCreditSetLoad(self):
        self.assertTrue(CreditSet.objects.all() > 0)

    def testSubmisisonSetLoad(self):
        self.assertTrue(SubmissionSet.objects.all() > 0)
