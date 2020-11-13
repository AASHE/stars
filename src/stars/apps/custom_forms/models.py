from django.db import models
from localflavor.us.models import PhoneNumberField

from stars.apps.credits.models import Subcategory

INST_CHOICES = (
    ('2-year', "2-year Associate's College"),
    ('baccalaureate', 'Baccalaureate College'),
    ('masters', "Master's Institution"),
    ('research', "Research University"),
    ('non-profit', "Non-profit Organization"),
    ('gov', 'Government Agency'),
    ('for-profit', "For-profit Business"),
    ('other', 'Other'),
)


class DataDisplayAccessRequest(models.Model):
    " a request for temporary access to the Data Displays "
    name = models.CharField(max_length=64)
    title = models.CharField(max_length=128)
    affiliation = models.CharField(
        "Institution or Affiliation", max_length=128)
    city_state = models.CharField("City/State", max_length=64)
    email = models.EmailField()

    summary = models.TextField("Summary description of your research")
    how_data_used = models.TextField(
        "How will STARS data be used in your research?")
    will_publish = models.BooleanField(
        "Click here if you will be distributing or publishing the data?",
        default=False)
    audience = models.TextField(
        "Who is the intended audience for your research?")
    period = models.DateField(
        "Requesting access starting on this date (mm/dd/yyyy)")
    end = models.DateField("Access requested until (mm/dd/yyyy)")

    has_instructor = models.BooleanField(
        "Is there an academic instructor or advisor who will provide guidance"
        " on how this data will be used?",
        default=False)
    instructor = models.TextField(
        "If yes, list name of instructor, title of instructor, and e-mail address.",
        null=True, blank=True)

    date = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return "%s" % (self.name)
