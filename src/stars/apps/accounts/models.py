from django.db import models
from django.contrib.auth.models import User

from stars.apps.institutions.models import Institution, StarsAccount


class UserProfile(models.Model):

    user = models.OneToOneField(User)
    is_member = models.BooleanField(default=False)
    is_aashe_staff = models.BooleanField(default=False)
    profile_instlist = models.CharField(max_length=128, blank=True, null=True)

    def is_participant(self):
        """
            Queries the institution model for any id found in profile_instlist
            which is just a list of id's in a string form received from drupal

            Also checks for a StarsAccount
        """
        if StarsAccount.objects.filter(user=self.user).count() > 0:
            return True

        if self.user.is_staff:
            return True

        if self.profile_instlist != '0':
            inst_list = map(int, self.profile_instlist.split(','))
            if inst_list:
                if Institution.objects.filter(
                        aashe_id__in=inst_list).count() > 0:
                    return True

        return False
