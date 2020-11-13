from django.test import TestCase

import django

from stars.apps import credits, institutions, submissions
from stars.test_factories import submissions_factories


class ResponsiblePartyFactoryTest(TestCase):

    def test_institution_is_produced(self):
        """Is an Institution created when a ResponsibleParty is produced?"""
        responsible_party = submissions_factories.ResponsiblePartyFactory()
        self.assertIsInstance(responsible_party.institution,
                              institutions.models.Institution)


class SubmissionSetFactoryTest(TestCase):

    def test_creditset_is_produced(self):
        """Is a CreditSet produced when a SubmissionSet is?"""
        submission_set = submissions_factories.SubmissionSetFactory()
        self.assertIsInstance(submission_set.creditset,
                              credits.models.CreditSet)

    def test_institution_is_produced(self):
        """Is an Institution created when a SubmissionSet is?"""
        submission_set = submissions_factories.SubmissionSetFactory()
        self.assertIsInstance(submission_set.institution,
                              institutions.models.Institution)

    def test_registering_user_is_produced(self):
        """Is an registering user created when a SubmissionSet is?"""
        submission_set = submissions_factories.SubmissionSetFactory()
        self.assertIsInstance(submission_set.registering_user,
                              django.contrib.auth.models.User)

    def test_submitting_user_is_produced(self):
        """Is an submitting user created when a SubmissionSet is?"""
        submission_set = submissions_factories.SubmissionSetFactory()
        self.assertIsInstance(submission_set.submitting_user,
                              django.contrib.auth.models.User)

    def test_rating_is_produced(self):
        """Is a Rating created when a SubmissionSet is?"""
        submission_set = submissions_factories.SubmissionSetFactory()
        self.assertIsInstance(submission_set.rating,
                              credits.models.Rating)

    def test_only_submisionset_is_set_to_current_submission(self):
        """Is the first SubmissionSet for an Inst set to current_submission?
        """
        submission_set = submissions_factories.SubmissionSetFactory()
        self.assertEqual(submission_set,
                         submission_set.institution.current_submission)

    def test_second_submissionset_is_not_set_to_current_submission(self):
        """Is the second SubmissionSet for an Inst set to current_submission?
        """
        first_submission_set = submissions_factories.SubmissionSetFactory()
        second_submission_set = submissions_factories.SubmissionSetFactory(
            institution=first_submission_set.institution)
        self.assertNotEqual(
            second_submission_set,
            second_submission_set.institution.current_submission)
        self.assertIsNotNone(
            second_submission_set.institution.current_submission)


class CategorySubmissionFactoryTest(TestCase):

    def test_submissionset_is_produced(self):
        """Is a SubmissionSet produced for a CategorySubmission?"""
        category_submission = submissions_factories.CategorySubmissionFactory()
        self.assertIsInstance(category_submission.submissionset,
                              submissions.models.SubmissionSet)

    def test_category_is_produced(self):
        """Is a Category produced for a CategorySubmission?"""
        category_submission = submissions_factories.CategorySubmissionFactory()
        self.assertIsInstance(category_submission.category,
                              credits.models.Category)


class SubcategorySubmissionFactoryTest(TestCase):

    def test_submissionset_is_produced(self):
        """Is a CategorySubmission produced for a SubcategorySubmission?"""
        subcategory_submission = (
            submissions_factories.SubcategorySubmissionFactory())
        self.assertIsInstance(subcategory_submission.category_submission,
                              submissions.models.CategorySubmission)

    def test_subcategory_is_produced(self):
        """Is a Subcategory produced for a SubcategorySubmission?"""
        subcategory_submission = (
            submissions_factories.SubcategorySubmissionFactory())
        self.assertIsInstance(subcategory_submission.subcategory,
                              credits.models.Subcategory)


class CreditUserSubmissionFactoryTest(TestCase):

    def test_credit_is_produced(self):
        """Is a Credit produced for a CreditUserSubmission?"""
        credit_user_submission = (
            submissions_factories.CreditUserSubmissionFactory())
        self.assertIsInstance(credit_user_submission.credit,
                              credits.models.Credit)

    def test_subcategory_submission_is_produced(self):
        """Is a SubcategorySubmission produced for a CreditUserSubmission?"""
        credit_user_submission = (
            submissions_factories.CreditUserSubmissionFactory())
        self.assertIsInstance(credit_user_submission.subcategory_submission,
                              submissions.models.SubcategorySubmission)

    def test_applicability_reason_is_produced(self):
        """Is an Applicability_eason produced for a CreditUserSubmission?"""
        credit_user_submission = (
            submissions_factories.CreditUserSubmissionFactory())
        self.assertIsInstance(credit_user_submission.applicability_reason,
                              credits.models.ApplicabilityReason)

    def test_user_is_produced(self):
        """Is a User produced for a CreditUserSubmission?"""
        credit_user_submission = (
            submissions_factories.CreditUserSubmissionFactory())
        self.assertIsInstance(credit_user_submission.user,
                              django.contrib.auth.models.User)

    def test_responsible_party_is_produced(self):
        """Is a Responsible_Party produced for a CreditUserSubmission?"""
        credit_user_submission = (
            submissions_factories.CreditUserSubmissionFactory())
        self.assertIsInstance(credit_user_submission.responsible_party,
                              submissions.models.ResponsibleParty)


class BoundaryFactoryTest(TestCase):

    def test_submissionset_is_produced(self):
        """Is a SubmissionSet produced for a Boundary?"""
        boundary = submissions_factories.BoundaryFactory()
        self.assertIsInstance(boundary.submissionset,
                              submissions.models.SubmissionSet)

    def test_climatezone_is_produced(self):
        """Is a ClimateZone produced for a Boundary?"""
        boundary = submissions_factories.BoundaryFactory()
        self.assertIsInstance(boundary.climate_region,
                              institutions.models.ClimateZone)
