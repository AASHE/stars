from stars.apps.institutions.models import Institution
import json
import io

from stars.apps.bt_etl.utils import (
    get_institution_type,
    get_institution_control,
    get_institution_fte_cat)


def extract_and_transform(filename='institution.json'):

    MODEL_STRING = "stars_content.institution"

    """
    [
    {
      "model": "stars_content.institution",
      "pk": 1,
      "fields": {
        "name": "University of Somewhere",
        "aashe_id": 1,
        "fte": 1000,
        "is_pcc_signatory": true,
        "is_member": true,
        "country": "USA",
        "type": "Baccalaureate",
        "current_rating_name": "Gold",
        "current_rating_ordinal": 4
      }
    },
    ...]
    """

    obj_list = []

    # maybe should have some filters here on current_rating and
    # latest_expired_submission
    for i in Institution.objects.all().exclude(is_test_institution=True):

        # only export institutions with rated submissions
        if i.submissionset_set.filter(
                status='r', creditset__version__startswith="2"):

            inst_obj = {
                'model': MODEL_STRING,
                'pk': i.pk,
                'fields': {
                    'name': i.name,
                    'aashe_id': i.aashe_id,
                    'fte': get_institution_fte_cat(i),
                    'is_pcc_signatory': i.is_pcc_signatory,
                    'is_member': i.is_member,
                    'country': i.ms_institution.country,
                    'country_iso': i.ms_institution.country_iso,
                    'state': i.ms_institution.state,
                    'type': get_institution_type(i),
                    'control': get_institution_control(i),
                    'current_rating_name': None,
                    'current_rating_ordinal': None,
                    'latest_report_version': None
                }
            }

            if i.current_rating:
                inst_obj['fields']['current_rating_name'] = (
                    i.current_rating.name)
                inst_obj['fields']['current_rating_ordinal'] = (
                    i.current_rating.minimal_score)
                inst_obj['fields']['latest_report_version'] = (
                    i.rated_submission.creditset.version)
            elif i.latest_expired_submission:
                inst_obj['fields']['latest_report_version'] = (
                    i.latest_expired_submission.creditset.version)
            else:
                print("no latest report for %s" % i)
                inst_obj['fields']['latest_report_version'] = None

            obj_list.append(inst_obj)

    with io.open(filename, 'w', encoding='utf-8') as f:

        i_json = json.dumps(obj_list, ensure_ascii=False, indent=2)
        # print type(i_json)
        f.write(i_json)
