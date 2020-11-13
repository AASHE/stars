from stars.apps.institutions.models import StarsAccount, PendingAccount
from stars.apps.submissions.models import (PENDING_SUBMISSION_STATUS,
                                           SubmissionSet)
from stars.apps.credits.models import CreditSet

from datetime import date


def init_starsaccount(user, institution):
    """
        Add a StarsAccount to institution for user with the admin permission.
    """
    account = StarsAccount(user=user, institution=institution,
                           user_level='admin', is_selected=False,
                           terms_of_service=True)
    account.save()
    account.select()
    return account


def init_pending_starsaccount(email, institution):
    """
        Add a PendingAccount to institution for email with admin persmission.
    """
    account = PendingAccount(user_email=email, institution=institution,
                             user_level='admin', terms_of_service=True)
    account.save()
    return account


def init_submissionset(institution, user, date_function=None):
    """
        Initializes a submissionset for an institution and user.
    """
    if not date_function:
        reg_date = date.today()
    else:
        reg_date = date_function
    # Get the current CreditSet
    creditset = CreditSet.objects.get_latest()
    # Submission is due in one year
    submissionset = SubmissionSet(creditset=creditset,
                                  institution=institution,
                                  date_registered=reg_date,
                                  registering_user=user,
                                  status=PENDING_SUBMISSION_STATUS)
    submissionset.save()
    institution.current_submission = submissionset
    institution.save()
    return submissionset
