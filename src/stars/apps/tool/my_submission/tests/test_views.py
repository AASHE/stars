"""Tests for apps.tool.my_submission.views.
"""
from stars.apps.tool.my_submission import views
from stars.apps.tool.tests.views import (InstitutionToolMixinTest,
                                         UserCanEditSubmissionMixinTest)
from stars.test_factories.models import (CategoryFactory,
                                         CategorySubmissionFactory,
                                         CreditFactory,
                                         CreditUserSubmissionFactory,
                                         DocumentationFieldFactory,
                                         DocumentationFieldSubmissionFactory,
                                         InstitutionFactory,
                                         StarsAccountFactory,
                                         SubcategoryFactory,
                                         SubcategorySubmissionFactory,
                                         SubmissionSetFactory)

# @TODO - we definitely need tests here for all the form submission tools


class SubmissionSummaryViewTest(InstitutionToolMixinTest):

    view_class = views.SubmissionSummaryView
    blessed_user_level = 'submit'  # user_level that should be allowed to GET
    blocked_user_level = 'view'  # user_level that should be blocked

    def setUp(self):
        super(SubmissionSummaryViewTest, self).setUp()
        self.institution = InstitutionFactory()
        self.account = StarsAccountFactory(institution=self.institution)
        self.request.user = self.account.user
        self.submission = SubmissionSetFactory(institution=self.institution)

    def test_get_succeeds(self, **kwargs):
        super(InstitutionToolMixinTest, self).test_get_succeeds(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id))

    def test_get_is_blocked(self, **kwargs):
        super(InstitutionToolMixinTest, self).test_get_is_blocked(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id))

    def test_success_url_is_loadable(self, **kwargs):
        super(InstitutionToolMixinTest, self).test_success_url_is_loadable(
            institution_slug=self.institution.slug,
            submissionset=str(self.submission.id))


class EditBoundaryViewTest(UserCanEditSubmissionMixinTest):

    view_class = views.EditBoundaryView


class CreditSubmissionNotesViewTest(UserCanEditSubmissionMixinTest):

    view_class = views.CreditSubmissionNotesView


class CreditSubmissionHistoryViewTest(UserCanEditSubmissionMixinTest):

    view_class = views.CreditSubmissionHistoryView

    def setUp(self, *args, **kwargs):
        super(CreditSubmissionHistoryViewTest, self).setUp(*args, **kwargs)

        category = CategoryFactory(creditset=self.submission.creditset)
        category.save()
        category_submission = CategorySubmissionFactory(
            category=category,
            submissionset=self.submission)
        self.category_abbreviation = category.abbreviation

        subcategory = SubcategoryFactory(category=category)
        subcategory.save()
        subcategory_submission = SubcategorySubmissionFactory(
            subcategory=subcategory,
            category_submission=category_submission)
        self.subcategory_slug = subcategory.slug

        credit = CreditFactory(subcategory=subcategory)
        credit.save()
        credit_submission = CreditUserSubmissionFactory(
            credit=credit,
            subcategory_submission=subcategory_submission)
        self.credit_identifier = credit.identifier

        # Some history to show:
        documentation_field = DocumentationFieldFactory(
            credit=credit)
        documentation_field.save()
        documentation_field_submission = DocumentationFieldSubmissionFactory(
            documentation_field=documentation_field,
            credit_submission=credit_submission)

        documentation_field_submission.save()

    def test_get_succeeds(self, **kwargs):
        super(CreditSubmissionHistoryViewTest, self).test_get_succeeds(
            category_abbreviation=self.category_abbreviation,
            subcategory_slug=self.subcategory_slug,
            credit_identifier=self.credit_identifier)

    def test_get_is_blocked(self, **kwargs):
        super(CreditSubmissionHistoryViewTest, self).test_get_is_blocked(
            category_abbreviation=self.category_abbreviation,
            subcategory_slug=self.subcategory_slug,
            credit_identifier=self.credit_identifier)
