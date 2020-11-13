from django.contrib import admin

from models import *

class HelpContextAdmin(admin.ModelAdmin):
    class Media:
        js = ('/media/tp/js/tiny_mce/tiny_mce.js',
              '/media/static/js/textarea_admin.js',)
admin.site.register(HelpContext, HelpContextAdmin)

class BlockContentAdmin(admin.ModelAdmin):
    class Media:
        js = ('/media/tp/js/tiny_mce/tiny_mce.js',
              '/media/static/js/textarea_admin.js',)
admin.site.register(BlockContent, BlockContentAdmin)

class SnippetContentAdmin(admin.ModelAdmin):
    pass
admin.site.register(SnippetContent, SnippetContentAdmin)
