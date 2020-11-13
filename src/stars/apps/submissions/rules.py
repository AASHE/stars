import logical_rules

from stars.apps.institutions.rules import (institution_can_get_rated,
                                           institution_can_submit_report,
                                           user_has_access_level,
                                           user_is_institution_admin,
                                           user_is_participant)
from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import Boundary


def submission_is_editable(submission):
    """
        A submission is only editable if it is the current submission
        for the institution and isn't rated (just a check for now)
    """
    return (submission.status != 'r' and submission.status != 'f' and
            submission == submission.institution.current_submission)


logical_rules.site.register("submission_is_editable", submission_is_editable)


def submission_is_not_locked(submission):
    """
        Exposes SubmissionSet.is_locked.
    """
    return not submission.is_locked


logical_rules.site.register("submission_is_not_locked",
                            submission_is_not_locked)


def publish_credit_data(credit_submission):
    """
        Identifies whether a credit's fields should be published anywhere
    """
    return credit_submission.submission_status == 'c'


def user_can_preview_submission(user, submission):
    """
        Only rated submissions and the current submission data
    """
    if user_has_access_level(user, 'view', submission.institution):
        if (submission.status == 'r' or
                submission == submission.institution.current_submission):
            return True
    return False


logical_rules.site.register("user_can_preview_submission",
                            user_can_preview_submission)


def user_can_view_submission(user, submission):
    """
        If a submission isn't rated then only the institution's users
        can see the submission
    """
    if submission.status == 'r':
        return True
    return user_can_preview_submission(user, submission)


logical_rules.site.register("user_can_view_submission",
                            user_can_view_submission)


def user_can_view_export(user, submission):
    """
        As long as a user can view an institution's submissions they
        can export their rated submissions

        Only Full-Access users can export their current submissions

        All users can export their own snapshots

        All participants can export rated submissions
    """
    if submission.status == 'r':
        if user_is_participant(user):
            return True

    if user_has_access_level(user, 'view', submission.institution):
        if submission.status == 'r':
            return True
            # all institutions have access to exports for their own reports
        elif submission.institution.current_submission == submission:
            return True
        elif submission.status == 'f':
            return True
    return False


logical_rules.site.register("user_can_view_export",
                            user_can_view_export)


def user_can_download_certificate(user, submission):
    if submission.status == "r":
        if user.is_staff:
            return True
        # return (user_has_access_level(user, 'admin', submission.institution))
    return False


logical_rules.site.register("user_can_download_certificate",
                            user_can_download_certificate)


def user_can_edit_submission(user, submission):
    return (submission_is_editable(submission) and
            user_has_access_level(user, 'submit', submission.institution))


logical_rules.site.register("user_can_edit_submission",
                            user_can_edit_submission)


def user_can_edit_submission_or_is_admin(user, submission):
    return (user_can_edit_submission(submission=submission,
                                     user=user) or
            user_has_access_level(user=user,
                                  access_level='admin',
                                  institution=submission.institution))


logical_rules.site.register("user_can_edit_submission_or_is_admin",
                            user_can_edit_submission_or_is_admin)


def user_can_manage_submission(user, submission):
    return (submission_is_editable(submission) and
            user_has_access_level(user, 'admin', submission.institution))


logical_rules.site.register("user_can_manage_submission",
                            user_can_manage_submission)


def user_can_see_internal_notes(user, submission):
    return user_has_access_level(user, 'view', submission.institution)


logical_rules.site.register("user_can_see_internal_notes",
                            user_can_see_internal_notes)


def user_can_submit_for_rating(user, submission):
    """
        Rule defines whether a user (and institution) has
        privileges to submit a SubmissionSet for a rating
    """
    return (submission == submission.institution.current_submission and
            user_can_manage_submission(user, submission) and
            institution_can_get_rated(submission.institution))


logical_rules.site.register("user_can_submit_for_rating",
                            user_can_submit_for_rating)


def user_can_submit_report(user, submission):
    """
        Rule defines whether a user (and institution) has
        privileges to submit a SubmissionSet for a rating
    """
    return (submission == submission.institution.current_submission and
            user_can_manage_submission(user, submission) and
            institution_can_submit_report(submission.institution))


logical_rules.site.register("user_can_submit_report",
                            user_can_submit_report)


def user_can_submit_snapshot(user, submission):
    """
        A user can submit a snapshot for any submissionset with the
        "snapshot" feature, as long as...
            - they are an admin for the institution
            - the submission is their current submission or a report
    """
    if (submission.creditset.has_feature('snapshot') and
            user_is_institution_admin(user, submission.institution)):

        if (submission == submission.institution.current_submission or
                submission.is_rated()):
            return True

    return False


logical_rules.site.register("user_can_submit_snapshot",
                            user_can_submit_snapshot)


def user_can_migrate_version(user, institution):
    """
        Only institution admins can migrate a submission
    """
    if (institution.current_submission.creditset.version !=
            CreditSet.objects.get_latest().version):
        return user_has_access_level(user, 'admin', institution)
    else:
        return False


logical_rules.site.register("user_can_migrate_version",
                            user_can_migrate_version)


def user_can_migrate_data(user, institution):
    """
        Can this user do a data migration?
        Only institution admins can migrate a submission
    """
    return user_has_access_level(user, 'admin', institution)


logical_rules.site.register("user_can_migrate_data", user_can_migrate_data)


def user_can_migrate_from_submission(user, submission):
    """
        Only institution admins can migrate a submission

        Participants can migrate from Reports or Snapshots
        Respondents can only migrate from Reports
    """
    if user_has_access_level(user, 'admin', submission.institution):
        if submission.status == 'r' or submission.status == 'f':
            return True
    return False


logical_rules.site.register("user_can_migrate_from_submission",
                            user_can_migrate_from_submission)


def submission_has_boundary(submission):
    """
        Institutions can't submit for a rating unless they have a boundary
    """
    try:
        __ = submission.boundary
        return True
    except Boundary.DoesNotExist:
        return False


logical_rules.site.register("submission_has_boundary",
                            submission_has_boundary)


def submission_is_not_missing_required_boundary(submission):
    """
        Sometimes an Institution Boundary is required, and sometimes
        it's not.  If it's required, it has to be there.
    """
    if submission.creditset.has_boundary_feature:
        try:
            _ = submission.boundary
        except Boundary.DoesNotExist:
            return False
    return True


logical_rules.site.register("submission_is_not_missing_required_boundary",
                            submission_is_not_missing_required_boundary)


def required_credits_are_complete(submission):
    creditset = submission.creditset
    required_credits = creditset.get_credits().filter(is_required=True)
    credit_submissions = submission.get_credit_submissions()
    for credit in required_credits:
        credit_submission = credit_submissions.get(credit=credit)
        if credit_submission.submission_status != 'c':
            return False
    return True


logical_rules.site.register("required_credits_are_complete",
                            required_credits_are_complete)


def submission_has_scores(submission):
    """
        Indicates that the preview or reporting tool should show scores for
        this submission
    """
    if submission.status == 'r':
        return (submission.rating.name != "Reporter" and
                not submission.expired)
    elif submission.status == 'f':
        # don't show score for snapshots
        return False
    else:
        return submission.institution.is_participant


logical_rules.site.register("submission_has_scores", submission_has_scores)
