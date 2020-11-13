"""update_a_specific_set_of_scores.py

Updates a set of SubcategorySubmission, CategorySubmission scores that
is the product of the hard-coded list of CreditUserSubmission pk's.

Because Chris changed a Credit formula and the related
CreditUserSubmissions didn't recalculate automatically.  (Should
they?)  So I recalculated the CreditUserSubmissions, but not the
related SubcategorySubmission, CategorySubmission scores.  So that's
what this is for.

Not worrying about setting SubmissionSet.score, since it's not set for
any of these.

"""

from stars.apps.submissions.models import CreditUserSubmission


for credit_user_submission_pk in [542360, 543258, 548941, 560551]:
    cus = CreditUserSubmission.objects.get(pk=credit_user_submission_pk)

    print "getting SubcategorySubmission points ..."
    cus.subcategory_submission.points = (
        cus.subcategory_submission.get_claimed_points())
    cus.subcategory_submission.save()

    print "getting CategorySubmission score ..."
    cus.subcategory_submission.category_submission.score = (
        cus.subcategory_submission.category_submission.get_STARS_score())
    cus.subcategory_submission.category_submission.save()
