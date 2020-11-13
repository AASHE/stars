import copy
import datetime

from django.core.exceptions import ObjectDoesNotExist

from stars.apps.credits.models import CreditSet, DocumentationField
from stars.apps.submissions.models import (Boundary,
                                           ChoiceSubmission,
                                           CREDIT_SUBMISSION_STATUSES,
                                           CreditUserSubmission,
                                           MultiChoiceSubmission,
                                           NumericSubmission,
                                           PENDING_SUBMISSION_STATUS,
                                           SubcategorySubmission,
                                           SubmissionSet)


def bumped_tabular_embedded_fields(tabular_field):
    """
        Returns a list of lists that maps the fields in
        tabular_field['fields'] to the pk's of those fields
        that succeeded them.

        E.g., given:

            DocField1.pk is 1

            DocField2.pk is 2; DocField2.previous_version = 1

            TabField1.fields[['1']]

            bump_tabular_fields(TabField1) returns TabField1 with
            fields reset to [['2']]
    """
    new_fields = []
    for row in tabular_field.tabular_fields['fields']:
        new_row = []
        for col in row:
            new_col = str(DocumentationField.objects.get(
                previous_version=int(col)).pk)
            new_row.append(new_col)
        new_fields.append(new_row)
    return new_fields


def migrate_creditset(old_cs, new_version_name, release_date):
    """
        Copy a creditset to a new version and update `previous_version`
        references
    """
    def migrate_obj(old_obj, prop_dict, previous=True):

        new_obj = copy.copy(old_obj)
        new_obj.id = None
        if previous:
            new_obj.previous_version = old_obj
        for k, v in prop_dict.items():
            setattr(new_obj, k, v)
        new_obj.save()
        return new_obj

    new_cs = migrate_obj(old_cs, {'version': new_version_name,
                                  'release_date': release_date})

    # ratings
    for r in old_cs.rating_set.all():
        migrate_obj(r, {'creditset': new_cs})

    # categories, subcategories, credits, applicability reasons,
    # documentation field, choice
    for cat in old_cs.category_set.all():
        new_cat = migrate_obj(cat, {'creditset': new_cs})

        for sub in cat.subcategory_set.all():
            new_sub = migrate_obj(sub, {'category': new_cat})

            for credit in sub.credit_set.all():
                new_c = migrate_obj(credit, {'subcategory': new_sub})

                for ar in credit.applicabilityreason_set.all():
                    migrate_obj(ar, {'credit': new_c})

                for field in credit.documentationfield_set.order_by('-id'):

                    new_f = migrate_obj(field, {'credit': new_c})

                    for choice in field.choice_set.all():
                        migrate_obj(choice,
                                    {'documentation_field': new_f})

                # for cts in CreditTestSubmission.objects.filter(credit=credit):
                #     new_cts = CreditTestSubmission(
                #         credit=new_c,
                #         expected_value=cts.expected_value)
                #     new_cts.save()

                #     for dfs in cts.get_submission_fields():
                #         new_field = dfs.documentation_field.next_version
                #         dfs_class = DocumentationFieldSubmission.get_field_class(
                #             dfs.documentation_field)
                #         if dfs_class:
                #             new_dfs = dfs_class(documentation_field=new_field,
                #                                 value=dfs.value,
                #                                 credit_submission=new_cts)
                #             new_dfs.save()

    for tabular_field in DocumentationField.objects.filter(
            credit__subcategory__category__creditset=new_cs,
            type='tabular'):
        tabular_field.tabular_fields['fields'] = (
            bumped_tabular_embedded_fields(tabular_field))
        tabular_field.save()

    return new_cs


def create_ss_mirror(old_submissionset,
                     new_creditset=None,
                     registering_user=None,
                     keep_innovation=False,
                     keep_status=False):
    """

        and migrates the data from old_submissionset leaving it unchanged

        takes an optional creditset to use
    """
    new_submissionset = new_submissionset_for_old_submissionset(
        old_submissionset=old_submissionset,
        new_creditset=new_creditset,
        registering_user=registering_user)
    return migrate_submission(old_submissionset,
                              new_submissionset,
                              keep_innovation=keep_innovation,
                              keep_status=keep_status)


