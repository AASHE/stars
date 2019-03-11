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


class TAApplication(models.Model):
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
    title = models.CharField(max_length=64)
    department = models.CharField(max_length=64)
    institution = models.CharField(
        "Institution/Organization Affiliation", max_length=128)
    phone_number = PhoneNumberField()
    email = models.EmailField()
    instituion_type = models.CharField(
        "Institution/Organization Type", max_length=32, choices=INST_CHOICES)
    subcategories = models.ManyToManyField(Subcategory)
    skills_and_experience = models.TextField()
    related_associations = models.TextField()
    resume = models.FileField(upload_to='ta_apps', max_length=255)
    credit_weakness = models.TextField(null=True, blank=True)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


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


class SteeringCommitteeNomination(models.Model):
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
    email = models.EmailField()
    affiliation = models.CharField(
        "Institution or Affiliation", max_length=128)
    phone_number = PhoneNumberField()
    why = models.TextField(
        "Why would you be excited to serve on the STARS Steering Committee?")
    skills = models.TextField(
        "What specific skills or background would you bring to the STARS Steering Committee that would help advance STARS?")
    successful = models.TextField(
        "How can you help STARS become a successful rating system?")
    strengths = models.TextField(
        "What do you consider to be the strengths and weaknesses of STARS?")
    perspectives = models.TextField(
        "What perspectives or representation of stakeholder groups would you bring to the STARS Steering Committee?")
    resume = models.FileField(upload_to='sc_apps', max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


class EligibilityQuery(models.Model):
    name = models.CharField(max_length=64)
    title = models.CharField(max_length=128)
    email = models.EmailField()
    institution = models.CharField(max_length=128)
    requesting_institution = models.CharField(max_length=128, blank=True,
                                              null=True)
    other_affiliates = models.BooleanField(default=False)
    included_in_boundary = models.BooleanField(default=False)
    separate_administration = models.BooleanField(default=False)
    rationale = models.TextField()
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        if self.requesting_institution:
            return self.requesting_institution
        else:
            return self.institution
