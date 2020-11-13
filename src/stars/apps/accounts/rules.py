import logical_rules

def user_is_staff(user):
    """
        A rule wrapping user.is_staff
    """
    return user.is_staff
logical_rules.site.register("user_is_staff", user_is_staff)
