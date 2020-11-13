"""Tests for stars.apps.tool.my_submission.forms.
"""
from django.forms.widgets import HiddenInput
from django.test import TestCase
import testfixtures

from stars.apps.credits.models import DocumentationField, Unit
from stars.apps.submissions.models import CreditSubmission, TextSubmission
from stars.apps.tool.my_submission import forms
from stars.test_factories.models import NumericDocumentationFieldSubmissionFactory


class NumericSubmissionFormTest(TestCase):

    def setUp(self):
        self.numeric_submission = NumericDocumentationFieldSubmissionFactory()
        self.institution = self.numeric_submission.get_institution()
        self.us_units = Unit(is_metric=False,
                             ratio=.25)
        self.us_units.save()
        self.metric_units = Unit(is_metric=True,
                                 ratio=4,
                                 equivalent=self.us_units)
        self.metric_units.save()
        self.us_units.equivalent = self.metric_units
        self.us_units.save()

    def test_not_using_metric_is_value_saved_unchanged(self):
        """Not using metric; is `value` saved unchanged?
        """
        self.institution.prefers_metric_system = False
        self.institution.save()
        self.numeric_submission.documentation_field.units = self.us_units
        self.numeric_submission.documentation_field.save()
        form = forms.NumericSubmissionForm(
            data={'value': 100,
                  'metric_value': 0},
            instance=self.numeric_submission)
        form.is_valid()
        form.save()
        self.assertEqual(self.numeric_submission.value, 100)

    def test_not_using_metric_is_converted_value_saved(self):
        """Not using metric, is converted value saved to `metric_value`?
        """
        self.institution.prefers_metric_system = False
        self.institution.save()
        self.numeric_submission.documentation_field.units = self.us_units
        self.numeric_submission.documentation_field.save()
        form = forms.NumericSubmissionForm(
            data={'value': 100,
                  'metric_value': 0},
            instance=self.numeric_submission)
        form.is_valid()
        form.save()
        self.assertEqual(self.numeric_submission.metric_value, 25)

    def test_not_using_metric_is_metric_value_hidden(self):
        """Not using metric, is `metric_value` hidden?
        """
        self.institution.prefers_metric_system = False
        self.institution.save()
        self.numeric_submission.documentation_field.units = self.us_units
        self.numeric_submission.documentation_field.save()
        form = forms.NumericSubmissionForm(
            data={'value': 100,
                  'metric_value': 0},
            instance=self.numeric_submission)
        form.is_valid()
        self.assertIsInstance(form.fields['metric_value'].widget,
                              HiddenInput)

    def test_using_metric_is_metric_value_saved_unchanged(self):
        """Using metric, is `metric_value` saved unchanged?
        """
        self.institution.prefers_metric_system = True
        self.institution.save()
        self.numeric_submission.documentation_field.units = self.metric_units
        self.numeric_submission.documentation_field.save()
        form = forms.NumericSubmissionForm(
            data={'value': 0,
                  'metric_value': 25},
            instance=self.numeric_submission)
        form.is_valid()
        form.save()
        self.assertEqual(self.numeric_submission.metric_value, 25)

    def test_using_metric_is_converted_value_saved(self):
        """Using metric, is converted field value saved to `value`?
        """
        self.institution.prefers_metric_system = True
        self.institution.save()
        self.numeric_submission.documentation_field.units = self.metric_units
        self.numeric_submission.documentation_field.save()
        form = forms.NumericSubmissionForm(
            data={'value': 0,
                  'metric_value': 25},
            instance=self.numeric_submission)
        form.is_valid()
        form.save()
        self.assertEqual(self.numeric_submission.value, 100)

    def test_using_metric_is_value_hidden(self):
        """Using metric, is `value` field hidden?
        """
        self.institution.prefers_metric_system = True
        self.institution.save()
        self.numeric_submission.documentation_field.units = self.us_units
        self.numeric_submission.documentation_field.save()
        form = forms.NumericSubmissionForm(
            data={'value': 100,
                  'metric_value': 0},
            instance=self.numeric_submission)
        form.is_valid()
        self.assertIsInstance(form.fields['value'].widget,
                              HiddenInput)


class TextSubmissionFormTest(TestCase):

    def test_clean_value_logging(self):
        """Does clean_value log a message if there's no self(.instance)?
        """
        text_submission = TextSubmission()
        text_submission.documentation_field = DocumentationField()
        text_submission.credit_submission = CreditSubmission()

        text_submission_form = forms.TextSubmissionForm(
            instance=text_submission)
        text_submission_form.cleaned_data = {'value': None}
        text_submission_form.instance = None

        with testfixtures.LogCapture('stars') as log:
            text_submission_form.clean_value()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'INFO')
        self.assertTrue('No Instance' in log.records[0].msg)


class LongTextSubmissionFormTest(TestCase):

    def test_clean_value_logging(self):
        """Does clean_value log a message if there's no self(.instance)?
        """
        long_text_submission_form = forms.LongTextSubmissionForm()
        long_text_submission_form.cleaned_data = {'value': None}
        long_text_submission_form.instance = None

        with testfixtures.LogCapture('stars') as log:
            long_text_submission_form.clean_value()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'INFO')
        self.assertTrue('No Instance' in log.records[0].msg)
