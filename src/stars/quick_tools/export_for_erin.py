import datetime

from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import SubmissionSet


def get_header_row(credit_set):

    headers = ["STARS Version", "Institution", "Date Submitted",
               "Rating", "Total Score"]

    for category in credit_set.category_set.all():

        for subcategory in category.subcategory_set.all():
            headers.append(subcategory.title)

    return '\t'.join(headers)


def get_submission_set_rows(submission_sets):

    rows = []

    for submission_set in submission_sets:

        values = [submission_set.creditset.version,
                  submission_set.institution.name,
                  str(submission_set.date_submitted),
                  submission_set.rating.name,
                  str(submission_set.score)]

        for category_submission in submission_set.categorysubmission_set.all():

            for subcategory_submission in category_submission.subcategorysubmission_set.all():  # noqa
                values.append(str(subcategory_submission.points))

        rows.append('\t'.join(values))

    return rows


OUTPUT_FILENAME = "export_for_erin.tsv"


def main():

    with open(OUTPUT_FILENAME, "wb") as output_file:

        for credit_set in CreditSet.objects.all():

            submission_sets = SubmissionSet.objects.filter(
                creditset=credit_set,
                status="r",
                date_submitted__gt=datetime.date(2014, 12, 31))

            if not submission_sets:
                continue

            output_file.write(get_header_row(credit_set) + '\n')

            for row in get_submission_set_rows(submission_sets):
                output_file.write(row + '\n')

            output_file.write('\n')

    print "output sent to " + OUTPUT_FILENAME


if __name__ == "__main__":
    main()
