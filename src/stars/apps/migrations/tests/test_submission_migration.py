"""
    Submission Migration unit tests
"""
from django.test import TestCase

from stars.apps.credits.models import (Category,
                                       Credit,
                                       Subcategory,
                                       DocumentationField,
                                       Unit)
from stars.apps.migrations import utils
from stars.apps.submissions.models import (CreditUserSubmission,
                                           NumericSubmission)
from stars.test_factories.models import (CreditSetFactory,
                                         SubmissionSetFactory)


def make_two_creditsets():
    return (CreditSetFactory(release_date='1970-01-01'),
            CreditSetFactory(release_date='1971-10-07'))


class VersionMigrationTest(TestCase):

    def setUp(self):
        super(VersionMigrationTest, self).setUp()
        self.first_creditset, self.second_creditset = make_two_creditsets()
        self._submissionset = None

    @property
    def submissionset(self):
        if not self._submissionset:
            self._submissionset = SubmissionSetFactory(
                creditset=self.first_creditset)
        return self._submissionset

    def test_migrate_submission_sets_migrated_from(self):
        """Does migrate_submission() set SubmissionSet.migrated_from?"""

        new_submissionset = SubmissionSetFactory(
            institution=self.submissionset.institution,
            creditset=self.second_creditset)

        utils.migrate_submission(old_submissionset=self.submissionset,
                                 new_submissionset=new_submissionset)

        self.assertEqual(new_submissionset.migrated_from,
                         self.submissionset)