def new_submissionset_for_old_submissionset(old_submissionset,
                                            new_creditset=None,
                                            registering_user=None):
    """
        Returns a new SubmissionSet based on existing submissionset
        `old_submissionset`, using CreditSet `new_creditset` or, if
        not specified, the latest CreditSet.

        If `registering_user` is provided, it's tacked on to the
        new SubmissionSet, otherwise, the registering_user from
        `old_submissionset` is copied.
    """
    new_creditset = new_creditset or CreditSet.objects.get_latest()

    new_submissionset = SubmissionSet(
        creditset=new_creditset,
        institution=old_submissionset.institution,
        date_registered=old_submissionset.date_registered,
        status=PENDING_SUBMISSION_STATUS,
        is_locked=True,
        is_visible=False,
        date_created=datetime.date.today())

    new_submissionset.registering_user = (registering_user or
                                          old_submissionset.registering_user)

    new_submissionset.save()

    return new_submissionset


def migrate_ss_version(old_submissionset, new_creditset):
    """
        Migrate a SubmissionSet from one CreditSet version to another

        - Locks the old submission.
        - Creates the new hidden one
        - Migrates the data
        - Hides the old one
        - Unhides the new one and makes it active
        - Returns the new submissionset
    """
    if not old_submissionset.is_locked:
        old_submissionset.is_locked = True
        old_submissionset.save()

    new_submissionset = create_ss_mirror(old_submissionset, new_creditset)

    new_submissionset.is_locked = False
    new_submissionset.is_visible = True
    new_submissionset.migrated_from = old_submissionset
    new_submissionset.save()

    # make active submission set
    new_submissionset.institution.set_active_submission(new_submissionset)

    old_submissionset.is_visible = False
    old_submissionset.save()

    return new_submissionset


