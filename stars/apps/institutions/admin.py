from django.contrib import admin

from models import *

class InstitutionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Institution, InstitutionAdmin)

class StarsAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'user_level')
admin.site.register(StarsAccount, StarsAccountAdmin)