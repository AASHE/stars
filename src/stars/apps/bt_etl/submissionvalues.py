from datetime import timedelta
import io
import json
import time

from django.db.models import Q

from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import (
    SubmissionSet,
    SubcategorySubmission,
    CreditUserSubmission,
    NumericSubmission
)
from stars.apps.bt_etl.utils import get_datapoint_key


LATEST_CS = CreditSet.objects.get_latest()
MODEL_STRING = "stars_content.submissionvalue"
STARS_URL = "https://reports.aashe.org"


def extract_and_transform(filename='submissionvalue.json'):
    """
    [
    {
      "model": "stars_content.submissionvalue",
      "pk": 1,
      "fields": {
        data_point_key = models.CharField(max_length=16)
        title = models.CharField(max_length=128)
        short_title = models.CharField(max_length=64)
        is_numeric = models.BooleanField(default=True)
        imperial_value = models.FloatField(blank=True, null=True)
        imperial_units = models.CharField(max_length=16, blank=True, null=True)
        metric_value = models.FloatField(blank=True, null=True)
        metric_units = models.CharField(max_length=16, blank=True, null=True)
        text_value = models.TextField(blank=True, null=True)
        display_value = models.TextField(blank=True, null=True)
        detail_url = models.URLField()

        # Report information
        report_id = models.IntegerField()
        overall_score = models.FloatField()
        rating_name = models.CharField(max_length=16)
        rating_ordinal = models.IntegerField()
        is_latest = models.BooleanField()
        is_expired = models.BooleanField()
        report_url = models.URLField()

        # Institution Data
        inst_id = models.IntegerField()
        inst_name = models.CharField(max_length=255)
        inst_aashe_id = models.IntegerField(unique=True, blank=True, null=True)
        inst_fte = models.IntegerField(blank=True, null=True)
        inst_is_pcc_signatory = models.NullBooleanField(default=False)
        inst_is_member = models.NullBooleanField(default=False)
        inst_country = models.CharField(max_length=128, blank=True, null=True)
        inst_type = models.CharField(
            max_length=128, blank=True, null=True)
        inst_rating_name =
            models.CharField(max_length=16, blank=True, null=True)
        inst_rating_ordinal = models.IntegerField()
      }
    },
    ...]
    """

    start = time.time()
    with io.open(filename, 'w', encoding='utf-8') as f:

        f.write(u"[")
        qs = SubmissionSet.objects.filter(status='r')
        qs = qs.filter(creditset__version__startswith="2")
        qs = qs.select_related('creditset')
        total = qs.count()
        count = 0
        for ss in qs:
            count += 1
            print "%s of %s" % (count, total)
            obj_list = get_ss_obj(ss)

            inner_count = 0
            for o in obj_list:
                inner_count += 1
                r_json = json.dumps(o, ensure_ascii=False, indent=2)
                f.write(r_json)
                if (count != total or inner_count != len(obj_list)):
                    f.write(u",")
        f.write(u"]")
    print("total elapsed time: %s" %
          timedelta(seconds=int(time.time() - start)))


def get_ss_obj(ss):

    start_ss = time.time()
    obj_list = []

    # Add overall, category, subcategory, and credit scores
    etl_obj = get_ss_etl_obj(ss)
    if etl_obj:
        obj_list.append(etl_obj)

    for category in LATEST_CS.category_set.all():

        etl_obj = get_cat_etl_obj(category, ss)
        if etl_obj:
            obj_list.append(etl_obj)

        for subcategory in category.subcategory_set.all():

            etl_obj = get_sub_etl_obj(subcategory, ss)
            if etl_obj:
                obj_list.append(etl_obj)

            for credit in subcategory.credit_set.all():

                etl_obj = get_credit_etl_obj(credit, ss)
                if etl_obj:
                    obj_list.append(etl_obj)

                # for field in credit.numericsubmission_
                # set.filter(value__isnull=False):

                q_filter = Q(type='numeric') | Q(type='calculated')
                for df in credit.documentationfield_set.filter(q_filter):

                    etl_obj = get_df_etl_obj(df, ss)
                    if etl_obj:
                        obj_list.append(etl_obj)

    print("Report took: %s" % timedelta(seconds=int(time.time() - start_ss)))
    return obj_list