def migrate_submission(old_submissionset,
                       new_submissionset,
                       keep_status=False,
                       keep_innovation=False):
    """
        Migrate data from one SubmissionSet to another

        Keeping the status will keep the submission status the same
        and transfer all the properties UNLESS the submissionsets
        are of different versions.

        Note: don't migrate Innovations credits if the previous submission
        is rated, unless indicated (e.g., in the case of a snapshot).
    """
    # if the old SubmissionSet hasn't been initialized we don't have
    # to do much:
    if old_submissionset.categorysubmission_set.count() == 0:
        new_submissionset.migrated_from = old_submissionset
        new_submissionset.save()
        return new_submissionset

    # check if we can migrate innovation data
    if old_submissionset.status != "r":
        # Always migrate Innovation credits for unrated submissions.
        migrate_innovation_credits = True
    else:
        # For rated submissions, migrate Innovation credits
        # when keep_innovation is True, don't migrate them when
        # keep_innovation is False.
        migrate_innovation_credits = keep_innovation

    # Since there is currently no change necessary with the category
    # we will ignore it.

    # Get all SubcategorySubmissions in the new SubmissionSet ...
    subcategory_submissions = SubcategorySubmission.objects.filter(
        category_submission__submissionset=new_submissionset)

    # ... and maybe filter out the Innovation credits:
    if not migrate_innovation_credits:
        subcategory_submissions = subcategory_submissions.exclude(
            subcategory__slug="innovation")

    for subcategory_submission in subcategory_submissions:
        # get the related subcategory
        prev_subcategory = (
            subcategory_submission.subcategory.get_for_creditset(
                old_submissionset.creditset))

        # if it has a previous version
        if prev_subcategory:
            try:
                old_subcategory_submission = (
                    SubcategorySubmission.objects.get(
                        category_submission__submissionset=old_submissionset,
                        subcategory=prev_subcategory))
                subcategory_submission.description = (
                    old_subcategory_submission.description)
                subcategory_submission.save()
            except SubcategorySubmission.DoesNotExist:
                # This must be a new subcategory
                continue
        else:
            pass

    # Get all the CreditUserSubmission for the new SubmissionSet ...
    credit_user_submissions_to_migrate = CreditUserSubmission.objects.filter(
        subcategory_submission__category_submission__submissionset=new_submissionset)

    # ... and maybe filter out Innovation Credits:
    if not migrate_innovation_credits:
        credit_user_submissions_to_migrate = (
            credit_user_submissions_to_migrate.exclude(
                subcategory_submission__subcategory__slug="innovation"))

    for credit_user_submission_to_migrate in (
            credit_user_submissions_to_migrate):

        # find the parent credit
        prev_credit = credit_user_submission_to_migrate.credit.get_for_creditset(
            old_submissionset.creditset)

        if prev_credit:
            try:
                old_credit_user_submission = CreditUserSubmission.objects.get(
                    subcategory_submission__category_submission__submissionset=old_submissionset,
                    credit=prev_credit)

                credit_user_submission_to_migrate.last_updated = (
                    old_credit_user_submission.last_updated)
                try:
                    credit_user_submission_to_migrate.user = (
                        old_credit_user_submission.user)
                except:
                    credit_user_submission_to_migrate.user = None
                credit_user_submission_to_migrate.internal_notes = (
                    old_credit_user_submission.internal_notes)
                credit_user_submission_to_migrate.submission_notes = (
                    old_credit_user_submission.submission_notes)
                credit_user_submission_to_migrate.responsible_party = (
                    old_credit_user_submission.responsible_party)

                if (keep_status and
                    old_submissionset.creditset.version == new_submissionset.creditset.version):

                    credit_user_submission_to_migrate.submission_status = (
                        old_credit_user_submission.submission_status)
                    credit_user_submission_to_migrate.responsible_party_confirm = (
                        old_credit_user_submission.responsible_party_confirm)
                    credit_user_submission_to_migrate.applicability_reason = (
                        old_credit_user_submission.applicability_reason)
                    credit_user_submission_to_migrate.assessed_points = (
                        old_credit_user_submission.assessed_points)
                else:
                    if credit_user_submission_to_migrate.credit.is_opt_in:
                        # The opt-in-ed-ness of an opt_in credit doesn't
                        # carry forward:
                        credit_user_submission_to_migrate.submission_status = (
                            CREDIT_SUBMISSION_STATUSES["NOT_APPLICABLE"])
                    elif (old_credit_user_submission.submission_status !=
                          CREDIT_SUBMISSION_STATUSES["NOT_STARTED"]):
                        credit_user_submission_to_migrate.submission_status = (
                            CREDIT_SUBMISSION_STATUSES["IN_PROGRESS"])
                    else:
                        credit_user_submission_to_migrate.submission_status = (
                            CREDIT_SUBMISSION_STATUSES["NOT_STARTED"])

            except CreditUserSubmission.DoesNotExist:
                continue

        # get all the fields in this credit
        submission_fields = credit_user_submission_to_migrate.get_submission_fields()  # noqa

        for submission_field in submission_fields:

            prev_documentation_field = (
                submission_field.documentation_field.get_for_creditset(
                    old_submissionset.creditset))

            if prev_documentation_field:
                submission_field_class = submission_field.__class__
                if submission_field_class.__name__ == 'TabularSubmissionField':
                    # don't migrate the tabular wrappers,
                    # cause they don't actually exist
                    pass
                else:
                    try:
                        prev_cus = CreditUserSubmission.objects.get(
                            credit=prev_documentation_field.credit,
                            subcategory_submission__category_submission__submissionset=old_submissionset)  # noqa
                        old_submission_field = (
                            submission_field_class.objects.get(
                                documentation_field=prev_documentation_field,
                                credit_submission=prev_cus))
                        if isinstance(submission_field,
                                      ChoiceSubmission):
                            if old_submission_field.value is not None:
                                old_selection = old_submission_field.value.choice  # noqa
                                new_choices = (
                                    submission_field.get_choice_queryset())
                                try:
                                    new_selection = new_choices.get(
                                        choice=old_selection)
                                except ObjectDoesNotExist:
                                    submission_field.value = None
                                else:
                                    submission_field.value = new_selection
                        elif isinstance(submission_field,
                                        MultiChoiceSubmission):
                            # Hey there, sorry, but this bit of code
                            # -- the part that handles
                            # MultiChoiceSubmissions -- hasn't been
                            # tested.
                            new_choices = (
                                submission_field.get_choice_queryset())
                            old_selections = old_submission_field.get_value()
                            for old_selection in old_selections:
                                try:
                                    new_selection = new_choices.get(
                                        choice=old_selection)
                                except ObjectDoesNotExist:
                                    pass
                                else:
                                    submission_field.value.add(new_selection)
                        else:
                            submission_field.value = old_submission_field.value

                        if isinstance(submission_field, NumericSubmission):
                            submission_field.metric_value = old_submission_field.metric_value
                            submission_field.save(
                                recalculate_related_calculated_fields=False)
                        else:
                            submission_field.save()

                    except submission_field_class.DoesNotExist:
                        pass

        # Calculate calculated fields after all the other
        # submission fields have values.
        for submission_field in submission_fields:
            if submission_field.documentation_field.type == 'calculated':
                submission_field.calculate(log_exceptions=False)
                submission_field.save(
                    recalculate_related_calculated_fields=False,
                    log_calculation_exceptions=False)

        # don't save until all the fields are updated
        credit_user_submission_to_migrate.save()

    try:
        new_boundary = copy.copy(old_submissionset.boundary)
        new_boundary.submissionset = new_submissionset
        new_boundary.id = None
        new_boundary.save()
    except Boundary.DoesNotExist:
        pass

    return new_submissionset
