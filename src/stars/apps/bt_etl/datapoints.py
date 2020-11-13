import io
import json

from stars.apps.credits.models import CreditSet
from django.db.models import Q


MODEL_STRING = "stars_content.datapoint"


def extract_and_transform(filename='datapoint.json'):
    """
    [
    {
      "model": "stars_content.datapoint",
      "pk": 1,
      "fields": {
        "parent": null,
        "title": "Category 1",
        "type": "category",
        "key": "cat_1",
        "ordinal": 1
      }
    },
    ...]
    """

    obj_list = []

    cs = CreditSet.objects.get_latest()

    def get_datapoint(obj, type, parent, is_numeric, metric_units=None, imperial_units=None):
        return {
            'model': MODEL_STRING,
            'pk': obj.pk,
            'fields': {
                'parent': parent,
                'title': obj.title,
                'type': type,
                'key': "%s_%s" % (type, obj.id),
                'ordinal': obj.ordinal,
                'is_numeric': is_numeric,
                'metric_units': metric_units,
                'imperial_units': imperial_units
            }
        }

    for cat in cs.category_set.all():
        if not cat.title == "Institutional Characteristics":
            obj_list.append(get_datapoint(cat, "cat", None, True, "%", "%"))

            for sub in cat.subcategory_set.all():
                obj_list.append(get_datapoint(
                    sub, "sub", cat.id, True, "%", "%"))

                for credit in sub.credit_set.all():
                    obj_list.append(get_datapoint(
                        credit, "cred", sub.id, True, "%", "%"))

                    q_filter = Q(type='numeric') | Q(type='calculated')
                    for df in credit.documentationfield_set.filter(q_filter):
                        imperial_units = df.us_units.name if df.us_units else None
                        metric_units = df.metric_units.name if df.metric_units else None
                        if not imperial_units:
                            if 'percentage' in df.title or "Percentage" in df.title:
                                metric_units = "%"
                                imperial_units = "%"
                        obj_list.append(get_datapoint(
                            df, "field", credit.id, True, metric_units, imperial_units))

    with io.open(filename, 'w', encoding='utf-8') as f:

        r_json = json.dumps(obj_list, ensure_ascii=False, indent=2)
        # print type(r_json)
        f.write(r_json)
