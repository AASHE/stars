"""
    We keep getting AttributeError like this:

    'NumericSubmissionForm' object has no attribute 'cleaned_data'

    This test is designed to duplicate the issue so we can debug it.
"""
from stars.apps.test_utils.views import ViewTest

from stars.apps.tool.my_submission.views import (
    CreditSubmissionReportingFieldsView)
from stars.apps.submissions.models import (CreditUserSubmission,
                                           NumericSubmission)

from stars.apps.registration.views import init_submissionset
from stars.test_factories.models import (DocumentationFieldFactory,
                                         InstitutionFactory,
                                         StarsAccountFactory,
                                         ResponsiblePartyFactory)


class SRT87Test(ViewTest):

    view_class = CreditSubmissionReportingFieldsView

    def setUp(self):
        super(SRT87Test, self).setUp()

        # initialize the creditset and institution
        self.institution = InstitutionFactory()
        self.account = StarsAccountFactory(institution=self.institution,
                                           user_level='admin')
        self.request.user = self.account.user

        self.field = DocumentationFieldFactory(type='numeric',
                                               required=True,
                                               min_range=0)

        # Set up titles for the url
        self.field.credit.identifier = u"CR-1"
        self.field.credit.validation_rules = (
            "if A < 0: errors['B'] = 'you have errors'")
        self.field.credit.save()
        self.credit = self.field.credit

        self.subcategory = self.credit.subcategory
        self.subcategory.title = u"subcategory"
        self.subcategory.save()

        self.subcategory.category.abbreviation = "CAT"
        self.subcategory.category.save()
        self.category = self.subcategory.category

        tabular_field_dict = {
            "numRows": 1,
            "fields": [['']],
            "rowHeadings": ["Row 1"],
            "colHeadings": ["Col 1"],
            "numCols": 1}
        self.tabular_field = DocumentationFieldFactory(
            type='tabular',
            required=True,
            tabular_fields=tabular_field_dict,
            credit=self.credit)
        # create a submission set to work with
        self.submission = init_submissionset(self.institution,
                                             self.account.user)

        self.rp = ResponsiblePartyFactory(institution=self.institution)

        self.view_kwargs = {
            "institution_slug": self.institution.slug,
            "submissionset": str(self.submission.id),
            "category_abbreviation": self.category.abbreviation,
            "subcategory_slug": self.subcategory.slug,
            "credit_identifier": self.credit.identifier}

    def testValueError(self):
        """
            Fill out a credit once where it validates
            then where a required field won't validate due to numeric max_limit
            That field should also be in the "required fields" for the credit
        """
        cus = CreditUserSubmission.objects.all()[0]
        self.assertEqual(cus.submission_status, 'ns')

        self.request.method = "POST"
        self.request.POST = {"NumericSubmission_1-value": '1',
                             "responsible_party": '%d' % self.rp.id,
                             "responsible_party_confirm": 'on',
                             "submission_status": 'c'}
        response = self.view_class.as_view()(self.request, **self.view_kwargs)
        self.assertEqual(response.status_code, 302)

        cus = CreditUserSubmission.objects.all()[0]
        self.assertEqual(cus.submission_status, 'c')

        self.assertEqual(NumericSubmission.objects.all()[0].value, 1)

        # check the actual output
        self.request.method = "GET"
        response = self.view_class.as_view()(self.request, **self.view_kwargs)
        self.assertEqual(response.status_code, 200)

        self.request.method = "POST"
        self.request.POST["NumericSubmission_1-value"] = '-1'  # above range

        try:
            response = self.view_class.as_view()(self.request,
                                                 **self.view_kwargs)
            self.assertEqual(response.status_code, 200)
        except AttributeError:
            self.fail("Still issuing the AttributeError.")

    def test_get_succeeds(self, status_code=200, **kwargs):
        super(SRT87Test, self).test_get_succeeds(status_code,
                                                 **self.view_kwargs)
