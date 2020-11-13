from stars.apps.institutions.models import Institution

inst_id = input('Institution ID: ')

i = Institution.objects.get(pk=inst_id)

new_sub = i.rated_submission

# get their previously rated submission if their is one
old_sub = None
i.current_rating = None
qs = i.submissionset_set.all().filter(status='r').exclude(id=new_sub.id).order_by("-date_submitted")
if qs.count() > 0:
    old_sub = qs[0]
    i.current_rating = old_sub.rating

# reset their submissions
new_sub.status = 'ps'
new_sub.reporter_status = False

# reset their subscription to allow another submission
subscription = i.current_subscription
subscription.ratings_used = 0

i.current_submission = new_sub

subscription.save()
new_sub.save()
i.save()