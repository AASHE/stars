from django.contrib import admin

from models import *

class RatingAdmin(admin.ModelAdmin):
    list_display = ('name', 'minimal_score', 'creditset', 'image_large')
    list_filter = ('creditset',)
    ordering = ('minimal_score', 'creditset', )

admin.site.register(Rating, RatingAdmin)

class IncrementalFeatureAdmin(admin.ModelAdmin):
    pass
admin.site.register(IncrementalFeature, IncrementalFeatureAdmin)

class CreditSetAdmin(admin.ModelAdmin):
    list_display = ('version', 'release_date')
admin.site.register(CreditSet, CreditSetAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'creditset',)
    list_filter = ('creditset',)
    search_fields = ('title',)

    class Media:
        js = (
            '/media/tp/js/tiny_mce/tiny_mce.js',
            '/media/static/js/textarea_admin.js',
          )
admin.site.register(Category, CategoryAdmin)

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category',)
    list_filter = ('category__creditset', 'category',)
    search_fields = ('title',)

    class Media:
        js = (
            '/media/tp/js/tiny_mce/tiny_mce.js',
            '/media/static/js/textarea_admin.js',
          )
admin.site.register(Subcategory, SubcategoryAdmin)

class DocumentationFieldInline(admin.TabularInline):
    model = DocumentationField

class CreditAdmin(admin.ModelAdmin):
    list_display = ('get_identifier','title', 'subcategory', 'type')
    list_filter = ('subcategory__category__creditset', 'subcategory',)
    search_fields = ('title',)
    inlines = [
            DocumentationFieldInline,
        ]

    class Media:
        js = (
            '/media/tp/js/tiny_mce/tiny_mce.js',
            '/media/static/js/textarea_admin.js',
          )
admin.site.register(Credit, CreditAdmin)


class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'equivalent', 'ratio', 'is_metric')
admin.site.register(Unit, UnitAdmin)


class ChoiceInline(admin.TabularInline):
    model = Choice


class DocumentationFieldAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'credit', 'required')
    list_filter = ('type',)
    search_fields = ('title', 'credit',)
    inlines = [ChoiceInline]
admin.site.register(DocumentationField, DocumentationFieldAdmin)

# class ChoiceAdmin(admin.ModelAdmin):
#     list_display = ('choice', 'documentation_field', 'is_bonafide')
#     list_filter = ('documentation_field',)
# admin.site.register(Choice, ChoiceAdmin)
