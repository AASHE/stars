from stars.apps.submissions.models import SubmissionSet

ss_id_list = [
              # 2182, # ASU
              # 2166, # Goshen College
              # 2038, # Slippery Rock University
              # 2082, # University of Nebraska-Lincoln
              # 2036, # University of Victoria
              # 2089, # Wilfrid Laurier University
              2036, # u of vic
]

def recalculate_score(ss):
    """
    Extracted as a method so that it can be used from the command line
    """
    print ss
    print "current score: %s" % ss.score
    print "current rating: %s" % ss.rating
    
    ss.score = None
    ss.save()
    
    ss.score = ss.get_STARS_score()
    ss.save()
    new_rating = ss.get_STARS_rating(recalculate=True)
    if ss.rating != new_rating:
        ss.rating = new_rating
        ss.institution.current_rating = new_rating
        ss.institution.save()
        ss.save()
    
    print "new score: %s" % ss.score
    print "new rating: %s" % ss.rating

for id in ss_id_list:
    ss = SubmissionSet.objects.get(pk=id)
    recalculate_score(ss)
