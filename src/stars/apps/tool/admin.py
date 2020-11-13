"""
    This section is used exclusively to override the django-terms admin.py file
"""

from django.contrib import admin
from terms.admin import TermAdmin
from terms.models import Term

class MyTermAdmin(TermAdmin):
    class Media:
        js = ('/media/tp/js/tiny_mce/tiny_mce.js',
              '/media/static/js/textarea_admin.js',)

admin.site.unregister(Term)
admin.site.register(Term, MyTermAdmin)