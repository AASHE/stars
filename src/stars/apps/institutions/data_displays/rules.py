import logical_rules

from stars.apps.institutions.rules import user_is_participant
from stars.apps.institutions.data_displays.models import AuthorizedUser

from datetime import date


def user_has_participant_displays(user):
    """
        User can access displays that require participant level access
    """
    if user_is_participant(user) or user.is_staff:
        return True

    try:
        account = AuthorizedUser.objects.get(email=user.email,
                                             start_date__lte=date.today(),
                                             end_date__gte=date.today())
        if account.participant_level:
            return True
    except AuthorizedUser.DoesNotExist:
        pass
    return False
logical_rules.site.register("user_has_participant_displays",
                            user_has_participant_displays)


def user_has_member_displays(user):
    """
        User can access displays that require member level access
    """
    if user.membersuiteportaluser.is_member:
        return True

    # all participants have member display access
    if user_has_participant_displays(user):
        return True

    try:
        account = AuthorizedUser.objects.get(email=user.email,
                                             start_date__lte=date.today(),
                                             end_date__gte=date.today())
        if account.member_level:
            return True
    except AuthorizedUser.DoesNotExist:
        pass
    return False
logical_rules.site.register("user_has_member_displays",
                            user_has_member_displays)
