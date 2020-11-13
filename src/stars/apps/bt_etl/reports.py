from datetime import datetime
import io
import json

from stars.apps.submissions.models import SubmissionSet


def extract_and_transform(filename='report.json'):

    MODEL_STRING = "stars_content.report"
    STARS_URL = "https://reports.aashe.org"

    """
    [
    {
      "model": "stars_content.report",
      "pk": 1,
      "fields": {
        "institution": 1,
        "name": "Aug 2017 (2.0)",
        "date_submitted": "2017-08-12",
        "long_name": "University of Somewhere - August 3, 2017 (2.0)",
        "rating_name": "Gold",
        "rating_ordinal": 4,
        "version_name": "2.0",
        "version_ordinal": 4,
        "is_current": true,
        "is_latest": true
      }
    },
    ...]
    """

    obj_list = []

    qs = SubmissionSet.objects.get_rated()
    qs = qs.filter(creditset__version__startswith="2")

    for ss in qs:

        ss_obj = {
            'model': MODEL_STRING,
            'pk': ss.pk,
            'fields': {
                'institution': ss.institution.id,
                'name': "%s (%s)" % (
                    datetime.strftime(ss.date_submitted, "%b %G"),
                    ss.creditset.version),
                'date_submitted': ss.date_submitted.isoformat(),
                'long_name':
                    "%s - %s (%s)" % (
                        ss.institution.name,
                        datetime.strftime(ss.date_submitted, "%B %e, %G"),
                        ss.creditset.version),
                'rating_name': ss.rating.name,
                'rating_ordinal': ss.rating.minimal_score,
                'version_name': ss.creditset.version,
                'version_ordinal': ss.creditset.id,
                'is_current': ss == ss.institution.rated_submission,
                'is_latest': (
                    ss == ss.institution.rated_submission or
                    (
                        not ss.institution.rated_submission and
                        ss.institution.latest_expired_submission != None and
                        ss.id == ss.institution.latest_expired_submission.id
                    )
                ),
                'is_expired': ss.expired,
                'report_url': "%s%s" % (STARS_URL, ss.get_scorecard_url())
            }
        }

        obj_list.append(ss_obj)

    with io.open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(obj_list, ensure_ascii=False, indent=2))
