# -*- coding: utf-8 -*-
import datetime

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from selenium.webdriver.support.ui import Select

from stars.apps.credits.models import CreditSet
from stars.apps.test_utils.live_server import StarsLiveServerTest
from stars.apps.institutions.data_displays.views import (
    Dashboard,
    ScoreFilter)
from stars.test_factories.models import (CategoryFactory,
                                         InstitutionFactory,
                                         RatingFactory,
                                         SubmissionSetFactory,
                                         SubscriptionFactory,
                                         UserFactory,
                                         MemberSuitePortalUserFactory)


class DashboardTestCase(TestCase):

    def setUp(self):
        # Need at least some history.
        SubscriptionFactory()

    def test_dashboard_loads(self):
        """Does the dashboard load?
        """
        client = Client()
        resp = client.get(reverse('institutions:data_displays:dashboard'))
        self.assertEqual(200, resp.status_code)

    def test_get_ratings_context(self):
        """Does get_ratings_context return a sensible context?
        """
        gold_rating = RatingFactory(name='gold')

        for factory in range(2):
            InstitutionFactory(
                current_rating=gold_rating,
                current_submission=SubmissionSetFactory(),
                rating_expires=datetime.date(2020, 1, 1))

        ratings_context = Dashboard().get_ratings_context()

        self.assertEqual(2, ratings_context['gold'])

    def test_get_participation_context_total_participant_count(self):
        """Does get_participation_context return right total participant count?
        """
        SubscriptionFactory(start_date=datetime.date(2015, 1, 1))
        participation_context = Dashboard().get_participation_context()
        # when data_displays is tested in isolation 'total_participant_count'
        # returns 2
        # when the full suite is run, it returns 6
        self.assertEqual(2, participation_context['total_participant_count'])

    def test_get_particpants_context_sorts_by_country(self):
        """Does get_participants_context sort its result by country?
        """
        InstitutionFactory(country='Bolivia')
        InstitutionFactory(country='Austrailia')
        InstitutionFactory(country='Denmark')
        InstitutionFactory(country='Columbia')
        participants_context = Dashboard().get_participants_context()
        participants = participants_context['participants']
        self.assertEqual(participants.pop()[0], 'Denmark')
        self.assertEqual(participants.pop()[0], 'Columbia')
        self.assertEqual(participants.pop()[0], 'Bolivia')
        self.assertEqual(participants.pop()[0], 'Austrailia')

    def test_get_context_data_cacheless(self):
        """Does get_context_data() work if the cache is empty?
        """
        cache.clear()
        context = Dashboard().get_context_data()
        self.assertEqual(context['display_version'], '2.0')


PASSWORD = 'password'


def member(user=None):
    """Return a User that will be identified as a member.
    """
    user = user or UserFactory(password=PASSWORD)
    MemberSuitePortalUserFactory(user=user, is_member=True)
    return user


def new_non_member():
    """Return a User that will NOT be identified as a member.
    """
    non_member = UserFactory(password=PASSWORD)
    MemberSuitePortalUserFactory(user=non_member, is_member=False)
    return non_member


GOTTA_BE_A_MEMBER_SENTINEL = 'This Data Display is only accessible to'
FILTERS_SHOW_SENTINEL = 'Select a filter'


def create_creditset(version):
    if version.startswith('1'):
        scoring_method = 'STARS 1.0 Scoring'
    else:
        scoring_method = 'STARS 2.0 Scoring'
    creditset = CreditSet.objects.create(
        version=version,
        release_date=datetime.date.today(),
        tier_2_points=0,
        scoring_method=scoring_method)
    return creditset


def create_creditsets():
    create_creditset('1.0')
    create_creditset('1.2')
    create_creditset('2.0')
    create_creditset('2.1')


class AggregateFilterTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.member = member()
        self.non_member = new_non_member()
        create_creditsets()

    def test_categories_data_display_loads(self):
        """Does the Category data display load?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('institutions:data_displays:categories_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(FILTERS_SHOW_SENTINEL, resp.content)

    def test_categories_data_display_members_only(self):
        """Is the Category data display held back from non-members?
        """
        self.client.login(username=self.non_member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('institutions:data_displays:categories_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(GOTTA_BE_A_MEMBER_SENTINEL, resp.content)

    def test_categories_data_display_v2_loads(self):
        """Does the Category data display load for version 2.0 data?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('institutions:data_displays:categories_data_display',
                                       kwargs={'cs_version': '2.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(FILTERS_SHOW_SENTINEL, resp.content)


class ScoreFilterTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.member = member()
        self.non_member = new_non_member()
        create_creditsets()

    def test_scores_data_display_loads(self):
        """Does the Scores data display load?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('institutions:data_displays:scores_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(FILTERS_SHOW_SENTINEL, resp.content)

    def test_scores_data_display_members_only(self):
        """Is the Scores data display held back from non-members?
        """
        self.client.login(username=self.non_member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('institutions:data_displays:scores_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(GOTTA_BE_A_MEMBER_SENTINEL, resp.content)

    def test_scores_data_display_v2_loads(self):
        """Does the Scores data display load for version 2.0 data?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('institutions:data_displays:scores_data_display',
                                       kwargs={'cs_version': '2.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(FILTERS_SHOW_SENTINEL, resp.content)

    def test_get_object_from_string_category(self):
        """Does get_object_from_string() return the Category it should?
        """
        category = CategoryFactory()
        result = ScoreFilter().get_object_from_string('cat_' +
                                                      str(category.pk))
        self.assertEqual(category, result)


class ContentFilterTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.member = member()
        self.non_member = new_non_member()
        create_creditsets()

    def test_content_data_display_loads(self):
        """Does the Content data display load?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('institutions:data_displays:content_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(FILTERS_SHOW_SENTINEL, resp.content)

    def test_content_data_display_members_only(self):
        """Is the Content data display held back from non-members?
        """
        self.client.login(username=self.non_member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('institutions:data_displays:content_data_display',
                                       kwargs={'cs_version': '1.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(GOTTA_BE_A_MEMBER_SENTINEL, resp.content)

    def test_content_data_display_v2_loads(self):
        """Does the Content data display load for version 2.0 data?
        """
        self.client.login(username=self.member.username,
                          password=PASSWORD)
        resp = self.client.get(reverse('institutions:data_displays:content_data_display',
                                       kwargs={'cs_version': '2.0'}))
        self.assertEqual(200, resp.status_code)
        self.assertIn(FILTERS_SHOW_SENTINEL, resp.content)


class DataDisplayLiveServerTest(StarsLiveServerTest):

    def setUp(self):
        super(DataDisplayLiveServerTest, self).setUp()
        self.selenium.implicitly_wait(30)
        create_creditsets()

    def filter_canada(self):
        """Set a filter to show only Canadian institutions.
        """
        Select(self.selenium.find_element_by_id(
            "filter_type")).select_by_visible_text("Country")
        Select(self.selenium.find_element_by_id(
            "filter_options")).select_by_visible_text("Canada")
        self.selenium.find_element_by_xpath(
            "//button[@type='button']").click()

    def go_to_dashboard(self):
        """Go to the Data Displays dashboard.
        """
        self.selenium.get(self.live_server_url)
        self.selenium.find_element_by_link_text(
            u"Explore the Data »").click()

    def test_can_add_category_filter(self):
        """Can we add a filter on the Category data display?
        """
        self.user = member(self.user)
        self.go_to_dashboard()
        self.selenium.find_element_by_link_text("Category Display").click()
        self.filter_canada()

    def test_can_add_score_filter(self):
        """Can we add a filter on the Score data display?
        """
        self.user = member(self.user)
        self.go_to_dashboard()
        self.selenium.find_element_by_link_text("Score Display").click()
        self.filter_canada()

    def test_can_add_content_filter(self):
        """Can we add a filter on the Content data display?
        """
        self.user = member(self.user)
        self.go_to_dashboard()
        self.selenium.find_element_by_link_text("Content Display").click()
        self.filter_canada()
