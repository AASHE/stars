import logical_rules
import sys
from datetime import datetime, date, timedelta

from django.db.models import Max

from stars.apps.institutions.models import StarsAccount


def user_has_access_level(user, access_level, institution):
    """
        Access levels are "admin", "submit", "view"
    """
    if not user.is_authenticated():
        return False

    if user.is_staff:
        return True
    try:
        account = StarsAccount.objects.get(institution=institution, user=user)
        if account.has_access_level(access_level):
            return True
    except StarsAccount.DoesNotExist:
        pass
    return False
logical_rules.site.register("user_has_access_level", user_has_access_level)


def user_is_participant(user):
    """
        Confirms this user has a StarsAccount for a participating institution
    """
    if not user.is_authenticated():
        return False

    if user.is_staff:
        return True

    for account in user.starsaccount_set.all():
        if account.institution.is_participant:
            return True

    return False
logical_rules.site.register("user_is_participant", user_is_participant)


def user_is_participant_or_member(user, is_member):
    """
        Check that the user is either a participant or a member

        is_member is passed in because it's stored in the session
    """
    if user_is_participant(user) or is_member:
        return True

    return False
logical_rules.site.register("user_is_participant_or_member",
                          user_is_participant_or_member)


def user_has_view_access(user, institution):
    """
        hardcoded version of user_has_access_level for view access
    """
    return user_has_access_level(user, "view", institution)
logical_rules.site.register("user_has_view_access", user_has_view_access)


def user_is_institution_admin(user, institution):
    return user_has_access_level(user, 'admin', institution)
logical_rules.site.register("user_is_institution_admin",
                            user_is_institution_admin)


def institution_can_get_rated(institution):
    if(institution.is_participant and
       institution.current_subscription.get_available_ratings() > 0 and
       institution.current_subscription.paid_in_full):
        return True
    return False
logical_rules.site.register("institution_can_get_rated",
                            institution_can_get_rated)


def institution_has_score_feature(institution):
    return institution.is_participant
logical_rules.site.register("institution_has_score_feature",
                            institution_has_score_feature)


def institution_has_internal_notes_feature(institution):
    return institution.is_participant
logical_rules.site.register("institution_has_internal_notes_feature",
                            institution_has_internal_notes_feature)


def institution_has_my_resources(institution):
    """
        If they're a participant, or if their most recent subscription ended
        less than 60 days prior or it is before september 2012
    """
    sept = date(year=2012, day=1, month=9)

    return True

    if institution.is_participant or date.today() < sept:
        return True
    else:
        td = timedelta(days=60)
        qs = institution.subscription_set.filter(end_date__lte=date.today())
        if qs:
            max_dict = qs.aggregate(Max("end_date"))
            if max_dict['end_date__max'] >= date.today() - td:
                return True
    return False
logical_rules.site.register("institution_has_my_resources",
                            institution_has_my_resources)


def institution_has_export(institution):
    return institution.is_participant
logical_rules.site.register("institution_has_export", institution_has_export)


def institution_has_my_reports(institution):
    return institution.is_participant
logical_rules.site.register("institution_has_my_reports",
                            institution_has_my_reports)


def institution_has_snapshot_feature(institution):
    return institution.current_submission.creditset.has_feature('snapshot')
logical_rules.site.register("institution_has_snapshot_feature",
                            institution_has_snapshot_feature)

# Data Displays