def get_ss_etl_obj(ss):
    print(ss)

    display_value = None
    if ss.rating.name == "Reporter":
        display_value = "Reporter"

    etl_obj = get_base_subdata(ss, ss)
    update_score_fields(
        etl_obj,
        ss,
        ss.creditset,
        "Overall Score",
        "Overall Score",
        ss.score,
        ss.get_scorecard_url(),
        "%", "%",
        display_value=display_value)
    return etl_obj


def get_cat_etl_obj(category, ss):

    if ss.creditset == LATEST_CS:
        current_category = category
    else:
        current_category = category.get_for_creditset(ss.creditset)
    # print("\t%s >> %s" % (category, current_category))
    # if this exists in this creditset
    if current_category:
        category_submission = ss.categorysubmission_set.get(
            category=current_category)

        display_value = None
        if ss.rating.name == "Reporter":
            display_value = "Reporter"

        etl_obj = get_base_subdata(category_submission, ss)
        r = category_submission.get_score_ratio()
        score = 0
        if r[1] > 0 and r[0]:
            score = (r[0] / r[1]) * 100
        update_score_fields(
            etl_obj,
            category_submission,
            category,
            "%s Score" % category.title,
            category.title,
            score,
            ss.get_scorecard_url(),
            "%", "%",
            display_value=display_value
        )
        return etl_obj
    return None


def get_sub_etl_obj(subcategory, ss):
    if ss.creditset == LATEST_CS:
        current_subcategory = subcategory
    else:
        current_subcategory = subcategory.get_for_creditset(ss.creditset)
    # print("\t\t%s >> %s" % (subcategory, current_subcategory))
    if current_subcategory:

        subcategory_submission = SubcategorySubmission.objects.get(
            subcategory=current_subcategory,
            category_submission__submissionset=ss)

        display_value = None
        if ss.rating.name == "Reporter":
            display_value = "Reporter"

        etl_obj = get_base_subdata(subcategory_submission, ss)

        if subcategory_submission.percentage_score:
            score = subcategory_submission.percentage_score * 100
        else:
            score = 0
        update_score_fields(
            etl_obj,
            subcategory_submission,
            subcategory,
            "%s Score" % subcategory.title,
            subcategory.title,
            score,
            ss.get_scorecard_url(),
            "%", "%",
            display_value=display_value
        )
        return etl_obj
    return None


def get_credit_etl_obj(credit, ss):
    if ss.creditset == LATEST_CS:
        current_credit = credit
    else:
        current_credit = credit.get_for_creditset(ss.creditset)

    if current_credit:

        cus = CreditUserSubmission.objects.get(
            credit=current_credit,
            subcategory_submission__category_submission__submissionset=ss)

        etl_obj = get_base_subdata(cus, ss)

        display_value = None
        if ss.rating.name == "Reporter":
            display_value = "Reporter"
        else:
            if cus.is_na():
                display_value = "Not Applicable"
            elif not cus.is_pursued():
                display_value = "Not Pursued"

        score = 0
        if (cus.assessed_points > 0 and
            cus.get_available_points(use_cache=True) > 0):  # noqa

            score = (float(cus.assessed_points) /
                     cus.get_available_points(use_cache=True) * 100)

        update_score_fields(
            etl_obj,
            cus,
            credit,
            "%s Score" % credit.title,
            credit.title,
            score,
            cus.get_scorecard_url(),
            "%", "%",
            display_value=display_value
        )
        return etl_obj
    return None


