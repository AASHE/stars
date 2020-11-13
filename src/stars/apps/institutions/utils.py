import datetime

from stars.apps.institutions.models import Institution


def get_current_subscription(institution):

    today = datetime.date.today()

    try:
        current_subscription = institution.subscription_set.filter(
            start_date__lte=today,
            end_date__gte=today).order_by("start_date")[0]
    except IndexError:
        current_subscription = None

    return current_subscription


def update_institution_properties(institution):
    """Update one Institution's properties.

        Updates the following properties:

            current_subscription
            current_rating, rated_submission
    """
    institution.update_current_subscription()
    institution.update_current_rating()
    institution.save()


def update_all_institution_properties():
    """Update properties for all Institutions.
    """
    for institution in Institution.objects.all():
        update_institution_properties(institution=institution)
