from django.contrib import admin

from models import *

class EmailInline(admin.TabularInline):
    model = CopyEmail

class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'active')
    search_fields = ('title','description', 'content')
    list_filter = ('active',)
    inlines = [
        EmailInline,
    ]
admin.site.register(EmailTemplate, EmailTemplateAdmin)
