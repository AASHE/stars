"""
    We keep getting ValueErrors like this:

    The NumericSubmission could not be changed because the data didn't validate.

    This test is designed to duplicate the issue so we can debug it.
"""
from django.test import TestCase
from django.test.client import Client


from stars.apps.tests.views import ViewTest
from stars.apps.tool.tests.views import InstitutionToolMixinTest

from stars.apps.tool.my_submission.views import CreditSubmissionDetailView
from stars.apps.submissions.models import CreditUserSubmission, ResponsibleParty

from stars.apps.registration.views import init_submissionset
from stars.test_factories import (SubmissionSetFactory,
                                  DocumentationFieldFactory,
                                  CreditFactory,
                                  InstitutionFactory,
                                  StarsAccountFactory,
                                  CreditUserSubmissionFactory,
                                  ResponsiblePartyFactory)


class ValueErrorTest(ViewTest):

    view_class = CreditSubmissionDetailView

    def setUp(self):
        super(ValueErrorTest, self).setUp()

        self.institution = InstitutionFactory()
        self.account = StarsAccountFactory(institution=self.institution,
            user_level='admin')
        self.request.user = self.account.user

        self.field = DocumentationFieldFactory(type='boolean')
        self.submission = init_submissionset(self.institution,
            self.account.user)

        self.field.credit.identifier = u"CR-1"
        self.field.credit.save()
        self.credit = self.field.credit

        self.subcategory = self.credit.subcategory
        self.subcategory.title = u"subcategory"
        self.subcategory.save()

        self.subcategory.category.abbreviation = "CAT"
        self.subcategory.category.save()
        self.category = self.subcategory.category

        self.rp = ResponsiblePartyFactory(institution=self.institution)

#         self.credit = CreditFactory()
#         self.cus = CreditUserSubmissionFactory(applicability_reason=None,
#             credit=self.credit)
#         self.submission = self.cus.get_submissionset()

        self.view_kwargs = {
                            "institution_slug": self.institution.slug,
                            "submissionset": str(self.submission.id),
                            "category_abbreviation": self.category.abbreviation,
                            "subcategory_slug": self.subcategory.slug,
                            "credit_identifier": self.credit.identifier,
                            }

    def testValueError(self):
        """
            Fill out a credit accurately, marking it as complete
            then change a field so it won't validate and save as complete
            again
        """
        cus = CreditUserSubmission.objects.all()[0]
        self.assertEqual(cus.submission_status, 'ns')

        rp = ResponsibleParty.objects.all()[0]

        self.request.method = "POST"
        self.request.POST = {
                                "BooleanSubmission_1-value": '2', # YES
                                "responsible_party": '%d' % self.rp.id,
                                "responsible_party_confirm": 'on',
                                "submission_status": 'c',
                             }
        response = self.view_class.as_view()(self.request, **self.view_kwargs)
        self.assertEqual(response.status_code, 302)

        cus = CreditUserSubmission.objects.all()[0]
        self.assertEqual(cus.submission_status, 'c')

        self.request.POST["BooleanSubmission_1-value"] = '1' # unknown

        response = self.view_class.as_view()(self.request, **self.view_kwargs)
        self.assertEqual(response.status_code, 200)

    def test_get_succeeds(self, status_code=200, **kwargs):
        super(ValueErrorTest, self).test_get_succeeds(status_code, **self.view_kwargs)

