from stars.apps.institutions.models import Institution

#  Number of institutions who renewed after getting a rating
#  average ratio of ratings to subscriptions
ratio_list = []
i_with_more_subs_count = 0
i_with_2_ratings_count = 0
for i in Institution.objects.filter(current_rating__isnull=False):
    subscription_count = i.subscription_set.all().count()
    rating_count = i.submissionset_set.filter(status='r').count()
#    print "%s %d:%d" % (i, subscription_count, rating_count)
    ratio_list.append(subscription_count / rating_count)
    if subscription_count > rating_count:
        i_with_more_subs_count += 1
    if rating_count > 1:
        i_with_2_ratings_count += 1

print "Average Ratio: %f" % (sum(ratio_list) / float(len(ratio_list)))
print "Total Institutions: %d" % len(ratio_list)
print "Institutions with more subscriptions: %d" % i_with_more_subs_count
print "Institutions with more than one rating: %d" % i_with_2_ratings_count

#  How would a decrease affect the bottom line
print "Value of doubled-up institutions ($450/per): $%.0f" % (i_with_more_subs_count * 450)
print "If 50 percent of institutions who doubled up cancel: $%.0f" % (i_with_more_subs_count * 225)
