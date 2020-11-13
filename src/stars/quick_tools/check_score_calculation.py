"""
    Compare the stored score with the calculated score

    and display the calculation summary

    for a specified submission set
"""

from stars.apps.submissions.models import SubmissionSet
# ss_id = input('SubmissionSet ID: ')
# ss = SubmissionSet.objects.get(pk=ss_id)

for ss in SubmissionSet.objects.filter(status='r').filter(creditset__version="2.0"):

    print ss
    scoring_method = ss.creditset.scoring_method
#     print "scoring method: %s" % scoring_method
    
    print "current score:\t\t\t%f" % ss.score
    
    if hasattr(ss, scoring_method):
        calculated_score = getattr(ss, scoring_method)()
        print "calculated score:\t\t%f" % calculated_score
        
    print "%s :: %s" % (ss.rating, ss.creditset.get_rating(calculated_score))
#     
#     print "scoring summary:"
#      
#     for cat in ss.categorysubmission_set.all():
#         print "%s:\t\t\t%s" % (cat, getattr(cat, scoring_method)())
        
    print ""