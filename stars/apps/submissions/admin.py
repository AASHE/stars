from django.contrib import admin

from models import *

class SubmissionSetAdmin(admin.ModelAdmin):
    list_display = ('creditset', 'institution', 'date_registered', 'date_submitted', 'date_reviewed', 'rating', 'is_locked')
    list_filter = ('date_registered','status', 'is_locked')
    search_fields = ('institution__name',)
admin.site.register(SubmissionSet, SubmissionSetAdmin)

class BoundaryAdmin(admin.ModelAdmin):
    list_display = ("submissionset",)
    search_fields = ('submissionset__institution__name',)
admin.site.register(Boundary, BoundaryAdmin)

class CategorySubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', "submissionset")
    list_filter = ('submissionset__institution',)
admin.site.register(CategorySubmission, CategorySubmissionAdmin)

class DataCorrectionRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'reporting_field', 'date','approved')
    list_filter = ('approved',)
admin.site.register(DataCorrectionRequest, DataCorrectionRequestAdmin)

class SubcategorySubmissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(SubcategorySubmission, SubcategorySubmissionAdmin)

class CreditUserSubmissionAdmin(admin.ModelAdmin):
    list_filter = ("submission_status", 'credit')
    list_display = ("credit", "get_institution", "submission_status", "last_updated")
admin.site.register(CreditUserSubmission, CreditUserSubmissionAdmin)

class UploadSubmissionAdmin(admin.ModelAdmin):
    pass
admin.site.register(UploadSubmission, UploadSubmissionAdmin)

class ResponsiblePartyAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'institution', 'email')
    list_filter = ('institution',)
admin.site.register(ResponsibleParty, ResponsiblePartyAdmin)

class CreditSubmissionInquiryInline(admin.TabularInline):
    model = CreditSubmissionInquiry

class SubmissionInquiryAdmin(admin.ModelAdmin):
    list_display = ('date', 'anonymous', 'last_name', 'first_name', 'submissionset')
    inlines = [CreditSubmissionInquiryInline,]
admin.site.register(SubmissionInquiry, SubmissionInquiryAdmin)

class ExtensionRequestAdmin(admin.ModelAdmin):
    list_display = ('submissionset', 'date','user')
    search_fields = ('user__username',)
admin.site.register(ExtensionRequest, ExtensionRequestAdmin)
