from stars.apps.institutions.models import Institution
from stars.apps.credits.models import DocumentationField, Unit
from stars.apps.submissions.models import NumericSubmission

hdd_df = DocumentationField.objects.get(pk=4999)
cdd_df = DocumentationField.objects.get(pk=4998)

# Fix the ratios
dd_metric = Unit.objects.get(pk=26)
dd_metric.ratio = 1.8
dd_metric.save()
dd_imperial = Unit.objects.get(pk=25)
dd_imperial.ratio = 0.5555555556
dd_imperial.save()


def recalculate_score(ss):
    """
    Extracted as a method so that it can be used from the command line
    """
    print ss

    # reconvert the metric value for both degree day fields

    # first find the fields that need to be converted
    ns_list = NumericSubmission.objects.by_submissionset(ss)
    try:
        hdd_sub = ns_list.get(documentation_field=hdd_df)
        cdd_sub = ns_list.get(documentation_field=cdd_df)
    except NumericSubmission.DoesNotExist:
        print "no NumericSubmmission found (submission may not be initialized)"
        return

    # run the conversion on those fields - save will update the metric val
    print "old hdd value: %s" % hdd_sub.value
    hdd_sub.save()
    print "new hdd value: %s" % hdd_sub.value

    print "old cdd value: %s" % cdd_sub.value
    cdd_sub.save()
    print "new cdd value: %s" % cdd_sub.value

    # recalculate the score for the credit itself
    cus = cdd_sub.credit_submission.creditusersubmission
    print "old credit score: %d" % cus.assessed_points
    cus.save()
    print "new credit score: %d" % cus.assessed_points

    # Recalcuate the score and rating
    old_score = ss.score
    old_rating = ss.rating

    if old_score is not None:
        ss.score = ss.get_STARS_score()
        ss.save()

        if ss.score != old_score:
            print "old score: %s" % old_score
            print "new score: %s" % ss.score

    if old_rating:
        # only update the rating if there is one

        new_rating = ss.get_STARS_rating(recalculate=True)
        if ss.rating != new_rating:
            ss.rating = new_rating
            ss.institution.current_rating = new_rating
            ss.institution.save()
            ss.save()

        if ss.rating != old_rating:
            print "old rating: %s" % old_rating
            print "new rating: %s" % ss.rating

    print


metric_qs = Institution.objects.filter(prefers_metric_system=True)
rated_qs = metric_qs.filter(rated_submission__creditset__version="2.1")
current_qs = metric_qs.filter(current_submission__creditset__version="2.1")

print "****** Rated SubmissionSets ******"
for i in rated_qs:
    recalculate_score(i.rated_submission)

print "****** Current SubmissionSets ******"
for i in current_qs:
    recalculate_score(i.current_submission)