class MigrateSubmissionTestCase(TestCase):

    def get_creditset(self):
        creditset = CreditSetFactory()

        self.innovations_category = Category.objects.create(
            creditset=creditset,
            abbreviation="IN")
        self.innovations_subcategory = Subcategory.objects.create(
            category=self.innovations_category,
            title="Innovation")
        self.innovations_credit = Credit.objects.create(
            subcategory=self.innovations_subcategory,
            identifier="INNOVATION",
            point_value=10)

        self.us_unit = Unit(name='imperial units',
                            is_metric=False,
                            ratio=.5)  # 1 us is .5 metric
        self.us_unit.save()
        # metric value is twice the us unit
        self.metric_unit = Unit(name="metric units",
                                is_metric=True,
                                ratio=2,  # 1 metric is 2 us
                                equivalent=self.us_unit)
        self.metric_unit.save()
        self.us_unit.equivalent = self.metric_unit
        self.us_unit.save()
        self.innovations_documentation_field = (
            DocumentationField.objects.create(
                credit=self.innovations_credit,
                units=self.us_unit,
                type="numeric"))

        self.not_innovations_subcategory = Subcategory.objects.create(
            category=self.innovations_category,
            title="Not Innovation")
        self.not_innovations_credit = Credit.objects.create(
            subcategory=self.not_innovations_subcategory,
            identifier="NOT-INNOVATION",
            point_value=20)
        self.not_innovations_documentation_field = (
            DocumentationField.objects.create(
                credit=self.not_innovations_credit,
                type="numeric"))

        return creditset

    def get_submissionset(self, creditset, metric_preference=False):
        submissionset = SubmissionSetFactory(creditset=creditset)
        submissionset.institution.prefers_metric_system = metric_preference
        submissionset.institution.save()

        self.innovations_numeric_submission = NumericSubmission.objects.create(
            documentation_field=self.innovations_documentation_field,
            credit_submission=CreditUserSubmission.objects.get(
                subcategory_submission__subcategory__slug='innovation'),
            value=10, metric_value=5)

        self.not_innovations_numeric_submission = (
            NumericSubmission.objects.create(
                documentation_field=self.not_innovations_documentation_field,
                credit_submission=CreditUserSubmission.objects.get(
                    subcategory_submission__subcategory__slug='not-innovation'),
                value=20))

        return submissionset

    def test_innovations_credits_dont_migrate_for_rated_submission(self):
        """Do Innovation credits migrate from rated submissions?
        They shouldn't.
        """
        creditset = self.get_creditset()

        submissionset = self.get_submissionset(creditset=creditset)
        submissionset.status = "r"
        submissionset.save()

        new_submissionset = utils.new_submissionset_for_old_submissionset(
            old_submissionset=submissionset,
            new_creditset=submissionset.creditset)

        new_submissionset = utils.migrate_submission(
            old_submissionset=submissionset,
            new_submissionset=new_submissionset)

        new_credit_submissions = new_submissionset.get_credit_submissions()

        new_innovations_credit_submission = [
            cs for cs in new_credit_submissions
            if cs.credit.subcategory.slug == 'innovation'][0]
        self.assertEqual(
            0, new_innovations_credit_submission.numericsubmission_set.count())

        new_not_innovations_credit_submission = [
            cs for cs in new_credit_submissions
            if cs.credit.subcategory.slug == 'not-innovation'][0]
        self.assertEqual(
            1, new_not_innovations_credit_submission.numericsubmission_set.count())
        new_not_innovations_numericsubmission = (
            new_not_innovations_credit_submission.numericsubmission_set.all()[0])
        self.assertEqual(20, new_not_innovations_numericsubmission.value)

    def test_innovations_credits_migrate_if_specified(self):
        """
        Do Innovation credits migrate from rated submissions if told to?
        This test uses metric.
        """
        creditset = self.get_creditset()

        submissionset = self.get_submissionset(
            creditset=creditset, metric_preference=True)
        submissionset.status = "r"
        submissionset.save()

        new_submissionset = utils.new_submissionset_for_old_submissionset(
            old_submissionset=submissionset,
            new_creditset=submissionset.creditset)

        new_submissionset = utils.migrate_submission(
            old_submissionset=submissionset,
            new_submissionset=new_submissionset,
            keep_innovation=True)

        new_credit_submissions = new_submissionset.get_credit_submissions()

        new_innovations_credit_submission = [
            cs for cs in new_credit_submissions
            if cs.credit.subcategory.slug == 'innovation'][0]
        self.assertEqual(
            1, new_innovations_credit_submission.numericsubmission_set.count())
        new_innovations_numericsubmission = (
            new_innovations_credit_submission.numericsubmission_set.all()[0])
        self.assertEqual(10, new_innovations_numericsubmission.value)

        new_not_innovations_credit_submission = [
            cs for cs in new_credit_submissions
            if cs.credit.subcategory.slug == 'not-innovation'][0]
        self.assertEqual(
            1, new_not_innovations_credit_submission.numericsubmission_set.count())
        new_not_innovations_numericsubmission = (
            new_not_innovations_credit_submission.numericsubmission_set.all()[0])
        self.assertEqual(20, new_not_innovations_numericsubmission.value)

    def test_innovations_credits_migrate_if_submission_is_unrated(self):
        """Do Innovation credits migrate from unrated submissions?
        """
        creditset = self.get_creditset()

        submissionset = self.get_submissionset(creditset=creditset)
        submissionset.save()

        new_submissionset = utils.new_submissionset_for_old_submissionset(
            old_submissionset=submissionset,
            new_creditset=submissionset.creditset)

        new_submissionset = utils.migrate_submission(
            old_submissionset=submissionset,
            new_submissionset=new_submissionset)

        new_credit_submissions = new_submissionset.get_credit_submissions()

        new_innovations_credit_submission = [
            cs for cs in new_credit_submissions
            if cs.credit.subcategory.slug == 'innovation'][0]
        self.assertEqual(
            1, new_innovations_credit_submission.numericsubmission_set.count())
        new_innovations_numericsubmission = (
            new_innovations_credit_submission.numericsubmission_set.all()[0])
        self.assertEqual(10, new_innovations_numericsubmission.value)

        new_not_innovations_credit_submission = [
            cs for cs in new_credit_submissions
            if cs.credit.subcategory.slug == 'not-innovation'][0]
        self.assertEqual(
            1, new_not_innovations_credit_submission.numericsubmission_set.count())
        new_not_innovations_numericsubmission = (
            new_not_innovations_credit_submission.numericsubmission_set.all()[0])
        self.assertEqual(20, new_not_innovations_numericsubmission.value)
