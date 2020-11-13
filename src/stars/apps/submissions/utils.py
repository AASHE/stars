from stars.apps.submissions.models import DocumentationFieldSubmission


def get_documentation_field_submissions(credit_user_submission,
                                        source_db="default"):
    """Returns DocumentationFieldSubmissions for `credit_user_submission`.

    TabularSubmissionFields are filtered.

    Unlike CreditSubmission.get_submission_fields(), which can create
    DocumentationFieldSubmissions, this function will never create
    DocumentationFieldSubmissions.

    """
    documentation_field_submissions = []

    for documentation_field in (
            credit_user_submission.credit.documentationfield_set.using(
                source_db).all()):
        SubmissionFieldModelClass = (
            DocumentationFieldSubmission.get_field_class(
                documentation_field))
        if SubmissionFieldModelClass:
            try:
                submission_field = SubmissionFieldModelClass.objects.using(
                    source_db).get(documentation_field=documentation_field,
                                   credit_submission=credit_user_submission)
            except SubmissionFieldModelClass.DoesNotExist:
                pass
            else:
                documentation_field_submissions.append(submission_field)
        else:
            # TabularSubmissionField, just skip it.
            pass

    return documentation_field_submissions
