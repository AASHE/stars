"""
    Hint:
        $ PYTHONIOENCODING=UTF-8 ./manage.py shell
        In [1]: %run stars/quick_tools/reports/sci_export.py
"""
import datetime

from stars.apps.submissions.models import (CreditUserSubmission,
                                           SubmissionSet,
                                           SubcategorySubmission,
                                           SUBMISSION_STATUSES)
from stars.apps.credits.models import CreditSet


"""
- All published version 2.0 and 2.1 reports that are valid (i.e. not
Expired) at 11:59pm EST on June 30, 2017.
- Need to include reports that have been FINALIZED BUT NOT PUBLISHED,
i.e., those that submitted in May/June 2016 that have not yet addressed the
review results.
"""

def get_institution_institution_type_from_submission_set(submission_set):

    credit_user_submission = CreditUserSubmission.objects.get(
        credit__identifier="IC-1",
        subcategory_submission__category_submission__submissionset=submission_set)

    field = credit_user_submission.get_submission_fields()[0]

    return str(field.value)


DEADLINE = datetime.date(year=2017, month=6, day=30)


for cs in CreditSet.objects.filter(version__startswith="2"):

    ss_qs = SubmissionSet.objects.filter(creditset=cs)
    ss_qs = ss_qs.filter(
        status__in=[
            SUBMISSION_STATUSES["RATED"],
            SUBMISSION_STATUSES["REVIEW"]])

    ss_qs = ss_qs.filter(expired=False).filter(date_submitted__lte=DEADLINE)

    # Subcategory Scores Sheet
    filename = "%s_subcategory_scores.csv" % cs.version
    outfile = open(filename, 'w+')
    print "writing to: %s" % filename

    subcat_headers = [
        "Institution Name",
        "Status",
        "Submit Date",
        "STARS version",
        "Overall Score",
        "Rating",
        "Institution Type",
        "Country",
        "Nth Report (includes expired)",
        "# Reports Submitted (includes expired)",
    ]

    # Add the subcategories
    subcategories = []  # stored for later reference
    for cat in cs.category_set.all():
        for sub in cat.subcategory_set.all():
            subcategories.append(sub)
            subcat_headers.append("%s points claimed" % sub.title)
            subcat_headers.append("%s points available" % sub.title)

    print >>outfile, "\t".join(subcat_headers)

    for ss in ss_qs:
        row = []
        row.append(ss.institution.name)
        row.append(ss.status)
        row.append(unicode(ss.date_submitted))
        row.append(ss.creditset.version)
        row.append("%f.2" % ss.score if ss.score else "0.00")
        row.append(ss.rating.name)
        row.append(get_institution_institution_type_from_submission_set(ss))
        row.append(ss.institution.country)

        # calculated total reports submitted
        all_reports = ss.institution.submissionset_set.filter(
            status__in=[
                SUBMISSION_STATUSES["RATED"],
                SUBMISSION_STATUSES["REVIEW"]]
            ).order_by('date_submitted').values_list('id', 'date_submitted')
        # print all_reports
        # print ss.id
        index = [x[0] for x in all_reports].index(ss.id)

        row.append(unicode(index + 1))
        row.append(unicode(len(all_reports)))

        for sub in subcategories:
            subcatsub = SubcategorySubmission.objects.filter(
                subcategory=sub).get(category_submission__submissionset=ss)
            row.append(unicode(subcatsub.get_claimed_points()))
            row.append(unicode(subcatsub.get_adjusted_available_points()))

        print >>outfile, u"\t".join(row)

    outfile.close()
