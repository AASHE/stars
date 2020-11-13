from stars.apps.submissions.models import SubmissionSet
from stars.apps.institutions.models import Institution

# Rated # Renewed # Missed # Extension
import csv
from datetime import datetime

def print_renewed():

    csvWriter = csv.writer(open('dashboard/renewed.csv', 'wb'))

    # Renewed

    columns = ["institution", "liaison email", "exec email", "first submission reg date", "first submission deadline", "rating", "next submission deadline", "rating"]
    csvWriter.writerow(columns)

    for i in Institution.objects.filter(enabled=True):

        # if there are two visible submissions
        row = []
        if i.submissionset_set.filter(is_visible=True).count() > 1:
            row.append(i)
            row.append(i.contact_email)
            row.append(i.executive_contact_email)
            for ss in i.submissionset_set.filter(is_visible=True):
                row.append(ss.date_registered)
                row.append(ss.rating)
            print row
            csvWriter.writerow(row)

def print_registration_dates():

    csvWriter = csv.writer(open('dashboard/reg_dates.csv', 'wb'))
    columns = ["institution", "date_registered",]
    csvWriter.writerow(columns)

    for i in Institution.objects.filter(enabled=True):
        row = [i,]
        for ss in i.submissionset_set.order_by('date_registered'):
            row.append(ss.date_registered)
            csvWriter.writerow(row)

print_renewed()
print_registration_dates()
