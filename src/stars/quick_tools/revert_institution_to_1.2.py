"""
    Revert an institution from 2.0 to 1.2
    
    prompts for the institution
    prompts for a submission to use as the data source
    creates a new submissionset using the source
    marks the new one as the current submission
"""

from stars.apps.institutions.models import Institution
from stars.apps.migrations.utils import create_ss_mirror

institution_id = input('Institution ID: ')
institution = Institution.objects.get(pk=institution_id)
print institution

ss_id = input("(1.2)Submission to use [ID]: ")
ss = institution.submissionset_set.get(pk=ss_id)

new_ss = create_ss_mirror(ss,
                          ss.creditset,
                          registering_user=ss.registering_user,
                          keep_innovation=True,
                          keep_status=True)
new_ss.is_locked = False
new_ss.is_visible = True
new_ss.save()

institution.current_submission = new_ss
institution.save()
