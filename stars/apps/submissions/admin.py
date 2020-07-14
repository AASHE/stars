from django.contrib import admin


from models import (
    SubmissionSet,
    Boundary,
    CategorySubmission,
    DataCorrectionRequest,
    SubcategorySubmission,
    CreditUserSubmission,
    UploadSubmission,
    ResponsibleParty,
    CreditSubmissionInquiry,
    Flag,
    SubmissionInquiry,
    ExtensionRequest,
    URLSubmission,
    NumericSubmission,
    TextSubmission,
    LongTextSubmission,
    BooleanSubmission,
    DateSubmission,
)
from stars.apps.credits.widgets import (
    CategorySelectTree,
    SubcategorySelectTree,
    CreditSelectTree,
)
from stars.apps.credits.models import Rating

from django.forms.widgets import TextInput


class SubmissionSetMixin:
    def get_institution_user_choices(self, submissionset):
        user_list = []
        for a in submissionset.institution.starsaccount_set.all():
            user_list.append(a.user)
        if (
            submissionset.registering_user
            and submissionset.registering_user not in user_list
        ):
            user_list.append(submissionset.registering_user)
        if (
            submissionset.submitting_user
            and submissionset.submitting_user not in user_list
        ):
            user_list.append(submissionset.submitting_user)
        choices = [(u.id, u.email) for u in user_list]
        return choices

    def get_subcategory_choices(self, submissionset):
        choices = []
        for cat_sub in submissionset.categorysubmission_set.all():
            for sub_sub in cat_sub.subcategorysubmission_set.all():
                choices.append((sub_sub.id, sub_sub.subcategory.title))
        return choices

    def get_responsible_party_choices(self, submissionset):
        return [
            (rp.id, rp.email)
            for rp in submissionset.institution.responsibleparty_set.all()
        ]


class SubmissionSetAdmin(admin.ModelAdmin, SubmissionSetMixin):
    list_display = (
        "creditset",
        "institution",
        "date_created",
        "date_submitted",
        "date_published",
        "date_expiration",
        "status",
        "rating",
        "is_locked",
        "is_visible",
    )
    list_filter = ("date_registered", "status", "is_locked", "expired", "is_visible")
    search_fields = ("institution__name",)

    def get_form(self, request, obj=None, **kwargs):
        form = super(SubmissionSetAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            choices = self.get_institution_user_choices(obj)
            form.base_fields["registering_user"].choices = choices
            form.base_fields["submitting_user"].choices = choices
        rating_choices = [
            (r.id, "%s (%s)" % (r.name, r.creditset.version))
            for r in Rating.objects.all()
        ]
        rating_choices.insert(0, ("", "---------"))
        form.base_fields["rating"].choices = rating_choices

        migrated_choices = [
            (s.id, "%s" % s) for s in obj.institution.submissionset_set.all()
        ]
        migrated_choices.insert(0, ("", "---------"))
        form.base_fields["migrated_from"].choices = migrated_choices

        return form


admin.site.register(SubmissionSet, SubmissionSetAdmin)


class BoundaryAdmin(admin.ModelAdmin):
    list_display = ("submissionset",)
    search_fields = ("submissionset__institution__name",)


admin.site.register(Boundary, BoundaryAdmin)


class CategorySubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "submissionset")
    list_filter = ("submissionset__institution",)


admin.site.register(CategorySubmission, CategorySubmissionAdmin)


class DataCorrectionRequestAdmin(SubmissionSetMixin, admin.ModelAdmin):
    list_display = (
        "get_submissionset",
        "date",
        "approved",
        "reporting_field",
        "get_credit",
        "get_required_status",
    )
    list_filter = ("approved",)

    def get_form(self, request, obj=None, **kwargs):
        """
            Show the choice objects in the help text if this is a choice field
        """
        form = super(DataCorrectionRequestAdmin, self).get_form(request, obj, **kwargs)

        if obj.reporting_field.documentation_field.type == "choice":
            choice_list_text = ""
            for c in obj.reporting_field.documentation_field.choice_set.all():
                choice_list_text += "%d: %s<br/>" % (c.id, c.choice)
            form.base_fields["new_value"].help_text = choice_list_text

        if obj.reporting_field.documentation_field.type == "boolean":
            form.base_fields[
                "new_value"
            ].help_text = "Use <b>Yes</b>, <b>No</b>, or <b>Unknown</b>"

        if obj.reporting_field.documentation_field.type == "date":
            form.base_fields[
                "new_value"
            ].help_text = "This is a date field. You must use the format YYYY-MM-DD, for example 1979-12-24."

        cus = CreditUserSubmission.objects.get(
            pk=obj.reporting_field.credit_submission.id
        )
        choices = self.get_institution_user_choices(cus.get_submissionset())
        form.base_fields["user"].choices = choices
        return form


