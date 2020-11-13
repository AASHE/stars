"""

# Test Suite for Scoring Tests

>>> from django.core import management
>>> from stars.apps.submissions.models import *
>>> from stars.apps.credits.models import *

>>> management.call_command("flush", verbosity=0, interactive=False)
>>> management.call_command("loaddata", "submissions_testdata.json", verbosity=0)

>>> s1=CreditUserSubmission.objects.get(pk=1)
>>> s2=CreditUserSubmission.objects.get(pk=2)
>>> s3=CreditUserSubmission.objects.get(pk=3)

# Per formula, assessed points for s1 should be:
# 5 * 1100/1200 = 4.58

>>> s1.credit.formula
u"var1 = F + (K or 0) + (P or 0) + (U or 0)\\n\\nif var1 >= A:\\n  var2 = A \\nelse:\\n  var2 = var1\\n\\n\\npoints = 5 * (var2/A)"
>>> s1.save()
>>> s1.assessed_points
4.5800000000000001

>>> s2.save()
>>> s2.assessed_points
3.0

>>> s3.save()
>>> s3.assessed_points
3.0

>>> submission_set = SubmissionSet.objects.get(pk=1)
>>> submission_set.get_available_points()
11.0
>>> submission_set.get_adjusted_available_points()
11.0

>>> submission_set.get_claimed_points()
10.58
>>> submission_set.get_STARS_score()
96.181818181818187
>>> submission_set.get_STARS_rating().name
u'Platinum'

>>> s1.submission_status = 'na'
>>> s1.save()

>>> submission_set = SubmissionSet.objects.get(pk=1)
>>> submission_set.get_available_points()
11.0
>>> submission_set.get_adjusted_available_points()
6.0
>>> submission_set.get_claimed_points()
6.0
>>> submission_set.get_STARS_score()
100.0
>>> submission_set.get_STARS_rating().name
u'Platinum'

>>> s2.submission_status = 'np'
>>> s2.save()

>>> submission_set = SubmissionSet.objects.get(pk=1)
>>> submission_set.get_available_points()
11.0
>>> submission_set.get_adjusted_available_points()
6.0
>>> submission_set.get_claimed_points()
3.0
>>> submission_set.get_STARS_score()
50.0
>>> submission_set.get_STARS_rating().name
u'Silver'

>>> s2.submission_status = 'ns'
>>> s2.save()

>>> submission_set = SubmissionSet.objects.get(pk=1)
>>> submission_set.get_available_points()
11.0
>>> submission_set.get_adjusted_available_points()
6.0
>>> submission_set.get_claimed_points()
3.0
>>> submission_set.get_STARS_score()
50.0
>>> submission_set.get_STARS_rating().name
u'Silver'
"""
