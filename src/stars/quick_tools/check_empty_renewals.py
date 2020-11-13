from stars.apps.submissions.models import *
from stars.apps.institutions.models import *
from stars.apps.migrations.utils import migrate_submission

def get_renewals():
    """
        Returns a list of submissionsets for insistutions that
        have renewed their registration and have a new submissionset
    """
    
    renewal_list = []
    
    for i in Institution.objects.all():
        
        # if at least one submission has a rating
        if i.submissionset_set.filter(status='r', is_visible=True).count() > 0:
            
            # If there is a current submission that is pending submission then that's a renewal
            try:
                ss = i.submissionset_set.get(status='ps', is_locked=False, is_visible=True)
                renewal_list.append(ss)
            except:
                pass
                
    return renewal_list

# not_empty_list = []
# 
# for r in get_renewals():
#     print r
#     for cs in r.categorysubmission_set.all():
#         for ss in cs.subcategorysubmission_set.all():
#             for cus in ss.creditusersubmission_set.all():
#                 for df in cus.get_submission_fields():
#                     if df.value and r not in not_empty_list:
#                         not_empty_list.append(r)
#                         
# for ss in not_empty_list:
#     print ss

for r in get_renewals():
    
    old_ss = r.institution.get_latest_submission()
    
    migrate_submission(old_ss, r)
    
    mail_to = [r.institution.contact_email,]
    subject = "STARS Renewal and Data Migration"
    message = """%s %s,
    
Thank you again for renewing your participation in STARS. To make reporting easier, we have copied your data from your previous rated submission into your current submission, to prevent you from having to duplicate much of that data this time around.

If you have any questions, please contact us at any time.

Happy reporting!
The STARS Team
stars@aashe.org""" % (r.institution.contact_first_name, r.institution.contact_last_name)

    from django.core.mail import EmailMessage
    m = EmailMessage(
                    subject=subject,
                    body=message,
                    to=mail_to,
                    bcc=['ben@aashe.org',],
                    headers={'Reply-To': settings.EMAIL_REPLY_TO}
                )
    m.send()