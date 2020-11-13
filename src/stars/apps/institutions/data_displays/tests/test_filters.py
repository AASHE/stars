from django.test import TestCase

from stars.apps.institutions.data_displays.filters import Filter
from stars.test_factories.models import InstitutionFactory, CreditSetFactory, SubmissionSetFactory
from stars.apps.submissions.models import SubmissionSet


class FilterTestCase(TestCase):

    def setUp(self):
        self.institution_one = InstitutionFactory(name='First One')
        self.institution_two = InstitutionFactory(name='Second One')
        self.institution_three = InstitutionFactory(name='AASHE Test')
        creditset = CreditSetFactory()
        self.submission_one = SubmissionSetFactory(
            institution=self.institution_one,
            creditset=creditset)
        self.submission_two = SubmissionSetFactory(
            institution=self.institution_two,
            creditset=creditset)
        self.submission_three = SubmissionSetFactory(
            institution=self.institution_three,
            creditset=creditset)

        self.filter = Filter(key='institution',
                             title='Name',
                             item_list=(('Yes', 'True'),
                                        ('No', 'False')),
                             base_qs=SubmissionSet.objects.all())

    def test_get_active_title_when_key_rating_name(self):
        """Does get_active_title work when key == 'rating_name'?
        """
        filter = Filter(key='rating__name',
                        title='Rating Name',
                        item_list=None,
                        base_qs=None)
        self.assertEqual('True Rated Institutions',
                         filter.get_active_title(item='True'))

    def test_get_active_title_when_key_not_rating_name(self):
        """Does get_active_title work when key != 'rating_name'?
        """
        self.assertEqual(True,
                         self.filter.get_active_title(item='True'))

    def test_get_select_list(self):
        self.assertEqual(
            self.filter.item_list,
            self.filter.get_select_list())

    def test_get_results_DO_NOT_FILTER(self):
        """Does get_results handle the DO_NOT_FILTER flag?
        """
        self.assertEqual(
            2,
            self.filter.get_results(item='DO_NOT_FILTER').count())

    def test_get_results_filter(self):
        """Does get_results handle a filter?
        """
        filter_on = self.institution_one

        self.assertEqual(1,
                         self.filter.get_results(item=filter_on).count())
