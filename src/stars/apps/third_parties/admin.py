from django.contrib import admin
from django.contrib.auth.models import User

from models import ThirdParty

class ThirdPartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'publication')
    filter_horizontal = ('authorized_users',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ThirdPartyAdmin, self).get_form(request, obj, **kwargs)

        if obj:
            choices = [(u.id, u.email) for u in User.objects.all()]
            form.base_fields['authorized_users'].choices = choices
        return form

admin.site.register(ThirdParty, ThirdPartyAdmin)
