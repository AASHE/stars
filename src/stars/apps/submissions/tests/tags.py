"""
    Test Suite for Submission Tool.  
    These tests cover all aspects of the submission tool, including
     - the SubmissionSet hierarchy of models
     - the submission tool
     - submission template tags

@todo: turn this into a unit test:     
from stars.apps.credits.models import CreditSet, Category, Subcategory, Credit, DocumentationField, ApplicabilityReason
from stars.apps.submissions.models import get_active_submissions, get_active_field_submissions, get_na_submissions
cs = CreditSet.objects.get(pk=1)
cat = Category.objects.get(pk=2)
subcat = Subcategory.objects.get(pk=5)
credit = Credit.objects.get(pk=1)
reason = ApplicabilityReason.objects.get(pk=1)
textfield = DocumentationField.objects.get(pk=1)
datefield = DocumentationField.objects.get(pk=2)
numfield = DocumentationField.objects.get(pk=3)
cssubs = get_active_submissions(creditset=cs)
print cssubs
print cs.num_submissions()
catsubs = get_active_submissions(category=cat)
print catsubs
print cat.num_submissions()
subsubs = get_active_submissions(subcategory=subcat)
print subsubs
print subcat.num_submissions()
creditsubs = get_active_submissions(credit=credit)
print creditsubs
print credit.num_submissions()
reasonsubs = get_na_submissions(reason)
print reasonsubs
print reason.num_submissions()
textsubs = get_active_field_submissions(textfield)
print textsubs
print textfield.num_submissions()
datesubs = get_active_field_submissions(datefield)
print datesubs
print datefield.num_submissions()
numsubs = get_active_field_submissions(numfield)
print numsubs
print numfield.num_submissions()
     
"""
from django.test import TestCase
from stars.apps.submissions.models import *

from apps.tool.my_submission.templatetags import submit_tags
class Submit_tags_Test(TestCase):
    fixtures = ['v0.5-categories.json', 'v0.5-credits.json', 'v0.5-submission_set.json', 'v0.5-submission-credits.json']
    
    """
        #######   submit_tags.py Test Suite.  #######
    """
    def test_format_available_points(self):
        set, cat, subcat, credit, field = self._get_test_submission_objects()

        tag_context = submit_tags.format_available_points(set)
        self.assertEqual(tag_context['available_points'], 11.0)

        tag_context = submit_tags.format_available_points(cat)
        self.assertEqual(tag_context['available_points'], 8.0)

        tag_context = submit_tags.format_available_points(subcat)
        self.assertEqual(tag_context['available_points'], 4.0)
    
        tag_context = submit_tags.format_available_points(credit)
        self.assertEqual(tag_context['available_points'], 4.0)

    def test_show_submit_crumbs(self):
        set, cat, subcat, credit, field  = self._get_test_submission_objects()

        tag_context = submit_tags.show_submit_crumbs(set)
        self.assertEqual(tag_context['object_set'], [set])

        tag_context = submit_tags.show_submit_crumbs(cat)
        self.assertEqual(tag_context['object_set'], [set, cat])

        tag_context = submit_tags.show_submit_crumbs(subcat)
        self.assertEqual(tag_context['object_set'], [set, cat, subcat])
    
        tag_context = submit_tags.show_submit_crumbs(credit)
        self.assertEqual(tag_context['object_set'], [set, cat, subcat, credit])

    def _get_test_submission_objects(self):
        """ Returns a known suite of test submission objects:
            submission set -> category submission -> subcategory submission -> credit submission -> documentation field submission
        """
        set = SubmissionSet.objects.all()[0]
        self.assertEqual(set.creditset.version, u'0.5')

        cat = CategorySubmission.objects.all()[1]
        self.assertEqual(cat.category.title, u'Operations')        
 
        subcat = SubcategorySubmission.objects.all()[1]
        self.assertEqual(subcat.subcategory.title, u'Buildings')
    
        credit = CreditUserSubmission.objects.all()[0]
        self.assertEqual(credit.credit.title, u'New Green Buildings')

        field = URLSubmission.objects.all()[0]
        self.assertEqual(field.documentation_field.title, u'Website URL where the green building policy is posted')

        return set, cat, subcat, credit, field
