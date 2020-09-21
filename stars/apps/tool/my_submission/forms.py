import string
import sys
from logging import getLogger

from django import forms
from django.forms import Form, ModelForm
from django.forms.widgets import SelectDateWidget
from django.utils.safestring import mark_safe
from django.forms.utils import ErrorList
from django.forms.widgets import TextInput, ClearableFileInput, HiddenInput
from extra_views import InlineFormSet
from form_utils.forms import BetterModelForm

from stars.apps.helpers.forms import fields as custom_fields
from stars.apps.helpers.forms.forms import LocalizedModelFormMixin
from stars.apps.helpers.forms.util import WarningList
from stars.apps.submissions.models import *


logger = getLogger("stars")


class NewBoundaryForm(LocalizedModelFormMixin, BetterModelForm):
    class Meta:
        model = Boundary
        exclude = ("submissionset",)

        fieldsets = [
            (
                "Characteristics",
                {
                    "fields": Boundary.get_characteristic_field_names(),
                    "legend": "Characteristics",
                    "description": "boundary_characteristics",
                },
            ),
            (
                "Features",
                {
                    "fields": [
                        "ag_school_present",
                        "ag_school_included",
                        "ag_school_details",
                        "med_school_present",
                        "med_school_included",
                        "med_school_details",
                        "pharm_school_present",
                        "pharm_school_included",
                        "pharm_school_details",
                        "pub_health_school_present",
                        "pub_health_school_included",
                        "pub_health_school_details",
                        "vet_school_present",
                        "vet_school_included",
                        "vet_school_details",
                        "sat_campus_present",
                        "sat_campus_included",
                        "sat_campus_details",
                        "hospital_present",
                        "hospital_included",
                        "hospital_details",
                        "farm_present",
                        "farm_included",
                        "farm_acres",
                        "farm_details",
                        "agr_exp_present",
                        "agr_exp_included",
                        "agr_exp_acres",
                        "agr_exp_details",
                    ],
                    "legend": "Features",
                    "description": "boundary_features",
                },
            ),
            (
                "narrative",
                {
                    "fields": ["additional_details"],
                    "legend": "Narrative",
                    "description": "boundary_narrative",
                },
            ),
        ]

    def __init__(self, *args, **kwargs):
        super(NewBoundaryForm, self).__init__(*args, **kwargs)


class SubcategorySubmissionForm(ModelForm):
    class Meta:
        model = SubcategorySubmission
        fields = ("description",)

    def __init__(self, *args, **kwargs):
        super(SubcategorySubmissionForm, self).__init__(*args, **kwargs)

        self.fields["description"].widget.attrs = {
            "onkeydown": "field_changed(this);",
            "onchange": "field_changed(this);",
            "style": "width: 35em;height: 15em;",
        }


class SubmissionFieldFormMixin:
    def append_error(self, msg):
        """ Helper to append or add new error message to this form's
        value field error list"""
        if "value" in self._errors:
            self._errors["value"].append(msg)
        else:
            self._errors["value"] = ErrorList([msg])

    def append_warning(self, msg):
        """ Helper to append or add new warning message to this form's
        value field warning list"""
        if self.warnings:
            self.warnings.append(msg)
        else:
            self.warnings = WarningList([msg])


class SubmissionFieldForm(SubmissionFieldFormMixin, LocalizedModelFormMixin, ModelForm):
    """ Parent class for all submission fields to provide access to
    clean_value"""

    def __init__(self, *args, **kwargs):
        """ Add any specified options to the form's value field """
        super(SubmissionFieldForm, self).__init__(*args, **kwargs)
        self.warnings = None

    def field_includes_units(self):
        """ Returns true if the form field contains its own units,
        false otherwise"""
        return self.__class__ in (
            ChoiceWithOtherSubmissionForm,
            MultiChoiceSubmissionForm,
            MultiChoiceWithOtherSubmissionForm,
        )

    def form_name():
        return u"Credit Submission Form"

    form_name = staticmethod(form_name)

    def get_form_class(submission_field):
        """Return the class for the Form matching the
        DocumentationFieldSubmission submission_field model"""
        SubmissionFormsModule = sys.modules[__name__]
        FormClass = getattr(
            SubmissionFormsModule, "%sForm" % submission_field.__class__.__name__, None
        )
        return FormClass

    get_form_class = staticmethod(get_form_class)


