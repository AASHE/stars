from stars.apps.submissions.models import SubmissionSet, NumericSubmission
import math

ns_id_list = [
    349028,
    349029
]

for ns in NumericSubmission.objects.filter(id__in=ns_id_list):

    units = ns.documentation_field.units

    print ns.documentation_field.title
    print "current value:"
    print "%f %s" % (ns.value, units.name)

    if ns.value and units:
        # just convert the ones that have a value and units

        if units.is_metric:
            metric_units = units
            us_units = units.equivalent
        else:
            us_units = units
            metric_units = units.equivalent

        # some have the same units MMBtu, so we don't need to convert them
        if metric_units != us_units:
            # we don't have access to the convert method in the migration
            ns.metric_value = ns.value * metric_units.ratio

            # correct for flaot innacuracies during conversions
            roundup = math.ceil(ns.metric_value)
            if roundup - ns.metric_value < .01:
                ns.metric_value = roundup
            ns.save()

            print "new metric value: %f" % ns.metric_value
            print "%f %s" % (ns.value, us_units.name)
            print "%f %s" % (ns.metric_value, metric_units.name)

    # if ns.value and ns.documentation_field.units:
    #     # just convert the ones that have a value and units
    #
    #     print ns.documentation_field
    #
    #     metric_units = ns.documentation_field.metric_units
    #     us_units = ns.documentation_field.us_units
    #
    #     if metric_units != us_units:
    #         # some have the same units MMBtu, so we don't need to convert them
    #
    #         ns.metric_value = us_units.convert(ns.value)
    #
    #         print "%f %s" % (ns.value, us_units)
    #         print "%f %s" % (ns.metric_value, metric_units)
