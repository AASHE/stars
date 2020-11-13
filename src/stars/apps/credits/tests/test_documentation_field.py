"""Tests for apps.credits.models.DocumentationField.
"""
from django.test import TestCase

from stars.apps.credits.models import DocumentationField
from stars.apps.submissions.models import NumericSubmission
from stars.test_factories.models import (CreditFactory,
                                         CreditTestSubmissionFactory,
                                         CreditUserSubmissionFactory,
                                         DocumentationFieldFactory,
                                         NumericDocumentationFieldSubmissionFactory)


def make_numeric_fields(credit, num):
    fields = []
    for i in xrange(num):
        fields.append(DocumentationFieldFactory(credit=credit,
                                                type='numeric'))
    return fields


class DocumentationFieldTestCase(TestCase):

    def setUp(self):
        self.credit = CreditFactory()

    def test_get_formula_terms_not_calculated_field(self):
        """Does get_formula_terms handle non-calculated fields?"""
        non_calculated_field = DocumentationFieldFactory(
            credit=self.credit)
        formula_terms = non_calculated_field.get_formula_terms()
        self.assertItemsEqual([], formula_terms)

    def test_get_formula_terms_calculated_field(self):
        """Does get_formula_terms handle calculated fields?"""
        calculated_field = DocumentationFieldFactory(
            credit=self.credit,
            type='calculated')
        calculated_field.formula = 'value = A + B + C / D * (E / F)'
        formula_terms = calculated_field.get_formula_terms()
        self.assertItemsEqual(['value', 'A', 'B', 'C', 'D', 'E', 'F'],
                              formula_terms)

    def test_get_formula_terms_unparseable_formula(self):
        """Does get_formula_terms handle an unparseable formula?"""
        calculated_field = DocumentationFieldFactory(
            credit=self.credit,
            type='calculated')
        calculated_field.formula = 'value = (bogus }['
        formula_terms = calculated_field.get_formula_terms()
        self.assertItemsEqual([], formula_terms)

    def test_get_formula_terms_empty_formula(self):
        """Does get_formula_terms handle an empty formula?"""
        calculated_field = DocumentationFieldFactory(
            credit=self.credit,
            type='calculated')
        calculated_field.formula = ''
        formula_terms = calculated_field.get_formula_terms()
        self.assertItemsEqual([], formula_terms)

    def test_get_fields_for_terms(self):
        """Does get_fields_for_terms work on a sunny day?"""
        calculated_field = DocumentationFieldFactory(
            credit=self.credit,
            type='calculated')
        fields_for_terms = make_numeric_fields(self.credit, 3)
        fields_for_terms_identifiers = [df.identifier for df in
                                        fields_for_terms]
        fields = calculated_field.get_fields_for_terms(
            fields_for_terms_identifiers)
        self.assertItemsEqual(fields_for_terms, fields)

    def test_get_fields_for_terms_empty_terms_list(self):
        """Does get_fields_for_terms work with an empty terms list?"""
        calculated_field = DocumentationFieldFactory(
            credit=self.credit,
            type='calculated')
        fields = calculated_field.get_fields_for_terms(terms_list=[])
        self.assertEqual(0, fields.count())

    def test_update_formula_terms_initially_empty_formula(self):
        """Does update_formula_terms work with an empty formula?"""
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='')
        self.assertEqual(0, calculated_field.formula_terms.count())

    def test_update_formula_terms_initially_valid_formula(self):
        """Does update_formula_terms work with a valid formula?"""
        fields = make_numeric_fields(self.credit, 2)
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='value = A - B')
        self.assertItemsEqual(
            fields,
            list(calculated_field.formula_terms.all()))

    def test_update_formula_terms_formerly_empty_formula(self):
        """Does update_formula_terms work when a formula clears?"""
        fields = make_numeric_fields(self.credit, 5)
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='')
        calculated_field.formula = 'value = E - D - C'
        calculated_field.update_formula_terms()
        self.assertItemsEqual(
            fields[-3:],
            list(calculated_field.formula_terms.all()))

    def test_update_formula_terms_empty_formerly_valid_formula(self):
        """Does update_formula_terms work when a formula goes invalid?"""
        make_numeric_fields(self.credit, 5)
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='value = A + B + C')
        calculated_field.formula = ''
        calculated_field.update_formula_terms()
        self.assertEqual(0,
                         calculated_field.formula_terms.count())

    def test_update_formula_terms_valid_formerly_valid_formula(self):
        """Does update_document_fields work when a formula changes?"""
        fields = make_numeric_fields(self.credit, 5)
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='value = A + B + C')
        calculated_field.formula = 'value = D - E'
        calculated_field.update_formula_terms()
        self.assertItemsEqual(
            fields[-2:],
            list(calculated_field.formula_terms.all()))

    def test_update_formula_terms_invalid_formerly_valid_formula(self):
        """Does update_formula_terms work if an invalid formula changes?"""
        make_numeric_fields(self.credit, 5)
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='value = A + B + C')
        calculated_field.formula = 'value = D E'
        calculated_field.update_formula_terms()
        self.assertEqual(0,
                         calculated_field.formula_terms.count())

    def test_save_formerly_empty_formula(self):
        """Does save work when an empty formula is filled in?"""
        fields = make_numeric_fields(self.credit, 5)
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='')
        calculated_field.formula = 'value = E - D - C'
        calculated_field.save()
        self.assertItemsEqual(
            fields[-3:],
            list(calculated_field.formula_terms.all()))

    def test_save_empty_formerly_valid_formula(self):
        """Does save work when a valid formula is cleared?"""
        make_numeric_fields(self.credit, 5)
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='value = A + B + C')
        calculated_field.formula = ''
        calculated_field.save()
        self.assertEqual(0,
                         calculated_field.formula_terms.count())

    def test_save_valid_formerly_valid_formula(self):
        """Does save work when a valid formula changes?"""
        fields = make_numeric_fields(self.credit, 5)
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='value = A + B + C')
        calculated_field.formula = 'value = D - E'
        calculated_field.save()
        self.assertItemsEqual(
            fields[-2:],
            list(calculated_field.formula_terms.all()))

    def test_save_invalid_formerly_valid_formula(self):
        """Does save work when a valid formula is changed to invalid?"""
        make_numeric_fields(self.credit, 5)
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='value = A + B + C')
        calculated_field.formula = 'value = D E'
        calculated_field.save()
        self.assertEqual(0,
                         calculated_field.formula_terms.count())

    def test_save_recalculates_credit_user_submissions(self):
        """Does save recalculate submissions when formula changes?"""
        credit_submission = CreditUserSubmissionFactory(credit=self.credit)
        fields = make_numeric_fields(self.credit, 3)
        field_submissions = []
        for i in xrange(len(fields)):
            field_submissions.append(
                NumericDocumentationFieldSubmissionFactory(
                    documentation_field=fields[i],
                    credit_submission=credit_submission,
                    value=i))
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='value = A + B + C')
        calculated_field_submission = (
            NumericDocumentationFieldSubmissionFactory(
                documentation_field=calculated_field,
                credit_submission=credit_submission))
        calculated_field_submission.calculate()
        self.assertEqual(3, calculated_field_submission.value)
        calculated_field.formula = 'value = C - B - A'
        calculated_field.save()
        # We have a dirty read.
        calculated_field_submission = NumericSubmission.objects.get(
            pk=calculated_field_submission.pk)
        self.assertEqual(1, calculated_field_submission.value)

    def test_save_recalculates_invalid_credit_user_submissions(self):
        """Does save recalculate submissions when formula goes invalid?"""
        credit_submission = CreditUserSubmissionFactory(credit=self.credit)
        fields = make_numeric_fields(self.credit, 3)
        field_submissions = []
        for i in xrange(len(fields)):
            field_submissions.append(
                NumericDocumentationFieldSubmissionFactory(
                    documentation_field=fields[i],
                    credit_submission=credit_submission,
                    value=i))
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='value = A + B + C')
        calculated_field_submission = (
            NumericDocumentationFieldSubmissionFactory(
                documentation_field=calculated_field,
                credit_submission=credit_submission))
        calculated_field_submission.calculate()
        self.assertEqual(3, calculated_field_submission.value)
        calculated_field.formula = 'value = bo-o-o-o-gus'
        calculated_field.save()
        # We have a dirty read.
        calculated_field_submission = NumericSubmission.objects.get(
            pk=calculated_field_submission.pk)
        self.assertEqual(None, calculated_field_submission.value)

    def test_save_recalculates_credit_test_submissions(self):
        """Does save recalculate submissions when formula changes?"""
        credit_submission = CreditTestSubmissionFactory(credit=self.credit)
        make_numeric_fields(self.credit, 3)
        # CreditSubmission.get_submission_fields() has a nasty side
        # effect -- it creates DocumentationFieldSubmissions for every
        # DocumentationField associated with CreditSubmission.Credit.
        # It's nasty because it gets called by the CreditSubmission's
        # __unicode__ method, which can get called anywhere, say, in
        # a log message, as it does if we try to just create a bunch
        # of NumericSubmissions for each DocumentationField, as we
        # do above, with CreditUserSubmission objects.  So we surrender.
        # Call the frickin' method here, and let it create the
        # NumericSubmissions.
        field_submissions = credit_submission.get_submission_fields()
        # Can't set the values of the DocumentationFieldSubmissions
        # created by get_submission_fields(), though, so we'll do that
        # here.
        for i in xrange(len(field_submissions)):
            field_submissions[i].value = i
            field_submissions[i].save()
        calculated_field = DocumentationField.objects.create(
            credit=self.credit,
            type='calculated',
            formula='value = A + B + C')
        calculated_field_submission = (
            NumericDocumentationFieldSubmissionFactory(
                documentation_field=calculated_field,
                credit_submission=credit_submission))
        calculated_field_submission.calculate()
        self.assertEqual(3, calculated_field_submission.value)
        calculated_field.formula = 'value = C - B - A'
        calculated_field.save()
        # We have a dirty read.
        calculated_field_submission = NumericSubmission.objects.get(
            pk=calculated_field_submission.pk)
        self.assertEqual(1, calculated_field_submission.value)
