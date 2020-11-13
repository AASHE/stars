from django.db import models


class AuthorizedUser(models.Model):

    email = models.EmailField()
    start_date = models.DateField()
    end_date = models.DateField()
    member_level = models.BooleanField(default=False)
    participant_level = models.BooleanField(default=False)

    class Meta:
        ordering = ('-start_date', '-end_date')
