from django.db import models
from django.contrib.auth.models import User

from sorl.thumbnail import ImageField

from stars.apps.submissions.models import SubmissionSet


class ThirdParty(models.Model):
    slug = models.SlugField(max_length=16)
    name = models.CharField(max_length=64)
    publication = models.CharField(max_length=128, blank=True, null=True)
    logo = models.ImageField(upload_to="tps", blank=True, null=True)
    next_deadline = models.DateField(blank=True, null=True)
    access_to_institutions = models.ManyToManyField(
        "institutions.Institution",
        related_name='third_parties',
        blank=True)
    disabled = models.BooleanField(default=False)
    help_text = models.TextField(blank=True, null=True)
    authorized_users = models.ManyToManyField(User)

    class Meta:
        verbose_name_plural = "Third Parties"
        ordering = ['-next_deadline', ]

    def __str__(self):
        return self.slug

    def get_snapshots(self):
        """
            Get all the available snapshots for this third party
        """
        qs = SubmissionSet.objects.filter(status='f')
        qs = qs.filter(institution__in=self.access_to_institutions.all())
        return qs

    def get_snapshot_institutions(self):
        """
            Get a list of institutions who have shared snapshots with this
            ThirdParty
        """
        i_list = []
        for i in self.access_to_institutions.all():
            if i.submissionset_set.filter(status='f').count() > 0:
                i_list.append(i)
        return i_list

    def get_snapshot_institution_count(self):
        """
            Get just the number of institutions that have shared snapshots
        """
        return len(self.get_snapshot_institutions())
