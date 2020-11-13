from django.contrib import admin

from models import *

class HomepageUpdateAdmin(admin.ModelAdmin):
    list_display = ('title','published', 'link')

admin.site.register(HomepageUpdate, admin.ModelAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title','published', )
    prepopulated_fields = {'slug': ('title',)}
    class Media:
        js = ('/media/tp/js/tiny_mce/tiny_mce.js',
              '/media/static/js/textarea_admin.js',)
admin.site.register(Category, CategoryAdmin)

class NewArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'timestamp',)
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('categories',)
    class Media:
        js = ('/media/tp/js/tiny_mce/tiny_mce.js',
              '/media/static/js/textarea_admin.js',)
admin.site.register(NewArticle, NewArticleAdmin)