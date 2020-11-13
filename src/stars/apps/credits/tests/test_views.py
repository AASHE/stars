"""
    Test the credit structure mixin
"""

from django.test import TestCase
from django.views.generic import TemplateView

from stars.apps.credits.views import CreditsetStructureMixin


class TestStructure(TestCase):
    fixtures = ['basic_creditset.json',]

    def setUp(self):
        pass

    def testMixin(self):
        """

        """
        class TestView(CreditsetStructureMixin, TemplateView):
            pass

        view = TestView()

        # /creditset_version/category_abbreviation/subcategory_slug/credit_number/field_id/
        kwargs = {}
        kwargs['creditset_version'] = "test"

        _context = view.get_context_data(**kwargs)
        cs = view.get_creditset()
        self.assertEqual(cs.id, 1)

        menu = view.get_creditset_nav()
        test_menu = [
            {
                'bookmark': u'/test/TC/',
                'title': u'Test Category',
                'attrs': {'id': 1},
                'children': [
                    {
                        'bookmark': u'/test/TC/test-subcategory/',
                        'title': u'Test Subcategory',
                        'attrs': {'id': 1},
                        'children': [
                            {
                                'url': u'/test/TC/test-subcategory/1/',
                                'attrs': {'id': 1},
                                'title': u'C1: Test Credit'
                            }
                        ]
                    }
                ]
            }
        ]

        self.assertEqual(menu[0], test_menu[0])

        # try a bogus category
        kwargs['category_abbreviation'] = 'TZ'

        try:
            _context = view.get_context_data(**kwargs)
        except Exception as e:
            self.assertEqual(e.__class__.__name__, "Http404")

        try:
            _context = view.get_context_data(**kwargs)
        except Exception as e:
            self.assertEqual(e.__class__.__name__, "Http404")

        # fix the category
        kwargs['category_abbreviation'] = 'TC'
        _context = view.get_context_data(**kwargs)
        cat = view.get_category()
        self.assertEqual(cat.id, 1)

        menu = view.get_creditset_nav()
        test_menu = [
            {
                'bookmark': u'/test/TC/',
                'attrs': {'id': 1},
                'children': [
                    {
                        'bookmark': u'/test/TC/test-subcategory/',
                        'attrs': {'id': 1},
                        'children': [
                            {
                                'url': u'/test/TC/test-subcategory/1/',
                                'attrs': {'id': 1},
                                'title': u'C1: Test Credit'
                            }
                        ],
                        'title': u'Test Subcategory'
                    }
                ],
                'title': u'Test Category'
            }
        ]
        self.assertEqual(menu[0], test_menu[0])
