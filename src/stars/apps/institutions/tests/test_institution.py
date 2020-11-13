"""Tests for apps.institutions.models.Institution.
"""
import datetime
from django.test import TestCase

import testfixtures

from stars.apps.institutions.models import (Institution,
                                            Subscription)
from stars.apps.submissions.models import REVIEW_SUBMISSION_STATUS
from stars.test_factories.models import (InstitutionFactory,
                                         RatingFactory,
                                         SubmissionSetFactory)


class InstitutionTest(TestCase):

    def test_update_from_iss_logging(self):
        """Does update_from_iss log a warning if there's no ISS instituion?
        """
        institution = Institution()
        institution.name = 'bob'

        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace('stars.apps.institutions.models.Institution.profile',
                          None)
                institution.update_from_iss()

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'WARNING')
        self.assertTrue('No ISS institution found bob' in log.records[0].msg)

    def test_set_slug_from_iss_institution_logging(self):
        """Does set_slug_from_iss_institution log exceptions (as errors)?
        """
        institution = Institution()

        def raiser(*args):
            raise Exception('bo-o-o-gus exception')

        with testfixtures.LogCapture('stars') as log:
            with testfixtures.Replacer() as r:
                r.replace('stars.apps.institutions.models.Institution.profile',
                          MockProfile())
                r.replace('stars.apps.institutions.models.slugify',
                          raiser)
                institution.set_slug_from_iss_institution(-99999)

        self.assertEqual(len(log.records), 1)
        self.assertEqual(log.records[0].levelname, 'ERROR')
        self.assertTrue('set slug for' in log.records[0].msg)

    def test_get_location_string_no_city(self):
        """Does get_location_string() work when there's no city?"""
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Institution.profile',
                      MockProfile(city='', state='ST', country_iso='CO'))
            institution = InstitutionFactory()
            self.assertEqual(institution.get_location_string(),
                             'ST, CO')

    def test_get_location_string_no_state(self):
        """Does get_location_string() work when there's no state?"""
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Institution.profile',
                      MockProfile(city='CITY', state='', country_iso='CO'))
            institution = InstitutionFactory()
            self.assertEqual(institution.get_location_string(),
                             'CITY, CO')

    def test_get_location_string_no_country(self):
        """Does get_location_string() work when there's no country?"""
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Institution.profile',
                      MockProfile(city='CITY', state='ST', country_iso=''))
            institution = InstitutionFactory()
            self.assertEqual(institution.get_location_string(),
                             'CITY, ST')

    def test_get_location_string_no_city_no_country(self):
        """Does get_location_string() work when there's no city or country?"""
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Institution.profile',
                      MockProfile(city='', state='ST', country_iso=''))
            institution = InstitutionFactory()
            self.assertEqual(institution.get_location_string(),
                             'ST')

    def test_get_location_string_no_nothing(self):
        """Does get_location_string() work if there's no city, state or country?
        """
        with testfixtures.Replacer() as r:
            r.replace('stars.apps.institutions.models.Institution.profile',
                      MockProfile(city='', state='', country_iso=''))
            institution = InstitutionFactory()
            self.assertEqual(institution.get_location_string(),
                             '')

    def test_is_participant_in_review_mode(self):
        """When a submission is in review mode, is is_particpant True?
        """
        institution = InstitutionFactory()
        self.assertFalse(institution.is_participant)
        institution.current_submission = SubmissionSetFactory(
            status=REVIEW_SUBMISSION_STATUS)
        institution.save()
        self.assertTrue(institution.is_participant)

    def test_access_level_in_review_mode(self):
        """When a submission is in review mode, is access_level correct?
        """
        institution = InstitutionFactory()
        self.assertEqual(institution.access_level, Subscription.BASIC_ACCESS)
        institution.current_submission = SubmissionSetFactory(
            status=REVIEW_SUBMISSION_STATUS)
        institution.save()
        self.assertEqual(institution.access_level, Subscription.FULL_ACCESS)

    def test_get_relative_rating_no_reporter(self):
        """Is get_relative_rating correct when there's no reporter rating?
        """
        good_rating = RatingFactory(name="Good", publish_score=True)
        submission = SubmissionSetFactory(
            rating=good_rating)
        submission.institution.current_rating = good_rating
        submission.institution.save()
        relative_rating = submission.institution.get_relative_rating()
        self.assertEqual(relative_rating, good_rating)

    def test_get_relative_rating_just_reporter(self):
        """Is get_relative_rating correct when there's only a reporter rating?
        """
        reporter_rating = RatingFactory(name="Reporter", publish_score=True)
        submission = SubmissionSetFactory(rating=reporter_rating)
        submission.institution.current_rating = reporter_rating
        submission.institution.save()
        relative_rating = submission.institution.get_relative_rating()
        self.assertEqual(relative_rating, reporter_rating)

    def test_get_relative_rating_with_reporter(self):
        """Is get_relative_rating correct when there's no reporter rating?
        """
        good_rating = RatingFactory(name="Good", publish_score=True)
        reporter_rating = RatingFactory(name="Reporter", publish_score=True)
        # A Good submission from 5 days ago:
        good_submission = SubmissionSetFactory(
            rating=good_rating,
            date_submitted=datetime.date.today() - datetime.timedelta(5))
        # And a Reporter submission from today:
        reporter_submission = SubmissionSetFactory(
            institution=good_submission.institution,
            rating=reporter_rating,
            date_submitted=datetime.date.today())

        reporter_submission.institution.current_rating = reporter_rating
        reporter_submission.institution.save()

        relative_rating = good_submission.institution.get_relative_rating()
        self.assertEqual(relative_rating, good_rating)

    def test_get_relative_rating_sorting(self):
        """Does get_ralative_rating choose the correct 1 when there are many?
        """
        good_rating = RatingFactory(name="Good", publish_score=True)
        reporter_rating = RatingFactory(name="Reporter", publish_score=True)
        bad_rating = RatingFactory(name="Bad", publish_score=True)
        # A Good submission from 5 days ago:
        good_submission = SubmissionSetFactory(
            rating=good_rating,
            date_submitted=datetime.date.today() - datetime.timedelta(5))
        # A Bad submission from yesterday:
        SubmissionSetFactory(
            institution=good_submission.institution,
            rating=bad_rating,
            date_submitted=datetime.date.today() - datetime.timedelta(1))
        # And a Reporter submission from today:
        reporter_submission = SubmissionSetFactory(
            institution=good_submission.institution,
            rating=reporter_rating,
            date_submitted=datetime.date.today())

        reporter_submission.institution.current_rating = reporter_rating
        reporter_submission.institution.save()

        relative_rating = good_submission.institution.get_relative_rating()
        self.assertEqual(relative_rating, bad_rating)


class MockProfile(object):

    def __init__(self, state='', city='', country_iso=''):
        self.org_name = 'MockProfile Org Name'
        self.state = state
        self.city = city
        self.country_iso = country_iso
