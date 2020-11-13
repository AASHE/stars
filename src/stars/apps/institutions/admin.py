from django.contrib import admin

from models import (Institution, StarsAccount,
                    PendingAccount, Subscription,
                    SubscriptionPayment, RegistrationReason,
                    RegistrationSurvey, RespondentRegistrationReason,
                    RespondentSurvey, ClimateZone, MigrationHistory)
from stars.apps.submissions.models import RATED_SUBMISSION_STATUS
from stars.apps.credits.models import Rating


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'aashe_id', 'date_created', 'enabled',
                    'current_rating')
    search_fields = ('name',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(InstitutionAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['current_submission'].queryset = (
                obj.submissionset_set.all())
            form.base_fields['rated_submission'].queryset = (
                obj.submissionset_set.filter(status=RATED_SUBMISSION_STATUS))
            form.base_fields['current_subscription'].queryset = (
                obj.subscription_set.all())
            form.base_fields['latest_expired_submission'].queryset = (
                obj.submissionset_set.filter(status=RATED_SUBMISSION_STATUS))
        rating_choices = [(r.id, "%s (%s)" % (r.name, r.creditset.version))
                          for r in Rating.objects.all()]
        rating_choices.insert(0, ("", "--------"))
        form.base_fields['current_rating'].choices = rating_choices
        return form


admin.site.register(Institution, InstitutionAdmin)


class StarsAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'user_level')
    list_filter = ('institution',)
    search_fields = ('user__email',)


admin.site.register(StarsAccount, StarsAccountAdmin)


class PendingAccountAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'institution', 'user_level')
    list_filter = ('institution',)
    search_fields = ('user_email',)


admin.site.register(PendingAccount, PendingAccountAdmin)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('institution', 'start_date', 'end_date',
                    'ratings_allocated', 'ratings_used', 'paid_in_full')
    search_fields = ('institution__name',)


admin.site.register(Subscription, SubscriptionAdmin)


class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'method', 'date')
    search_fields = ('subscription__institution__name',)


admin.site.register(SubscriptionPayment, SubscriptionPaymentAdmin)


class RegistrationReasonAdmin(admin.ModelAdmin):
    pass


admin.site.register(RegistrationReason, RegistrationReasonAdmin)


class RegistrationSurveyAdmin(admin.ModelAdmin):
    list_display = ('institution', 'primary_reason')


admin.site.register(RegistrationSurvey, RegistrationSurveyAdmin)


class RespondentRegistrationReasonAdmin(admin.ModelAdmin):
    pass


admin.site.register(RespondentRegistrationReason,
                    RespondentRegistrationReasonAdmin)


class RespondentSurveyAdmin(admin.ModelAdmin):
    list_display = ('institution', 'source')


admin.site.register(RespondentSurvey, RespondentSurveyAdmin)


class ClimateZoneAdmin(admin.ModelAdmin):
    pass


admin.site.register(ClimateZone, ClimateZoneAdmin)


class MigrationHistoryAdmin(admin.ModelAdmin):
    list_display = ('institution', 'date', 'source_ss', 'target_ss')

    def get_form(self, request, obj=None, **kwargs):
        form = super(MigrationHistoryAdmin, self).get_form(
            request, obj, **kwargs)
        if obj:
            qs = obj.institution.submissionset_set.all()
            form.base_fields['source_ss'].queryset = qs
            form.base_fields['target_ss'].queryset = qs
        return form


admin.site.register(MigrationHistory, MigrationHistoryAdmin)
