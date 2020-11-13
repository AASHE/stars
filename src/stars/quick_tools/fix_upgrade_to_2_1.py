from stars.apps.institutions.models import Institution


for institution in Institution.objects.all().order_by("name"):

    previous_submission = institution.current_submission.migrated_from

    if not previous_submission:
        continue

    if not previous_submission.status == "rv":
        continue

    print institution

    print "\tcurr pk/version/status", institution.current_submission.pk,
    print institution.current_submission.creditset.version,
    print institution.current_submission.status

    print "\tprev pk/version/status", previous_submission.pk,
    print previous_submission.creditset.version,
    print previous_submission.status

    previous_submission.is_visible = True
    previous_submission.is_locked = False
    previous_submission.save()

    institution.current_submission = previous_submission
    institution.save()
