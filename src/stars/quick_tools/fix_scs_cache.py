"""fix_scs_cache.py

There are some SubcategorySubmissions with incorrect points values
(Spring 2016).

points is a field whose job is to cache the output of
SubcategorySubmission.get_claimed_points().

This script intends to fix the data.

First, we clear the SubcategorySubmission.points fields we find that
are incorrect.

Since SubcategorySubmission.points can be used in calculating overall
SubmissionSet scores, we then recalculate the scores and ratings for
all related SubmissionSets.

(In an earlier version, we cleared all SubcategorySubmission.points
values and then recalculated the scores for those related
SubmissionSets.  This resulted in a larger set of submissions with
incorrect scores, though all but one were *not* because a
SubcategorySubmission had in incorrectly cached points value.)

Output is in org-mode format.

"""
from stars.apps.submissions.models import SubcategorySubmission

submission_sets = set()

print "SubcategorySubmissions with bad points cache"
print ("| scs id | subcategory submission | submission set "
       "| orig score | new score | diff |")
print ("|-")

for scs in SubcategorySubmission.objects.exclude(points__isnull=True):

    orig_points = round(scs.points, 2)

    scs.points = None
    scs.save()

    new_points = round(scs.get_claimed_points(), 2)

    if orig_points != new_points:
        submission_sets.add(scs.category_submission.submissionset)
        print "| {id} | {scs} | {ss} | {op} | {np} | {diff} |".format(
            id=scs.id, scs=scs, ss=scs.category_submission.submissionset,
            op=orig_points, np=new_points, diff=(new_points - orig_points))


print "{n} SubmissionSets to re-score and re-rate.".format(
    n=len(submission_sets))
print ("| # | ss id | submission set | orig score | new score | diff "
       "| orig rating | new rating |")
print ("|-")

for i, ss in enumerate(submission_sets):

    orig_score = round(ss.score, 2)
    orig_rating = ss.rating

    new_score = round(ss.get_STARS_score(recalculate=True), 2)
    new_rating = ss.get_STARS_rating(recalculate=True)

    if (new_score != orig_score) or (new_rating != orig_rating):

        print ("| {i} | {id} | {ss} | {os} | {ns} | {diff} "
               "| {or_} | {nr} |").format(
                   i=i, id=ss.id, ss=ss,
                   os=orig_score, ns=new_score, diff=(new_score - orig_score),
                   or_=orig_rating, nr=new_rating)

        if (new_score != orig_score):
            ss.score = new_score

        if orig_rating.name != 'Reporter' and (new_rating != orig_rating):
            ss.current_rating = new_rating

        ss.save()
