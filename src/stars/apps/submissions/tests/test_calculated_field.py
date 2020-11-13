"""Tests for apps.submissions.models.DocumentationFieldSubmission that
maps to a DocumentationField of type "calculated".

"""
from django.test import TestCase

from stars.apps.credits.models import DocumentationField
from stars.apps.submissions.models import NumericSubmission
from stars.test_factories.models import (CreditFactory,
                                         CreditUserSubmissionFactory,
                                         DocumentationFieldFactory,
                                         NumericDocumentationFieldSubmissionFactory)


class CalculatedFieldTest(TestCase):

    def setUp(self):
        self.credit_user_submission = CreditUserSubmissionFactory()
        self.credit = self.credit_user_submission.credit

        numeric_field = DocumentationFieldFactory(credit=self.credit,
                                                  type="numeric",
                                                  identifier="A")
        self.calculated_field = DocumentationFieldFactory(
            credit=self.credit,
            type="calculated",
            formula="value = A")

        self.calculated_submission = (
            NumericDocumentationFieldSubmissionFactory(
                documentation_field=self.calculated_field,
                credit_submission=self.credit_user_submission,
                value=999))

        self.numeric_submission = NumericDocumentationFieldSubmissionFactory(
            documentation_field=numeric_field,
            credit_submission=self.credit_user_submission,
            value=0)

    def test_save_of_calculated_field(self):
        """Does saving a calculated field change its value?
        It shouldn't.
        """
        self.calculated_submission.save()
        fresh_calculated_submission = NumericSubmission.objects.get(
            id=self.calculated_submission.id)
        self.assertEqual(999, fresh_calculated_submission.value)

    def test_save_of_noncalculated_field(self):
        """Does saving a noncalculated field change a related calculated field?
        It should.
        """
        new_numeric_submission_value = self.numeric_submission.value + 10

        self.numeric_submission.value = new_numeric_submission_value
        self.numeric_submission.save()

        fresh_calculated_submission = NumericSubmission.objects.get(
            pk=self.calculated_submission.pk)

        self.assertEqual(new_numeric_submission_value,
                         fresh_calculated_submission.value)

    def test_calculated_field_is_calculated_when_term_changes(self):
        credit = CreditFactory()
        first_term_field = DocumentationFieldFactory(
            credit=credit,
            type='numeric',
            identifier='AA')
        second_term_field = DocumentationFieldFactory(
            credit=credit,
            type='numeric',
            identifier='AB')
        calculated_field = DocumentationField.objects.create(
            credit=credit,
            type='calculated',
            formula='value = (AA or 0) + (AB or 0)')
        credit_submission = CreditUserSubmissionFactory(
            credit=credit)
        first_term_submission = NumericDocumentationFieldSubmissionFactory(
            credit_submission=credit_submission,
            documentation_field=first_term_field,
            value=1)
        NumericDocumentationFieldSubmissionFactory(
            credit_submission=credit_submission,
            documentation_field=second_term_field,
            value=2)
        calculated_submission = NumericDocumentationFieldSubmissionFactory(
            credit_submission=credit_submission,
            documentation_field=calculated_field,
            value=None)

        first_term_submission.value = 10
        first_term_submission.save()

        # We have a dirty read.
        calculated_submission = NumericSubmission.objects.get(
            pk=calculated_submission.pk)

        self.assertEqual(12, calculated_submission.value)

    def test_calculated_field_is_cleared_when_term_goes_invalid(self):
        credit = CreditFactory()
        term_field = DocumentationFieldFactory(
            credit=credit,
            type='numeric',
            identifier='BA')
        calculated_field = DocumentationField.objects.create(
            credit=credit,
            type='calculated',
            formula='value = BA')
        credit_submission = CreditUserSubmissionFactory(
            credit=credit)
        term_submission = NumericDocumentationFieldSubmissionFactory(
            credit_submission=credit_submission,
            documentation_field=term_field,
            value=1)
        calculated_submission = NumericDocumentationFieldSubmissionFactory(
            credit_submission=credit_submission,
            documentation_field=calculated_field,
            value=100)

        term_submission.value = None
        term_submission.save()

        # We have a dirty read.
        calculated_submission = NumericSubmission.objects.get(
            pk=calculated_submission.pk)

        self.assertEqual(None, calculated_submission.value)

    def test_all_related_calculated_fields_recalculate(self):
        """Do all related calculated fields recalculate when self.value changes?
        """
        second_calculated_field = DocumentationFieldFactory(
            credit=self.credit,
            type="calculated",
            formula=self.calculated_field.formula)

        second_calculated_submission = (
            NumericDocumentationFieldSubmissionFactory(
                documentation_field=second_calculated_field,
                credit_submission=self.credit_user_submission,
                value=self.calculated_submission.value))

        self.numeric_submission.value += 100
        self.numeric_submission.save()

        fresh_calculated_submission = NumericSubmission.objects.get(
            pk=self.calculated_submission.pk)

        self.assertEqual(self.numeric_submission.value,
                         fresh_calculated_submission.value)

        fresh_second_calculated_submission = NumericSubmission.objects.get(
            pk=second_calculated_submission.pk)

        self.assertEqual(self.numeric_submission.value,
                         fresh_second_calculated_submission.value)

    def test_calculated_field_as_formula_term_recalculates(self):
        """Does a calculated field in a formula recalculate?"""
        # test that calculated fields acting as formula terms are calculated
        # appropriately -- CF1 is term in CF2, T1 is term in CF1, test that
        # update of T1.value causes value of CF2 to be recalculated.
        second_calculated_field = DocumentationFieldFactory(
            credit=self.credit,
            type="calculated",
            formula="value = {}".format(self.calculated_field.identifier))

        second_calculated_submission = (
            NumericDocumentationFieldSubmissionFactory(
                documentation_field=second_calculated_field,
                credit_submission=self.credit_user_submission,
                value=5000))

        # Updating self.numeric_submission.value should cause
        # self.calculated_submission to calculate, which should
        # cause second_calculated_submission to calculate.

        self.numeric_submission.value += 100

        self.numeric_submission.save()

        self.assertEqual(
            NumericSubmission.objects.get(
                pk=self.numeric_submission.pk).value,
            NumericSubmission.objects.get(
                pk=second_calculated_submission.pk).value)
