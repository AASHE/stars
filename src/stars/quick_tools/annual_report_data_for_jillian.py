from stars.apps.institutions.models import Subscription, Institution
from stars.apps.submissions.models import SubmissionSet

YEAR = 2012

first_time_count = 0
renewed_count = 0
international_count = 0
countries = {'unknown': 0}

for sub in Subscription.objects.all().filter(start_date__year=YEAR):
    # first time
    if sub.institution.subscription_set.filter(start_date__lte=sub.start_date).count() == 1:
        first_time_count += 1
    # renewed
    else:
        renewed_count += 1
    # international + countries
    if sub.institution.international:
        international_count += 1
        if sub.institution.country:
            if sub.institution.country in countries.keys():
                countries[sub.institution.country] += 1
            else:
                countries[sub.institution.country] = 1
        else:
            countries['unknown'] += 1
            print "Unknown: %s" % sub.institution

print "First Time Participants: %d" % first_time_count
print "Renewed Participants: %d" % renewed_count
print "International: %s" % international_count
print "Countries: %s" % countries

print "------------------------"

first_report_count = 0
second_report_count = 0
same_year_report_count = 0
rating_counts = {'Gold': 0, 'Silver': 0, 'Bronze': 0, 'Reporter': 0}

for ss in SubmissionSet.objects.all().filter(status='r').filter(date_submitted__year=YEAR):
    if ss.rating:
        rating_counts[ss.rating.name] += 1
    else:
        print "No Rating: %s" % ss

    if ss.institution.submissionset_set.filter(status='r').filter(date_submitted__lte=ss.date_submitted).count() == 1:
        first_report_count += 1
    else:
        second_report_count += 1

for i in Institution.objects.all():
    if i.submissionset_set.filter(status='r').filter(date_submitted__year=YEAR).count() > 1:
        same_year_report_count += 1

print "First Report: %d" % first_report_count
print "Second Report: %d" % second_report_count
print "*Two Reports in one year: %d" % same_year_report_count
print "Ratings: %s" % rating_counts

# first report
# second report
# Rating breakdown
