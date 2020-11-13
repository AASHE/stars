from django.db.models import Max
from django.utils.encoding import smart_unicode, smart_str

from stars.apps.submissions.models import DataCorrectionRequest
from stars.apps.third_parties.models import ThirdParty

import csv

tp = ThirdParty.objects.get(pk=1)
tp_inst_list = tp.get_snapshot_institutions()

csvWriter = csv.writer(open('dcr_export.csv', 'wb'))

columns = [
            "Institution",
            "Date",
            "Field",
            "New Value",
            "Explanation"
           ]

csvWriter.writerow(columns)

# go through all data corrections
for dcr in DataCorrectionRequest.objects.order_by('date'):
    # confirm they shared with Princeton
    i = dcr.reporting_field.get_institution()
    if i in tp_inst_list:

        row = [
                smart_str(i),
                smart_str(dcr.date),
                smart_str(dcr.reporting_field),
                smart_str(dcr.new_value),
                smart_str(dcr.explanation)
               ]

        csvWriter.writerow(row)

#        print i
#        print "Correction Date: %s" % dcr.date

        # check that the date of the dcr is after
        # the last snapshot taken by that institution
#        qs = i.submissionset_set.filter(status='f')
#        if qs:
#            last_snapshot_date = qs.aggregate(Max('date_submitted'))['date_submitted__max']
##            print "Last Snapshot Date: %s" % last_snapshot_date
#            if dcr.date.date() > last_snapshot_date:
#                print i
#                print "Field:"
#                print dcr.reporting_field
#                print "New Value:"
#                print dcr.new_value
#                print "Explanation:"
#                print dcr.explanation