admin.site.register(DataCorrectionRequest, DataCorrectionRequestAdmin)


class SubcategorySubmissionAdmin(admin.ModelAdmin):
    pass


admin.site.register(SubcategorySubmission, SubcategorySubmissionAdmin)


class CreditUserSubmissionAdmin(admin.ModelAdmin, SubmissionSetMixin):
    list_filter = ("submission_status", "credit")
    list_display = ("credit", "get_institution", "submission_status", "last_updated")

    class Media:
        js = (
            "/media/static/bootstrap/js/jquery.js",
            "/media/static/js/select_tree.js",
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super(CreditUserSubmissionAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            ss = obj.get_submissionset()
            choices = self.get_institution_user_choices(ss)
            form.base_fields["user"].choices = choices
            choices = self.get_subcategory_choices(ss)
            form.base_fields["subcategory_submission"].choices = choices
            choices = []
            form.base_fields["applicability_reason"].choices = [
                (ar.id, ar.title) for ar in obj.credit.applicabilityreason_set.all()
            ]
            form.base_fields[
                "responsible_party"
            ].choices = self.get_responsible_party_choices(ss)
            form.base_fields["credit"].widget = CreditSelectTree()
        return form


admin.site.register(CreditUserSubmission, CreditUserSubmissionAdmin)


class SubmissionFieldMixin(object):
    list_display = ("id", "get_cus_id", "get_df_id")

    def get_form(self, request, obj=None, **kwargs):
        """
            This prevents super-long load times
        """
        form = super(SubmissionFieldMixin, self).get_form(request, obj, **kwargs)
        form.base_fields["credit_submission"].widget = TextInput()
        form.base_fields["documentation_field"].widget = TextInput()
        return form

    def get_cus_id(self, obj):
        return obj.credit_submission.id

    get_cus_id.short_description = "Credit Submission Id"

    def get_df_id(self, obj):
        return obj.documentation_field.id

    get_df_id.short_description = "Doc Field Id"


class UploadSubmissionAdmin(SubmissionFieldMixin, admin.ModelAdmin):
    pass


admin.site.register(UploadSubmission, UploadSubmissionAdmin)


class URLSubmissionAdmin(SubmissionFieldMixin, admin.ModelAdmin):
    pass


admin.site.register(URLSubmission, URLSubmissionAdmin)


class NumericSubmissionAdmin(SubmissionFieldMixin, admin.ModelAdmin):
    pass


admin.site.register(NumericSubmission, NumericSubmissionAdmin)


class TextSubmissionAdmin(SubmissionFieldMixin, admin.ModelAdmin):
    pass


admin.site.register(TextSubmission, TextSubmissionAdmin)


class LongTextSubmissionAdmin(SubmissionFieldMixin, admin.ModelAdmin):
    pass


admin.site.register(LongTextSubmission, LongTextSubmissionAdmin)


class BooleanSubmissionAdmin(SubmissionFieldMixin, admin.ModelAdmin):
    pass


admin.site.register(BooleanSubmission, BooleanSubmissionAdmin)


class DateSubmissionAdmin(SubmissionFieldMixin, admin.ModelAdmin):
    pass


admin.site.register(DateSubmission, DateSubmissionAdmin)


class ResponsiblePartyAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "institution", "email")
    list_filter = ("institution",)


admin.site.register(ResponsibleParty, ResponsiblePartyAdmin)


class CreditSubmissionInquiryInline(admin.TabularInline):
    model = CreditSubmissionInquiry


class FlagAdmin(admin.ModelAdmin):
    model = Flag


admin.site.register(Flag, FlagAdmin)


class SubmissionInquiryAdmin(admin.ModelAdmin):
    list_display = ("date", "anonymous", "last_name", "first_name", "submissionset")
    inlines = [CreditSubmissionInquiryInline]


admin.site.register(SubmissionInquiry, SubmissionInquiryAdmin)


class ExtensionRequestAdmin(admin.ModelAdmin):
    list_display = ("submissionset", "date", "user")
    search_fields = ("user__username",)


admin.site.register(ExtensionRequest, ExtensionRequestAdmin)
