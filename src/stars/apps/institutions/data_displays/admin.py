from django.contrib import admin

from models import *

class AuthorizedUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'start_date', 'end_date', 'member_level', 'participant_level')
    search_fields = ('email',)
admin.site.register(AuthorizedUser, AuthorizedUserAdmin)