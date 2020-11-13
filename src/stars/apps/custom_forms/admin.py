from django.contrib import admin

from models import DataDisplayAccessRequest


class DataDisplayAccessRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'name', 'affiliation', 'email', 'date')


admin.site.register(DataDisplayAccessRequest, DataDisplayAccessRequestAdmin)
