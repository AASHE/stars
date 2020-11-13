import logical_rules

from stars.apps.third_parties.models import ThirdParty


def user_can_access_third_party(user, third_party):
    if not third_party:
        return False
    if user in third_party.authorized_users.all():
        return True
    return False
logical_rules.site.register("user_can_access_third_party", user_can_access_third_party)