def get_df_etl_obj(df, ss):

    if ss.creditset == LATEST_CS:
        current_field = df
    else:
        current_field = df.get_for_creditset(ss.creditset)
    # print("\t\t\t\t%s >> %s" % (df, current_field))

    if current_field:

        find_path = [
            'credit_submission',
            'creditusersubmission',
            'subcategory_submission',
            'category_submission',
            'submissionset']
        lookup = {
            'documentation_field': current_field,
            "__".join(find_path): ss
        }
        try:
            field_submission = NumericSubmission.objects.get(**lookup)

            etl_obj = get_base_subdata(field_submission, ss)

            imperial_units = df.us_units.name if df.us_units else None
            metric_units = df.metric_units.name if df.metric_units else None
            if not imperial_units:
                if 'percentage' in df.title or "Percentage" in df.title:
                    metric_units = "%"
                    imperial_units = "%"

            cus = field_submission.credit_submission.creditusersubmission

            display_value = None
            if cus.is_na():
                display_value = "Not Applicable"
            elif not cus.is_pursued():
                display_value = "Not Pursued"

            update_score_fields(
                etl_obj,
                field_submission,
                df,
                df.title,
                df.title,
                field_submission.value if cus.is_pursued() else None,
                cus.get_scorecard_url(),
                imperial_units,
                metric_units,
                display_value=display_value
            )
            etl_obj['fields']['imperial_value'] = field_submission.value
            # this is to work around some inconsistencies in STARS
            if (imperial_units is None or imperial_units == "%" or
                    imperial_units == metric_units):
                etl_obj['fields']['metric_value'] = field_submission.value
            else:
                # values without units don't store a metric_value
                etl_obj['fields']['metric_value'] = (
                    field_submission.metric_value)

            return etl_obj
        except NumericSubmission.DoesNotExist:
            print("No submission found")
    return None


def get_base_subdata(obj, ss):

    i = ss.institution

    obj = {
        'model': MODEL_STRING,
        'pk': None,  # needs to be set by django
        'fields': {

            # Submission Properties
            'report_id': ss.id,
            'report_version': ss.creditset.version,
            'overall_score': ss.score,
            'rating_name': ss.rating.name,
            'rating_ordinal': ss.rating.minimal_score,
            'is_current': (
                ss.institution.rated_submission is not None and
                ss.id == ss.institution.rated_submission.id),
            'is_latest': (
                (ss.institution.rated_submission is not None and
                 ss.id == ss.institution.rated_submission.id)
                or
                (ss.institution.latest_expired_submission is not None and
                 ss.id == ss.institution.latest_expired_submission.id)
            ),
            'is_expired': ss.expired,
            'report_url': "%s%s" % (STARS_URL, ss.get_scorecard_url()),

            # Institution Properties
            'inst_id': i.id,
            'inst_name': i.name,
            'inst_aashe_id': i.aashe_id,
            'inst_fte': i.fte,
            'inst_is_pcc_signatory': i.is_pcc_signatory,
            'inst_is_member': i.is_member,
            'inst_country': i.country,
            'inst_type': i.institution_type,
            'inst_rating_name': None,
            'inst_rating_ordinal': None
        }
    }

    if i.current_rating:
        obj['fields']['inst_rating_name'] = i.current_rating.name
        obj['fields']['inst_rating_ordinal'] = i.current_rating.minimal_score

    return obj


def update_score_fields(etl_obj, obj, parent, title, short_title,
                        value, url, imperial_units, metric_units,
                        display_value=None):

    etl_obj['fields']['data_point_key'] = get_datapoint_key(parent)
    etl_obj['fields']['title'] = title
    etl_obj['fields']['short_title'] = short_title
    etl_obj['fields']['is_numeric'] = True
    etl_obj['fields']['imperial_value'] = value
    etl_obj['fields']['imperial_units'] = imperial_units
    # @todo - FIX!! - also... set to imperial value when no units or %
    etl_obj['fields']['metric_value'] = value
    etl_obj['fields']['metric_units'] = metric_units
    etl_obj['fields']['text_value'] = None
    etl_obj['fields']['detail_url'] = "%s%s" % (STARS_URL, url)
    etl_obj['fields']['display_value'] = display_value

    return etl_obj