class AbstractChoiceSubmissionForm(SubmissionFieldForm):
    """ An abstract base class to provide some of the baseline
    behaviour for choice-type field forms."""

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """
            Set up the choice's for the 'value' field on the form:

            - choices are drawn from the bonafide Choices defined for
              its doc. field.

            Note: widget cannot be replaced after this call!!
            Currently, subclasses must use value field's default
            widget...
        """
        super(AbstractChoiceSubmissionForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields["value"].queryset = self.instance.get_choice_queryset()


class AbstractMultiFieldSubmissionForm(AbstractChoiceSubmissionForm):
    """ An abstract base class for choice-with-other-type and other
    multi-field submissionforms."""

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """  Hook up the compress / decompress logic for the multi-field """
        super(AbstractMultiFieldSubmissionForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields["value"].set_compress_methods(
                self.instance.compress, self.instance.decompress
            )


class ChoiceSubmissionForm(AbstractChoiceSubmissionForm):
    # Uses the defaut ChoiceField and widget.
    class Meta:
        model = ChoiceSubmission
        fields = ["value"]


class ChoiceWithOtherSubmissionForm(AbstractMultiFieldSubmissionForm):
    value = custom_fields.ModelChoiceWithOtherField(required=False)

    class Meta:
        model = ChoiceSubmission
        fields = ["value"]


class MultiChoiceSubmissionForm(AbstractChoiceSubmissionForm):
    value = custom_fields.ModelMultipleChoiceCheckboxField(required=False)

    class Meta:
        model = MultiChoiceSubmission
        fields = ["value"]


class MultiChoiceWithOtherSubmissionForm(AbstractMultiFieldSubmissionForm):
    value = custom_fields.ModelMultipleChoiceWithOtherField(required=False)

    class Meta:
        model = MultiChoiceSubmission
        fields = ["value"]


class URLSubmissionForm(SubmissionFieldForm):
    value = forms.URLField(
        required=False, widget=TextInput(attrs={"style": "width: 600px;"})
    )

    class Meta:
        model = URLSubmission
        fields = ["value"]


class DateSubmissionForm(SubmissionFieldForm):
    value = forms.DateField(widget=SelectDateWidget(), required=False)

    def __init__(self, *args, **kwargs):
        """ If there is an instance, use the date range from that instance. """
        super(DateSubmissionForm, self).__init__(*args, **kwargs)
        if self.instance:
            min = self.instance.documentation_field.min_range
            max = self.instance.documentation_field.max_range
            if min is not None and max is not None:
                self.fields["value"].widget = SelectDateWidget(
                    years=range(min, max + 1)
                )

    class Meta:
        model = DateSubmission
        fields = ["value"]


class NumericSubmissionForm(SubmissionFieldForm):
    class Meta:
        model = NumericSubmission
        fields = ["value", "metric_value"]

    def __init__(self, *args, **kwargs):
        """
            Sets the base field to use. If it's metric, use the metric_value
            field if not, just use the value field. These will be converted for
            cleaning and during save.

            *from model's use_metric() method:
            We only use the `metric_value` if the institution is using metric,
            the field has units and those units are not the same for metric and
            US
        """

        super(NumericSubmissionForm, self).__init__(*args, **kwargs)

        # try:
        if self.instance.use_metric():
            self.units = self.instance.documentation_field.us_units
            self.fields["value"].widget = forms.HiddenInput()
        else:
            self.units = self.instance.documentation_field.metric_units
            self.fields["metric_value"].widget = forms.HiddenInput()
        # except Institution.DoesNotExist:
        # this will raise an error in credit editor
        # pass
        # If this is a calculated field, make the widgets read-only:
        if self.instance.documentation_field.type == "calculated":
            for field in self.fields.values():
                field.widget.attrs["readonly"] = "readonly"

    def clean_value(self):
        """ validate the value field if they aren't using metric """
        value = self.cleaned_data.get("value")
        if not self.instance.use_metric():
            if value is not None:
                min = self.instance.documentation_field.min_range
                max = self.instance.documentation_field.max_range
                self._validate_min_max(value, min, max)
        return value

    def clean_metric_value(self):
        """ validate the metric_value field when using metric """
        metric_value = self.cleaned_data.get("metric_value")
        if self.instance.use_metric():
            if metric_value is not None:
                min = self.instance.documentation_field.min_range
                max = self.instance.documentation_field.max_range
                if min is not None:
                    min = self.units.convert(min)
                if max is not None:
                    max = self.units.convert(max)
                self._validate_min_max(metric_value, min, max)
        return metric_value

    def _validate_min_max(self, value, min, max):
        """
            Validates that a value is within the min and max.
            It doesn't use the properties of self to allow the logic to be
            duplicated for metric and us values

            raises a validation error if necessary
        """
        if min is not None and max is not None and (value < min or value > max):
            raise forms.ValidationError(
                "The value is outside of the accepted range for this field "
                "(range: %d - %d)." % (min, max)
            )
        elif min is not None and value < min:
            raise forms.ValidationError(
                "The value is must be greater than or equal to %d." % min
            )
        elif max is not None and value > max:
            raise forms.ValidationError(
                "The value is must be less than or equal to %d" % max
            )

    def clean(self):
        """
            If we're using metric, convert value for formula validation

            save() on the model handles conversion. this is just for validation
        """
        # if there were field errors, we have no cleaned data.
        if not self.is_valid():
            return self.cleaned_data

        value = self.cleaned_data.get("value")
        metric_value = self.cleaned_data.get("metric_value")

        if self.instance.use_metric():
            if metric_value is not None:
                units = self.instance.documentation_field.metric_units
                if units is not None:
                    value = units.convert(metric_value)
            else:
                value = None

        return {"value": value, "metric_value": metric_value}

    def raise_validation_error(self, error_message, min=None, max=None):
        """Raises forms.ValidationError, converting `min` and `max` in
        the error message to metric, when appropriate.
        """
        if self.instance.use_metric() and self.units:
            for num in min, max:
                if num:
                    num = self.units.convert(num)
        raise forms.ValidationError(error_message.format(min=min, max=max))


class TextSubmissionForm(SubmissionFieldForm):
    class Meta:
        model = TextSubmission
        fields = ["value"]

    def __init__(self, *args, **kwargs):
        """ If there is an instance with choices, set up the choices. """
        super(TextSubmissionForm, self).__init__(*args, **kwargs)
        self["value"].field.widget.attrs["style"] = "width: 600px;"
        if self.instance:
            max = self.instance.documentation_field.max_range
            if max != None:
                self["value"].field.widget.attrs["maxlength"] = max

    def clean_value(self):
        """ Validate the character count """
        value = self.cleaned_data.get("value")
        if self.instance and value:
            max = self.instance.documentation_field.max_range

            chars = len(value)

            if max is not None:
                if chars > max:
                    raise forms.ValidationError(
                        "The text is too long for this field. "
                        "Limit: %d characters" % max
                    )
        elif not self.instance:
            logger.info("No Instance")
        return value


class LongTextSubmissionForm(SubmissionFieldForm):
    value = forms.CharField(
        widget=forms.Textarea(attrs={"style": "width: 600px;height:100px;"}),
        required=False,
    )  # don't use MCE for submissions!

    class Meta:
        model = LongTextSubmission
        fields = ["value"]

    def clean_value(self):
        """ Validate the word count """
        value = self.cleaned_data.get("value")
        if self.instance and value:
            max = self.instance.documentation_field.max_range

            words = len(string.split(value))

            if max != None:
                if words > max:
                    raise forms.ValidationError(
                        "The text is too long for this field. " "Limit: %d words" % max
                    )
        elif not self.instance:
            logger.info("No Instance")
        return value


class UploadSubmissionForm(SubmissionFieldForm):
    """
        The submitted value for a File Upload Documentation Field
    """

    class Meta:
        model = UploadSubmission
        fields = ["value"]

    def __init__(self, *args, **kwargs):
        """ Change the widget """
        super(UploadSubmissionForm, self).__init__(*args, **kwargs)
        self.fields["value"].widget = ClearableFileInput()

    def save(self, *args, **kwargs):
        instance = super(UploadSubmissionForm, self).save(*args, **kwargs)
        # Once the POST data has been saved, force form to be bound to
        # the saved instance.  See ticket #338
        self.files = {}
        self.data = {}
        from django.forms import model_to_dict

        self.initial.update(model_to_dict(instance))
        return instance


class BooleanSubmissionForm(SubmissionFieldForm):
    class Meta:
        model = BooleanSubmission
        fields = ["value"]


class CreditSubmissionForm(LocalizedModelFormMixin, ModelForm):
    """
        A collection of SubmissionFieldForms along with methods to
        process them.  This class is primarily here to serve as a base
        class for User and Test submission forms.  Warning: Currently,
        rendering the form using as_p or similar will only render
        fields defined by the sub-class.  Templates must include
        "tool/submissions/submission_fields_form.html" to render the
        submission field elements themselves.
    """

    def __init__(self, *args, **kwargs):
        """
            Construct a form to edit a CreditSubmission instance
            @param instance: CreditSubmission (or sub-class) object is REQUIRED
        """
        if not kwargs.has_key("instance") or not kwargs["instance"]:
            raise Exception(
                "CreditSubmission object is required " "for CreditSubmissionForm"
            )
        super(CreditSubmissionForm, self).__init__(*args, **kwargs)

        self.warnings = None  # Top-level warnings for this form
        # (filled by custom validation)
        self._form_fields = None  # lazy init - don't access directly,
        # call get_from_fields()

    def form_name():
        return u"Credit Submission Form"

    form_name = staticmethod(form_name)

    def get_submission_fields_and_forms(self):
        """
            Get a list of submission field form elements for this Form;

            @return: submission_field_list: list of fields and form elements

            Each item in the submission_field_list is a dictionary
            with elements 'field' and 'form'
        """
        if self._form_fields:  # lazy init
            return self._form_fields
        # else... do the work...
        self._form_fields = []

        # CAUTION: ModelForm stores any POST data during form
        # construction, BUT, if there was no POST data, the Form
        # stores data={}.  Thus, when we populate the Submission Field
        # forms below from their associated instances, we need to be
        # careful that the forms receive data=None instead of data={},
        # otherwise the Form binds the field to the empty dict rather
        # than the instance!!!
        if self.is_bound:
            data = self.data
            files = self.files
        else:
            data = None
            files = None

        # build the form fields based on the data and instance bound
        # to this form.
        prefix = 0  # Ideally, form prefix would be submission field
        # id, but this may not be set yet, and each must be
        # unique.

        for field in self.instance.get_submission_fields():
            prefix += 1
            SubmissionFieldFormClass = SubmissionFieldForm.get_form_class(field)
            if SubmissionFieldFormClass:
                # bind the field form to the data (if there was any)
                form = SubmissionFieldFormClass(
                    data,
                    files,
                    instance=field,
                    prefix="%s_%s" % (field.__class__.__name__, prefix),
                )
                form["value"].field.widget.attrs[
                    "onchange"
                ] = "field_changed(this);"  # see include.js
            else:
                # Dummy Tabular form class
                class DummyTabularForm(SubmissionFieldFormMixin):
                    def __init__(self, value):
                        self.cleaned_data = {"value": value}
                        self.warnings = None
                        self._errors = {}
                        self.instance = None

                    def is_valid(self):
                        return True

                    @property
                    def errors(self):
                        return self._errors

                    def save(self, *args, **kwargs):
                        # just a dummy
                        pass

                form = DummyTabularForm(value=None)
            self._form_fields.append({"field": field, "form": form})

        return self._form_fields

    def save(self, commit=True):
        """
            Save the data in this form (update instance or create a
            new submission)

            @return: the updated CreditSubmission instance.
        """
        # This is a bit tricky: CreditSubmission object needs the new
        # form field values to calculate points, but the form fields
        # need the CS objet to be saved so they can store a foreign
        # key to it...
        for field in self.get_submission_fields_and_forms():
            field["field"] = field["form"].save(False)

        self.instance = super(CreditSubmissionForm, self).save(commit)

        for field in self.get_submission_fields_and_forms():
            # Ensure field form has the newly saved instance of the
            # CreditSubmission object
            if field["form"].__class__.__name__ != "DummyTabularForm":
                field["form"].instance.credit_submission = self.instance
                if field["field"].documentation_field.type != "calculated":
                    field["form"].save(commit)

        return self.instance

    def is_valid(self):
        """ Perform data validation on the form and return True if it
        all passes"""
        is_valid = True

        # Caution: validation order is, unfortunately, important here...
        #  the Submission Fields are validated fist, so their cleaned_data
        #  is available when we validate, and thus clean(), the Form itself.
        for field in self.get_submission_fields_and_forms():
            if not field["form"].is_valid():
                is_valid = False

        # use short-cut evaluation here so Form is not validated if
        # fields don't validate.
        return is_valid and super(CreditSubmissionForm, self).is_valid()

    def has_warnings(self):
        """ Returns True if this submission generated any warning
        messages during clean"""
        for field in self.get_submission_fields_and_forms():
            if field["form"].warnings:
                return True
        # assert:  none of the fields had warnings defined.
        return self.warnings

    def non_field_warnings(self):
        """ Returns formatted 'top-level' warnings (not associated
        with any field) for this form"""
        return self.warnings.as_ul() if self.warnings else u""

    def _validate_required_fields(self):
        """ Helper to do required field validation.  Should only be
        called when submission is complete!"""

        __cleaned_data = self.cleaned_data

        for field in self.get_submission_fields_and_forms():
            # only try to evaluate the requirement if the field doesn't already
            # have errors
            if field["form"].is_valid():
                try:
                    form_value = field["form"].cleaned_data.get("value")
                    doc_field = field["field"].documentation_field
                    if doc_field.is_upload():  # require upload fields can be
                        # blank so long as a file has
                        # been previously uploaded
                        form_value = form_value or field["field"].get_value()
                    if (
                        doc_field.is_required()
                        and form_value in (None, "", [])
                        and doc_field.type != "tabular"
                    ):
                        field["form"].append_error(
                            u"This field is required to " "mark this credit complete."
                        )
                except AttributeError:
                    assert False

    def _has_errors(self):
        """ Helper method to determine if any error were discovered
        during basic validation of each field"""
        for field in self.get_submission_fields_and_forms():
            if (
                "value" in field["form"]._errors
                or "metric_value" in field["form"]._errors
            ):
                return True
        # assert:  none of the fields had errors defined.
        return len(self.non_field_errors()) > 0

    def load_warnings(self):
        """
            Run custom validation to load any warnings onto the form

              - this is a bit sketchy b/c custom validation should
                only run once on a 'complete' instance, with no other
                basic validation errors.  CAREFUL!

              - call ONLY on GET (warnings are loaded by form
                validation on POST) for Complete instances!

            Loads warnings onto form and returns TRUE if any warnings
            are loaded.
        """
        (
            validation_errors,
            validation_warnings,
        ) = self.instance.credit.execute_validation_rules(self.instance)
        return self._load_warnings(validation_warnings)

    def _load_warnings(self, validation_warnings):
        """ Helper to eliminate duplicate code - warnings are loaded
        on both GET and POST"""
        has_warnings = False
        for field in self.get_submission_fields_and_forms():
            doc_field = field["field"].documentation_field
            if doc_field.identifier in validation_warnings:
                field["form"].append_warning(validation_warnings[doc_field.identifier])
                has_warnings = True

        if "top" in validation_warnings:
            self.warnings = WarningList([validation_warnings["top"]])
            has_warnings = True
        return has_warnings

    def _load_errors(self, validation_errors):
        """ Helper to load custom validation errors onto form """
        has_errors = False
        for field in self.get_submission_fields_and_forms():
            doc_field = field["field"].documentation_field
            if doc_field.identifier == "AY":
                pass
            if doc_field.identifier in validation_errors:
                field["form"].append_error(validation_errors[doc_field.identifier])
                has_errors = True

        if "top" in validation_errors:
            has_errors = True
        return has_errors

    def clean(self):
        """
            Assumes that a complete submission is being validated and cleaned.
        """
        cleaned_data = self.cleaned_data
        error_message = "This credit cannot be submitted as complete."

        self._validate_required_fields()
        has_error = self._has_errors()

        # only perform custom validation if the form had no basic
        # validation errors.  this is important because custom
        # validation_rules assume data is clean and complete.
        if not has_error:
            (
                validation_errors,
                validation_warnings,
            ) = self.instance.credit.execute_validation_rules(self)
            has_error = self._load_errors(validation_errors)
            has_warning = self._load_warnings(validation_warnings)
            if "top" in validation_errors:
                error_message = validation_errors["top"]

        if has_error:
            raise forms.ValidationError(error_message)

        return cleaned_data

    def get_submission_field_key(self):
        """
            Returns a dictionary with identifier:value for each
            submission field on this form Should be analogous to
            CreditSubmission.get_submission_field_key
        """
        key = {}
        for field in self.get_submission_fields_and_forms():
            doc_field = field["field"].documentation_field
            key[doc_field.identifier] = field["form"].cleaned_data.get("value")
            if doc_field.is_upload():
                # upload fields may be blank but still have a file that's
                # been previously uploaded
                key[doc_field.identifier] = (
                    key[doc_field.identifier] or field["field"].get_value()
                )
        return key


class ResponsiblePartyForm(LocalizedModelFormMixin, ModelForm):
    """
        When adding a new Responsible Party
    """

    class Meta:
        model = ResponsibleParty
        exclude = ["institution"]

    def form_name():
        return u"Responsible Party Form"

    form_name = staticmethod(form_name)

    def __init__(self, *args, **kwargs):
        super(ResponsiblePartyForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if self.fields[f].widget.__class__.__name__ == "TextInput":
                self.fields[f].widget.attrs.update({"size": 40})


class CreditUserSubmissionForm(CreditSubmissionForm):
    """
        A Credit Submission Form for a user submission, with Submission Status
    """

    submission_status = forms.CharField(widget=HiddenInput())

    class Meta:
        model = CreditUserSubmission
        fields = [
            "submission_notes",
            "responsible_party_confirm",
            "responsible_party",
            "submission_status",
            "applicability_reason",
        ]

    def __init__(self, *args, **kwargs):
        super(CreditUserSubmissionForm, self).__init__(*args, **kwargs)

        self.fields[
            "applicability_reason"
        ].queryset = self.instance.credit.applicabilityreason_set.all()
        self.fields["applicability_reason"].widget = HiddenInput()

        self.fields["submission_notes"].widget.attrs["style"] = "width: 600px;"

        # Select only the responsible parties associated with that institution
        self.fields[
            "responsible_party"
        ].queryset = (
            self.instance.subcategory_submission.category_submission.submissionset.institution.responsibleparty_set.all()
        )
        self.fields["responsible_party"].label = "Select Responsible Party"

        if (
            not self.instance.credit.get_creditset().has_optional_responsible_parties_feature
        ):
            self.fields["responsible_party_confirm"].label = (
                "The information included in the submission for this credit "
                "is accurate to the best of my knowledge."
            )
            self.fields["responsible_party_confirm"].label = mark_safe(
                '<span class="required_note" '
                '      title="This field is required to complete credit"> '
                "  * "
                "</span>" + self.fields["responsible_party_confirm"].label
            )

        for field in self:
            # add the onchange field_changed handler to inform users
            # of lost changes if a field already has an onchange
            # handler then just add to it.
            if field.field.widget.attrs.has_key("onchange"):
                field.field.widget.attrs["onchange"] = (
                    field.field.widget.attrs["onchange"] + ";field_changed(this);"
                )  # see include.js
            else:
                field.field.widget.attrs["onchange"] = "field_changed(this);"

    def clean(self):
        """
            Submission status depends on status of required fields -
            can't submit as complete when it's not!  An applicability
            reason must be selected if the submission status is set to
            'na'. Otherwise we want the reason to be None.
        """
        cleaned_data = self.cleaned_data
        status = cleaned_data.get("submission_status")
        reason = cleaned_data.get("applicability_reason")
        marked_complete = status == "c"
        error = False

        if not status:
            msg = u"Please tick the appropriate status for this submission."
            self._errors["submission_status"] = ErrorList([msg])
        if status == "na" and not reason:
            msg = u"Please select a reason why this does not apply."
            self._errors["applicability_reason"] = ErrorList([msg])
            error = marked_complete  # this is only an error if the
            # submission is marked complete.
        if not status == "na":
            cleaned_data["applicability_reason"] = None

        # Responsible party and responsible party confirm are required
        # if marked complete and responsible parties aren't optional for
        # this creditset.
        if (
            marked_complete
            and not self.instance.credit.get_creditset().has_optional_responsible_parties_feature
        ):
            rp = cleaned_data.get("responsible_party")
            if rp == None or rp == "":
                msg = u"This field is required to mark this credit complete."
                self._errors["responsible_party"] = ErrorList([msg])
                error = True
            rpc = cleaned_data.get("responsible_party_confirm")
            if not rpc:
                msg = u"This field is required to mark this credit complete."
                self._errors["responsible_party_confirm"] = ErrorList([msg])
                error = True

        # Only perform the overall form validation if the submission
        # is marked complete and if the
        if marked_complete:
            cleaned_data = super(CreditUserSubmissionForm, self).clean()

        return cleaned_data

    def has_responsible_party_error(self):
        """ Return True iff there is an error with the responsible
        party fields on this form"""
        return self._errors and (
            "responsible_party" in self._errors
            or "responsible_party_confirm" in self._errors
        )


class CreditUserSubmissionNotesForm(LocalizedModelFormMixin, ModelForm):
    """
        A Form for storing internal notes about a Credit Submission
    """

    internal_notes = forms.CharField(
        label="Only shared internally",
        widget=forms.Textarea(attrs={"style": "width: 600px;height: 300px;"}),
        required=False,
    )

    class Meta:
        model = CreditUserSubmission
        fields = [
            "internal_notes",
        ]


class SubmitSubmissionSetForm(LocalizedModelFormMixin, ModelForm):
    """
        A Form to collect data for submitting a credit set for a rating
    """

    class Meta:
        model = SubmissionSet
        fields = ["reporter_status", "submission_boundary", "presidents_letter"]

    def __init__(self, *args, **kwargs):
        super(SubmitSubmissionSetForm, self).__init__(*args, **kwargs)
        self.fields["presidents_letter"].required = True
        self.fields["submission_boundary"].required = True
        self.fields["submission_boundary"].label = (
            "Please describe the boundaries of the institution's "
            "STARS submission.  If any institution-owned, leased, "
            "or operated buildings or other holdings are omitted, "
            "briefly explain why."
        )


class BoundaryForm(LocalizedModelFormMixin, ModelForm):
    """
        A Form to update the boundary data for a submission
    """

    class Meta:
        model = SubmissionSet
        fields = ["submission_boundary"]

    def __init__(self, *args, **kwargs):
        super(BoundaryForm, self).__init__(*args, **kwargs)
        self.fields["submission_boundary"].required = True
        self.fields["submission_boundary"].label = (
            "Please describe the boundaries of the institution's "
            "STARS submission.  If any institution-owned, leased, "
            "or operated buildings or other holdings are omitted, "
            "briefly explain why."
        )
        self.fields["submission_boundary"].widget.attrs = {"cols": 60, "rows": 4}


class StatusForm(LocalizedModelFormMixin, ModelForm):
    """
        A Form to allow institutions to choose the Reporter status if
        they choose
    """

    class Meta:
        model = SubmissionSet
        fields = ["reporter_status"]


class LetterForm(LocalizedModelFormMixin, ModelForm):
    """
        A Form to accept the president's letter
    """

    class Meta:
        model = SubmissionSet
        fields = ["presidents_letter"]

    def clean_presidents_letter(self):
        data = self.cleaned_data["presidents_letter"]
        if (
            "1-presidents_letter" in self.files.keys()
            and (self.files["1-presidents_letter"].content_type != "application/pdf")
            and "test" not in sys.argv
        ):

            raise forms.ValidationError("This doesn't seem to be a PDF file")
        return data

    def __init__(self, *args, **kwargs):
        super(LetterForm, self).__init__(*args, **kwargs)
        self.fields["presidents_letter"].required = True
        self.fields["presidents_letter"].label = ""
        self.fields["presidents_letter"].widget.attrs = {
            "style": "display:none; padding-bottom: 10px;",
            "onchange": "$('#upload-file-info').html($(this).val());",
        }


class ContactsForm(LocalizedModelFormMixin, ModelForm):
    """
        The contact information for the institution's contacts
    """

    class Meta:
        model = Institution
        fields = [
            "contact_first_name",
            "contact_last_name",
            "contact_title",
            "contact_department",
            "contact_email",
            "executive_contact_first_name",
            "executive_contact_last_name",
            "executive_contact_title",
            "executive_contact_department",
            "executive_contact_email",
            "president_first_name",
            "president_last_name",
            "president_title",
            "president_email",
        ]

    def __init__(self, *args, **kwargs):
        super(ContactsForm, self).__init__(*args, **kwargs)
        for f in (
            "contact_first_name",
            "contact_last_name",
            "contact_title",
            "contact_department",
            "contact_email",
            "executive_contact_first_name",
            "executive_contact_last_name",
            "executive_contact_title",
            "executive_contact_department",
            "executive_contact_email",
        ):
            self.fields[f].required = True

        self.fields["contact_first_name"].label = "First Name"
        self.fields["contact_last_name"].label = "Last Name"
        self.fields["contact_title"].label = "Title"
        self.fields["contact_department"].label = "Department/Office"
        self.fields["contact_email"].label = "Email"
        self.fields["executive_contact_first_name"].label = "First Name"
        self.fields["executive_contact_last_name"].label = "Last Name"
        self.fields["executive_contact_title"].label = "Title"
        self.fields["executive_contact_department"].label = "Department/Office"
        self.fields["executive_contact_email"].label = "Email"
        self.fields["president_first_name"].label = "First Name"
        self.fields["president_last_name"].label = "Last Name"
        self.fields["president_title"].label = "Title"
        self.fields["president_email"].label = "Email"

        for field in self.fields.values():
            if field.required:
                field.label += " *"


class ApproveSubmissionForm(LocalizedModelFormMixin, ModelForm):
    class Meta:
        model = SubmissionSet
        fields = ["status"]

    def __init__(self, *args, **kwargs):
        super(ApproveSubmissionForm, self).__init__(*args, **kwargs)

        self.fields["status"].widget = forms.HiddenInput()

    def clean_status(self):
        """Status always flips to RATED."""
        return SUBMISSION_STATUSES["RATED"]


class CreditSubmissionReviewForm(LocalizedModelFormMixin, ModelForm):
    class Meta:
        model = CreditUserSubmission
        fields = ["review_conclusion"]


class CreditSubmissionReviewNotationForm(LocalizedModelFormMixin, ModelForm):
    class Meta:
        model = CreditSubmissionReviewNotation
        fields = ["kind", "comment", "send_email"]

    def __init__(self, *args, **kwargs):
        super(CreditSubmissionReviewNotationForm, self).__init__(*args, **kwargs)
        self.fields["comment"].widget.attrs["class"] = "row-fluid"


class CreditSubmissionReviewNotationInlineFormSet(InlineFormSet):
    model = CreditSubmissionReviewNotation
    extra = 1
    can_delete = True
    form_class = CreditSubmissionReviewNotationForm


class SendCreditSubmissionReviewNotationsEmailForm(Form):

    email_content = forms.CharField(
        label="", widget=forms.Textarea(attrs={"style": "width: 628px; height: 700px"})
    )

    class Meta:
        fields = ["email_content"]
