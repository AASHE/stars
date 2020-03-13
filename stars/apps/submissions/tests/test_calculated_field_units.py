"""
    Tests for apps.submissions.models.DocumentationFieldSubmission that
    maps to a DocumentationField of type "calculated".

    stars.apps.submissions.tests.test_calculated_field_units
"""
from django.test import TestCase

from stars.apps.credits.models import DocumentationField, Unit
from stars.apps.submissions.models import NumericSubmission
from stars.test_factories.models import (CreditFactory,
                                         CreditUserSubmissionFactory,
                                         DocumentationFieldFactory,
                                         NumericDocumentationFieldSubmissionFactory)


class CalculatedFieldTest(TestCase):

    def setUp(self):

        self.us_units = Unit(is_metric=False, ratio=.25)
        self.us_units.save()
        self.metric_units = Unit(is_metric=True, ratio=4, equivalent=self.us_units)
        self.metric_units.save()
        self.us_units.equivalent = self.metric_units
        self.us_units.save()

        self.credit_user_submission = CreditUserSubmissionFactory()
        self.credit = self.credit_user_submission.credit

        fieldA = DocumentationFieldFactory(
            credit=self.credit,
            type="numeric",
            units=self.us_units,
            identifier="A")

        fieldB = DocumentationFieldFactory(
            credit=self.credit,
            type="numeric",
            units=self.us_units,
            identifier="B")

        self.calculated_field = DocumentationFieldFactory(
            credit=self.credit,
            type="calculated",
            units=self.us_units,
            formula="value = A + B")

        self.calculated_submission = (
            NumericDocumentationFieldSubmissionFactory(
                documentation_field=self.calculated_field,
                credit_submission=self.credit_user_submission,
                value=4,
                metric_value=1))

        self.fieldA_submission = NumericDocumentationFieldSubmissionFactory(
            documentation_field=fieldA,
            credit_submission=self.credit_user_submission,
            value=4,
            metric_value=1)

        self.fieldB_submission = NumericDocumentationFieldSubmissionFactory(
            documentation_field=fieldB,
            credit_submission=self.credit_user_submission,
            value=8,
            metric_value=2)

    def test_imperial_institution(self):
        institution = self.credit_user_submission.get_submissionset().institution
        institution.prefers_metric_system = False
        institution.save()

        self.fieldA_submission.value = 20
        self.fieldA_submission.save()
        self.fieldB_submission.value = 40
        self.fieldB_submission.save()

        calculated_submission = NumericSubmission.objects.get(
        pk=self.calculated_submission.pk)

        self.assertEqual(60, calculated_submission.value)
        self.assertEqual(15.0, calculated_submission.metric_value)

    def test_metric_institution(self):
        institution = self.credit_user_submission.get_submissionset().institution
        institution.prefers_metric_system = True
        institution.save()

        self.fieldA_submission.metric_value = 4
        self.fieldA_submission.save()
        self.fieldB_submission.metric_value = 5
        self.fieldB_submission.save()

        calculated_submission = NumericSubmission.objects.get(
            pk=self.calculated_submission.pk)
        self.assertEqual(9, calculated_submission.metric_value)
        self.assertEqual(36.0, calculated_submission.value)
