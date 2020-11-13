#!/usr/bin/env python
from django.shortcuts import render_to_response, get_object_or_404

"""
    Tests for the cms
    
    usage: python manage.py execfile tests/cms.py
"""

from stars.apps.cms.models import *

# todo: convert these to unit tests, starting with a syncdb

print "---------------TESTING ArticleMenu -------------------------"
try:
    help_category = ArticleCategory.objects.get(slug="help")
    menu = ArticleMenu(help_category)
    for subcategory in menu.subcategories:
        print subcategory.label + " : " + subcategory.get_absolute_url()
        for article in subcategory.articles:
            print "    " + article.title  + " : " + article.get_absolute_url()
#            print article.term
except Exception, e:
        print "Nope: %s" % e

print "---------------TESTING ArticleList -------------------------"
try:
    help_category = ArticleCategory.objects.get(slug="help")
    list = ArticleList(help_category)
    for article in list:
        print "Title: " + article.title + "  nid: " + article.nid
        print "     Teaser: " + article.teaser
except Exception, e:
        print "Nope: %s" % e


print "---------------TESTING Category CRUD  -------------------------"
cats = ArticleCategory.objects.all()
for cat in cats :
    if (cat.slug == 'test') :
        cat.delete()
ArticleCategory.objects.create(label="Test", ordinal=6, slug="test", term_id=0, parent_term=help_category.term_id, depth=1)
category = ArticleCategory.objects.get(slug="test")
print "Test category: " + category.label
root_category = category.get_root_category()
print "Root category : " + root_category.label

print "---------------TESTING Article -------------------------"
try:
    article = Article(3499, category)
    print article.title
    print article.get_absolute_url()
    print article.get_edit_url()
except Exception, e:
        print "Nope: %s" % e

category.delete()

#print "---------------TESTING Category SYNC  -------------------------"
#from stars.apps.cms.views import article_category_sync
#article_category_sync(None)
