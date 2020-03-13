import os
import re
import sys
from datetime import date, datetime, timedelta
from logging import getLogger
import hashlib
import math
import numpy
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from localflavor.us.models import PhoneNumberField
from django.core import urlresolvers
from django.core.files.temp import NamedTemporaryFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import EmailMessage
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_init, pre_delete
from django.dispatch import receiver
from django.utils.http import urlquote

from stars.apps.credits.models import (ApplicabilityReason, Category, Choice,
                                       Credit, CreditSet, DocumentationField,
                                       Rating, Subcategory)
from stars.apps.institutions.models import (ClimateZone,
                                            Institution,
                                            Subscription)
from stars.apps.notifications.models import EmailTemplate
from stars.apps.notifications.utils import build_message
from stars.apps.submissions.export.pdf import build_report_pdf


FINALIZED_SUBMISSION_STATUS = 'f'
PENDING_SUBMISSION_STATUS = 'ps'
PROCESSSING_SUBMISSION_STATUS = 'pr'
RATED_SUBMISSION_STATUS = 'r'
REVIEW_SUBMISSION_STATUS = 'rv'

SUBMISSION_STATUSES = {
    "FINALIZED": FINALIZED_SUBMISSION_STATUS,
    "PENDING": PENDING_SUBMISSION_STATUS,
    "PROCESSSING": PROCESSSING_SUBMISSION_STATUS,
    "RATED": RATED_SUBMISSION_STATUS,
    "REVIEW": REVIEW_SUBMISSION_STATUS
}

SUBMISSION_STATUS_CHOICES = (
    (PENDING_SUBMISSION_STATUS, 'Pending Submission'),
    (PROCESSSING_SUBMISSION_STATUS, 'Processing Submission'),
    (REVIEW_SUBMISSION_STATUS, 'Review Submission'),
    (RATED_SUBMISSION_STATUS, 'Rated'),
    (FINALIZED_SUBMISSION_STATUS, 'Finalized'),
)

# Max # of extensions allowed per submission set
MAX_EXTENSIONS = 1

# Extension period
EXTENSION_PERIOD = timedelta(days=366/2)

# Rating valid for
RATING_VALID_PERIOD = timedelta(days=365 * 3)

# Institutions that registered before May 29th, but haven't paid are
# still published.
REGISTRATION_PUBLISH_DEADLINE = date(2010, 5, 29)

logger = getLogger('stars')


def submission_upload_path_callback(instance, filename):
    """
        Dynamically alters the upload path based on the instance
    """
    path = instance.get_upload_path()
    path = "%s%s" % (path, filename)
    return path


class Flag(models.Model):
    """
        A flag that can be added by staff for a submission/credit/field
    """
    date = models.DateField(auto_now_add=True)
    description = models.TextField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')

    def get_admin_url(self):
        return urlresolvers.reverse('admin:submissions_flag_change',
                                    args=[self.id])

    def __unicode__(self):
        return "%s" % self.target


class SubmissionManager(models.Manager):
    """
        Adds some custom query functionality to the SubmissionSet object
    """

    def published(self):
        """ Submissionsets that have been paid in full or unpaid before
        May 28th.
        """

        deadline = REGISTRATION_PUBLISH_DEADLINE
        qs1 = SubmissionSet.objects.filter(institution__enabled=True).filter(
            payment__isnull=False).filter(is_visible=True).filter(
                is_locked=False)
        qs2 = qs1.filter(
            (Q(payment__type='later') &
             Q(date_registered__lte=deadline)) | ~Q(payment__type='later'))
        return qs2.distinct()

    def get_rated(self):
        """ All submissionsets that have been rated (and are visible) """
        return SubmissionSet.objects.filter(
            institution__enabled=True).filter(
                is_visible=True).filter(
                    status=RATED_SUBMISSION_STATUS)

    def get_snapshots(self, institution):
        return SubmissionSet.objects.filter(
            institution=institution).filter(
                status=FINALIZED_SUBMISSION_STATUS).order_by(
                    '-date_submitted').order_by('-id')


class SubmissionSet(models.Model):
    """
        A creditset (ex: 1.0) that is being submitted
    """
    objects = SubmissionManager()
    creditset = models.ForeignKey(CreditSet)
    institution = models.ForeignKey(Institution)
    date_registered = models.DateField()
    date_published = models.DateField(blank=True, null=True)
    date_reviewed = models.DateField(blank=True, null=True)
    date_submitted = models.DateField(blank=True, null=True)
    expired = models.BooleanField(default=False)
    registering_user = models.ForeignKey(
        User,
        related_name='registered_submissions')
    submitting_user = models.ForeignKey(User,
                                        related_name='submitted_submissions',
                                        blank=True,
                                        null=True)
    rating = models.ForeignKey(Rating, blank=True, null=True)
    status = models.CharField(max_length=8, choices=SUBMISSION_STATUS_CHOICES)
    submission_boundary = models.TextField(
        blank=True,
        null=True,
        help_text=("The following is an example institutional boundary: "
                   "This submission includes all of the the University's "
                   "main campus as well as the downtown satellite campus. "
                   "The University hospital and campus farm are excluded."))
    presidents_letter = models.FileField(
        "Executive Letter",
        upload_to=submission_upload_path_callback,
        blank=True,
        max_length=255,
        null=True,
        help_text=("Please upload a letter from your institution's "
                   "president, chancellor or other high ranking executive "
                   "in PDF format."))
    reporter_status = models.BooleanField(
        help_text=("Check this box if you would like to be given "
                   "reporter status and not receive a STARS rating "
                   "from AASHE."), default=False)
    pdf_report = models.FileField(upload_to=submission_upload_path_callback,
                                  blank=True,
                                  max_length=255,
                                  null=True)
    is_locked = models.BooleanField(default=False)
    is_visible = models.BooleanField(
        default=True,
        help_text=("Is this submission visible to the institution? "
                   "Often used with migrations."))
    score = models.FloatField(blank=True, null=True)
    migrated_from = models.ForeignKey('self', null=True, blank=True,
                                      related_name='+')
    date_created = models.DateField(blank=True, null=True, auto_now_add=True)

    class Meta:
        ordering = ("date_registered",)

    def __unicode__(self):
        if self.date_submitted:
            return '%s -- %s (%s)' % (self.institution.name,
                                      self.creditset.version,
                                      self.date_submitted.strftime("%m/%d/%Y"))
        return '%s -- %s' % (self.institution.name, self.creditset.version)

    def get_flag_url(self):

        link = "%s?content_type=%s&object_id=%d" % (
            urlresolvers.reverse('admin:submissions_flag_add'),
            ContentType.objects.get_for_model(self).id,
            self.id
        )
        return link

    @property
    def flags(self):
        type = ContentType.objects.get_for_model(self)
        return Flag.objects.filter(content_type__pk=type.id, object_id=self.id)

    def missed_deadline(self):
        return not self.institution.is_participant

    def get_upload_path(self):
        return 'secure/%d/submission-%d/' % (self.institution.id, self.id)

    def get_pdf(self, template=None, refresh=False):
        """
            Generates a PDF file from the report

            If the submission is rated the report can be saved in the
            model (unless refresh is set)
        """
        # see block comment below about the following commented-out
        # code, and when you uncomment that block down there, uncomment
        # this one, too.
        #
        # probably real good idea to clear all SubmissionSet.pdf_file
        # fields sometime, too.

        # if self.status == RATED_SUBMISSION_STATUS and not refresh:
        #     try:
        #         if self.pdf_report:
        #             return self.pdf_report.file
        #     except IOError:
        #         pass

        pdf = build_report_pdf(self, template)

        pdf_tempfile = NamedTemporaryFile(suffix='.pdf', delete=False)

        # do not close pdf_tempfile, or boto will complain if django
        # tries to save it to s3 (if the report is rated).

        pdf.write_pdf(target=pdf_tempfile)

        # the following commented-out code saves pdfs generated for
        # rated reports, and returns that saved pdf; for unrated reports,
        # the tempfile where the pdf is stored is returned.
        #
        # problem is, some kind of caching or static files bug
        # causes attempts to read, eg., <SubmissionSet>.pdf_file
        # to 404.
        #
        # once that's ironed out, go ahead and uncomment the code
        # below. until then, we're going to ignore SubmissionStatus.pdf_report
        # and always return the pdf tempfile.

        pdf_tempfile.close()  # delete this line when you uncomment the rest
        return pdf_tempfile   # delete this line when you uncomment the rest

        # # Rated institutions can have their pdf saved
        # if self.status == RATED_SUBMISSION_STATUS:
        #     pdf_filename = self.get_pdf_filename()
        #     # resetting file pointer for boto, in case we're storing
        #     # stuff on s3.
        #     pdf_tempfile.seek(0)
        #     pdf_uploaded_file = InMemoryUploadedFile(
        #         file=pdf_tempfile, field_name="pdf",
        #         name=pdf_filename, content_type="pdf",
        #         size=os.path.getsize(pdf_tempfile.name),
        #         charset="utf8")
        #     self.pdf_report.save(pdf_filename,
        #                          pdf_uploaded_file)
        #     pdf_tempfile.close()
        #     return self.pdf_report.file

        # else:
        #     pdf_tempfile.close()
        #     return pdf_tempfile

    def get_pdf_filename(self):
        return '%s.pdf' % self.institution.slug[:64]

    def is_enabled(self):
        if self.is_visible:
            for payment in self.payment_set.all():
                if payment.type == 'credit' or payment.type == 'check':
                    return True
        return False

    def was_submitted(self):
        """ Indicates if this set has been submitted for a rating. """
        return self.date_submitted is not None

    def get_crumb_label(self):
        return str(self.creditset.version)

    def get_crumb_url(self):
        return self.get_manage_url()

    def get_admin_url(self):
        return "%ssubmissionsets/%d/" % (self.institution.get_admin_url(),
                                         self.id)

    def get_add_payment_url(self):
        return "%sadd-payment/" % self.get_admin_url()

    def get_manage_url(self):
        return urlresolvers.reverse(
            'tool:my_submission:submission-summary',
            kwargs={'institution_slug': self.institution.slug,
                    'submissionset': self.id})

    def get_submit_url(self):
        return urlresolvers.reverse(
            'tool:my_submission:submission-submit',
            kwargs={'institution_slug': self.institution.slug,
                    'submissionset': self.id})

    def get_scorecard_url(self):

        if self.date_submitted:
            return '/institutions/%s/report/%s/' % (self.institution.slug,
                                                    self.date_submitted)
        else:
            return '/institutions/%s/report/%s/' % (self.institution.slug,
                                                    self.id)

    def get_parent(self):
        """ Used for building crumbs """
        return None

    def get_status(self):
        """ Returns a status display string showing current status or rating
            for this submission """
        if self.is_rated():
            return unicode(self.rating)
        return self.get_status_display()

    def is_pending_review(self):
        return self.status == PROCESSSING_SUBMISSION_STATUS

    def is_rated(self):
        """ Return True if this submission set has been rated """
        return self.status == RATED_SUBMISSION_STATUS

    def is_under_review(self):
        """ Is this SubmissionStatus under review? """
        return self.status == REVIEW_SUBMISSION_STATUS

    def get_total_credits(self):
        total = 0
        for cat in self.creditset.category_set.all():
            for sub in cat.subcategory_set.all():
                total += sub.credit_set.count()
        return total

    def get_STARS_rating(self, recalculate=False):
        """
            Return the STARS rating (potentially provisional) for this
            submission

            @todo: this is inefficient - need to store or at least cache
            the STARS score.
        """
        if (self.reporter_status or
            self.status == FINALIZED_SUBMISSION_STATUS or
            (not self.is_rated() and
             self.institution.access_level == Subscription.BASIC_ACCESS)):
            return self.creditset.rating_set.get(name='Reporter')

        if self.is_rated() and not recalculate:
            return self.rating
        score = self.get_STARS_score(recalculate)
        return self.creditset.get_rating(score)

    def get_STARS_score(self, recalculate=False):
        """
            Return self.score.

            Update self.score if is_rated() or is_under_review(),
            except when is_rated and there's already a score for
            this SubmissionSet and recalculate is False.

            When recalculated, self.score is updated and this
            SubmissionSet is saved.
        """
        if self.is_rated() and self.score and not recalculate:
            return self.score

        scoring_method = self.creditset.scoring_method
        if hasattr(self, scoring_method):
            score = getattr(self, scoring_method)
            if self.is_rated() or self.is_under_review():
                self.score = score(recalculate)
                self.save()
                return self.score
            return score(recalculate)
        else:
            logger.error(
                "No method (%s) defined to score submission %s" %
                (scoring_method, self.creditset.version))
            return 0

    def get_STARS_v1_0_score(self, recalculate=False):
        """
            Averages of each category average

            Added the `recalculate` parameter, because we use it for 2.0.
            It has no affect with this method.
        """
        score = 0
        non_inno_cats = 0
        innovation_score = 0
        for cat in self.categorysubmission_set.all().select_related():
            if cat.category.is_innovation():
                innovation_score = cat.get_STARS_v1_0_score()
            elif cat.category.include_in_score:
                score += cat.get_STARS_v1_0_score()
                non_inno_cats += 1

        score = (score / non_inno_cats) if non_inno_cats > 0 else 0   # average

        score += innovation_score  # plus any innovation points

        return score if score <= 100 else 100

    def get_STARS_v2_0_score(self, recalculate=False):
        """
            Percentage of total achieved out of total available
        """
        innovation_score = 0
        total_available = 0
        total_achieved = 0

        for cat in self.categorysubmission_set.all().select_related():
            if cat.category.is_innovation():
                innovation_score = cat.get_STARS_v2_0_score(recalculate)[0]
            elif cat.category.include_in_score:
                _score, _avail = cat.get_STARS_v2_0_score(recalculate)
                total_achieved += _score
                total_available += _avail

        score = total_achieved / total_available * 100

        score += innovation_score  # plus any innovation points

        return score if score <= 100 else 100

    def get_claimed_points(self):
        """
            @TODO: Consider changing this to a stored value in the model
            if we do that we'll probably need transactions
        """
        score = 0
        for cat in self.categorysubmission_set.all():
            score += cat.get_claimed_points()
        return score

    def get_available_points(self):
        score = 0
        for cat in self.categorysubmission_set.all():
            score += cat.get_available_points()
        return score

    def get_adjusted_available_points(self):
        """ Gets only the points for credits that have not been labelled as
            Not Applicable """
        score = 0
        for cat in self.categorysubmission_set.all():
            score += cat.get_adjusted_available_points()
        return score

    def get_finished_credit_count(self):
        """ Get the number of credits that have been marked complete,
            not pursuing, or not applicable """
        count = 0
        for cat in self.categorysubmission_set.all():
            count += cat.get_finished_credit_count()
        return count

    def get_percent_complete(self):
        """ Return the percentage of credits completed in the entire
            set: 0 - 100 """
        total_credits = self.get_total_credits()
        if total_credits == 0:
            return 0
        return int(
            (self.get_finished_credit_count() / float(total_credits)) * 100)

    def get_progress_title(self):
        """ Returns a title for progress on the entire submission set """
        return "Complete" if (
            self.get_percent_complete() == 100) else "Reporting Status"

    def get_amount_due(self):
        """ Returns the amount of the total # of "later" payments tied to
            this submission """
        total = 0.0
        for p in self.payment_set.filter(type='later'):
            total += p.amount

        return total

    def init_credit_submissions(self):
        """
            Initializes all CreditUserSubmissions in a SubmissionSet
        """
        # Build the category list if necessary
        for category in self.creditset.category_set.all():
            try:
                categorysubmission = CategorySubmission.objects.get(
                    category=category, submissionset=self)
            except:
                categorysubmission = CategorySubmission(
                    category=category, submissionset=self)
                categorysubmission.save()

            # Create SubcategorySubmissions if necessary
            for subcategory in (
                    categorysubmission.category.subcategory_set.all()):
                try:
                    subcategorysubmission = SubcategorySubmission.objects.get(
                        subcategory=subcategory,
                        category_submission=categorysubmission)
                except SubcategorySubmission.DoesNotExist:
                    subcategorysubmission = SubcategorySubmission(
                        subcategory=subcategory,
                        category_submission=categorysubmission)
                    subcategorysubmission.save()

                # Create CreditUserSubmissions if necessary
                for credit in subcategory.credit_set.all():
                    try:
                        creditsubmission = CreditUserSubmission.objects.get(
                            credit=credit,
                            subcategory_submission=subcategorysubmission)
                    except CreditUserSubmission.DoesNotExist:
                        creditsubmission = CreditUserSubmission(
                            credit=credit,
                            subcategory_submission=subcategorysubmission)
                        creditsubmission.save()
                    if (credit.is_opt_in and
                        creditsubmission.submission_status != NOT_APPLICABLE):  # noqa

                        creditsubmission.submission_status = NOT_APPLICABLE
                        creditsubmission.save()

    def get_credit_submissions(self):
        """Returns all the credit submissions for this SubmissionSet."""
        category_subs = CategorySubmission.objects.filter(
            submissionset=self)
        subcategory_subs = SubcategorySubmission.objects.filter(
            category_submission__in=category_subs)
        return CreditUserSubmission.objects.filter(
            subcategory_submission__in=subcategory_subs)

    def save(self,
             skip_init_credit_submissions=False,
             *args, **kwargs):
        """If this is the first time save() has been called for this
        SubmissionSet, and `skip_init_credit_submissions` is False,
        initialize this SubmissionSet's CreditSubmissions.

        CreditSubmission initialization is not always desired, e.g.,
        during the Institution restoration process
        (e.g., see ./management/commands/restore_institution.py).

        Additionally, this SubmissionSet is flushed from the
        file-based cache, a surprisingly expensive operation.

        """
        run_init_credit_submissions = (
            not skip_init_credit_submissions and not self.pk)

        super(SubmissionSet, self).save(*args, **kwargs)

        if run_init_credit_submissions:
            self.init_credit_submissions()

    def take_snapshot(self, user):
        """
            Creates a new SubmissionSet, based on this one, for the
            latest CreditSet.  Sends courtesy emails as well.
        """
        # Importing create_ss_mirror within take_snapshot() to avoid the
        # circular imports created when stars.apps.migrations.utils is
        # imported at the top level.
        from stars.apps.migrations.utils import create_ss_mirror

        # Participants keep their existing submission and save a duplicate
        new_ss = create_ss_mirror(old_submissionset=self,
                                  new_creditset=self.creditset,
                                  registering_user=user,
                                  keep_innovation=True,
                                  keep_status=True)

        new_ss.registering_user = user
        new_ss.date_registered = date.today()
        new_ss.date_submitted = date.today()
        new_ss.submitting_user = user
        new_ss.status = FINALIZED_SUBMISSION_STATUS
        new_ss.is_visible = True
        new_ss.is_locked = False
        new_ss.save()

        et = EmailTemplate.objects.get(slug="snapshot_successful")
        to_mail = [user.email]
        if user.email != self.institution.contact_email:
            to_mail.append(self.institution.contact_email)
        et.send_email(to_mail, {'ss': self})

    def get_institution_type(self):
        """Return the institution type for the institution associated with
        this submissionset.

        For creditsets >= 2.0, pull the institution type off the institution
        boundary credit.  For others, pull from the institution record.
        """
        if self.creditset.version > '2.':
            institutional_characteristics_category = Category.objects.get(
                abbreviation='IC',
                creditset=self.creditset)
            institutional_characteristics_credit_submissions = (
                self.get_credit_submissions().filter(
                    subcategory_submission__category_submission__category=  # noqa
                    institutional_characteristics_category))
            boundary_credit_submission = (
                institutional_characteristics_credit_submissions.get(
                    credit__title='Institutional Boundary'))
            boundary_credit_submission_fields = (
                boundary_credit_submission.get_submission_fields())
            institution_type_submission_field = filter(
                lambda x: x.documentation_field.title.startswith(
                    'Institution type'),
                boundary_credit_submission_fields)[0]
            return institution_type_submission_field.get_human_value()
        else:
            return self.institution.institution_type


INSTITUTION_TYPE_CHOICES = (("associate", "Associate"),
                            ("baccalaureate", "Baccalaureate"),
                            ("master", "Master"),
                            ("doctorate", "Doctorate"),
                            ("special_focus", "Special Focus"),
                            ("tribal", "Tribal"))

INSTITUTION_CONTROL_CHOICES = (("public", "Public"),
                               ("private_profit", "Private for-profit"),
                               ("private_nonprofit", "Private non-profit"))

FEATURES_CHOICES = ((True, 'Yes'),
                    (False, 'No'))


class Boundary(models.Model):
    """
        Defines the boundary for the submission set.
    """

    submissionset = models.OneToOneField(SubmissionSet)

    # Characteristics
    fte_students = models.IntegerField("Full-time Equivalent Enrollment",
                                       blank=True, null=True)
    undergrad_count = models.IntegerField("Number of Undergraduate Students",
                                          blank=True, null=True)
    graduate_count = models.IntegerField("Number of Graduate Students",
                                         blank=True, null=True)
    fte_employmees = models.IntegerField("Full-time Equivalent Employees",
                                         blank=True, null=True)
    institution_type = models.CharField(max_length=32,
                                        choices=INSTITUTION_TYPE_CHOICES,
                                        blank=True, null=True)
    institutional_control = models.CharField(
        max_length=32,
        choices=INSTITUTION_CONTROL_CHOICES,
        blank=True, null=True)
    endowment_size = models.BigIntegerField(blank=True, null=True)
    student_residential_percent = models.FloatField(
        'Percentage of students that are Residential', blank=True, null=True)
    student_ftc_percent = models.FloatField(
        'Percentage of students that are Full-time commuter',
        blank=True, null=True,
        help_text=("Please indicate the percentage of full-time enrolled "
                   "students that commute to campus."))
    student_ptc_percent = models.FloatField(
        'Percentage of students that are Part-time commuter',
        blank=True, null=True,
        help_text=('Please indicate the percentage of part-time enrolled '
                   'students that commute to campus.'))
    student_online_percent = models.FloatField(
        'Percentage of students that are On-line only', blank=True, null=True)
    gsf_building_space = models.FloatField(
        "Gross square feet of building space", blank=True, null=True,
        help_text=("For guidance, consult <a href='http://nces.ed.gov/pubs2006"
                   "/ficm/content.asp?ContentType=Section&chapter=3&section=2&"
                   "subsection=1' target='_blank'>3.2.1 Gross Area (Gross "
                   "Square Feet-GSF)</a> of the U.S. Department of "
                   "Education's Postsecondary Education Facilities Inventory "
                   "and Classification Manual."))
    gsf_lab_space = models.FloatField(
        "Gross square feet of laboratory space",
        help_text=('Scientific research labs and other high performance '
                   'facilities eligible for <a href="http://'
                   'www.labs21century.gov/index.htm" target="_blank">'
                   'Labs21 Environmental Performance Criteria</a> (EPC).'),
        blank=True, null=True)
    cultivated_grounds_acres = models.FloatField(
        "Acres of cultivated grounds",
        help_text=("Areas that are landscaped, planted, and maintained "
                   "(including athletic fields). If less than 5 acres, "
                   "data not necessary."),
        blank=True, null=True)
    undeveloped_land_acres = models.FloatField(
        "Acres of undeveloped land",
        help_text="Areas without any buildings or development. If less "
        "than 5 acres, data not necessary",
        blank=True, null=True)
    climate_region = models.ForeignKey(
        ClimateZone,
        help_text=("See the <a href='http://apps1.eere.energy.gov/"
                   "buildings/publications/pdfs/building_america/"
                   "ba_climateguide_7_1.pdf'>USDOE</a> site and <a "
                   "href='http://www.ashrae.org/File%20Library/"
                   "docLib/Public/20081111_cztables.pdf'>ASHRAE</a>  "
                   "(international) for more information."),
        blank=True, null=True)

    # Features
    ag_school_present = models.NullBooleanField(
        "Agricultural school is present", choices=FEATURES_CHOICES, null=True)
    ag_school_included = models.NullBooleanField(
        "Agricultural school is included in submission",
        choices=FEATURES_CHOICES, null=True)
    ag_school_details = models.TextField("Reason for Exclusion", blank=True,
                                         null=True)
    med_school_present = models.NullBooleanField("Medical school is present",
                                                 choices=FEATURES_CHOICES,
                                                 null=True)
    med_school_included = models.NullBooleanField(
        "Medical school is included in submission", choices=FEATURES_CHOICES,
        null=True)
    med_school_details = models.TextField("Reason for Exclusion",
                                          blank=True, null=True)
    pharm_school_present = models.NullBooleanField(
        "Pharmacy school is present", choices=FEATURES_CHOICES, null=True)
    pharm_school_included = models.NullBooleanField(
        "Pharmacy school is included in submission", choices=FEATURES_CHOICES,
        null=True)
    pharm_school_details = models.TextField("Reason for Exclusion", blank=True,
                                            null=True)
    pub_health_school_present = models.NullBooleanField(
        "Public health school is present", choices=FEATURES_CHOICES, null=True)
    pub_health_school_included = models.NullBooleanField(
        "Public health school is included in submission",
        choices=FEATURES_CHOICES, null=True)
    pub_health_school_details = models.TextField("Reason for Exclusion",
                                                 blank=True, null=True)
    vet_school_present = models.NullBooleanField(
        "Veterinary school is present", choices=FEATURES_CHOICES, null=True)
    vet_school_included = models.NullBooleanField(
        "Veterinary school is included in submission",
        choices=FEATURES_CHOICES, null=True)
    vet_school_details = models.TextField("Reason for Exclusion",
                                          blank=True, null=True)
    sat_campus_present = models.NullBooleanField(
        "Satellite campuses are present", choices=FEATURES_CHOICES, null=True)
    sat_campus_included = models.NullBooleanField(
        "Satellite campuses are included in submission",
        choices=FEATURES_CHOICES, null=True)
    sat_campus_details = models.TextField("Reason for Exclusion",
                                          blank=True, null=True)
    hospital_present = models.NullBooleanField("Hospital is present",
                                               choices=FEATURES_CHOICES,
                                               null=True)
    hospital_included = models.NullBooleanField(
        "Hospital is included in submission", choices=FEATURES_CHOICES,
        null=True)
    hospital_details = models.TextField("Reason for Exclusion",
                                        blank=True, null=True)
    farm_present = models.NullBooleanField("Farm is present",
                                           help_text='Larger than 5 acres',
                                           choices=FEATURES_CHOICES, null=True)
    farm_included = models.NullBooleanField(
        "Farm is included in submission",
        choices=FEATURES_CHOICES, null=True)
    farm_acres = models.FloatField("Number of acres", blank=True, null=True)
    farm_details = models.TextField("Reason for Exclusion", blank=True,
                                    null=True)
    agr_exp_present = models.NullBooleanField(
        "Agricultural experiment station is present",
        help_text='Larger than 5 acres', choices=FEATURES_CHOICES, null=True)
    agr_exp_included = models.NullBooleanField(
        "Agricultural experiment station is included in submission",
        choices=FEATURES_CHOICES, null=True)
    agr_exp_acres = models.IntegerField("Number of acres", blank=True,
                                        null=True)
    agr_exp_details = models.TextField("Reason for Exclusion", blank=True,
                                       null=True)

    # Narrative
    additional_details = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Boundaries"

    def __unicode__(self):
        return unicode(self.submissionset)

    def get_characteristic_fields_and_values(self):
        """
            This is a useful tool for displaying the boundary
        """
        f_set = []
        for field_name in self.__class__.get_characteristic_field_names():
            d = {'title': self._meta.get_field(field_name).verbose_name}
            if hasattr(self, "get_%s_display" % field_name):
                d['value'] = getattr(self, "get_%s_display" % field_name)
            else:
                d['value'] = getattr(self, field_name)

            f_set.append(d)

        return f_set

    @classmethod
    def get_characteristic_field_names(cls):
        return [
            'fte_students',
            'undergrad_count',
            'graduate_count',
            'fte_employmees',
            'institution_type',
            'institutional_control',
            'endowment_size',
            'student_residential_percent',
            'student_ftc_percent',
            'student_ptc_percent',
            'student_online_percent',
            'gsf_building_space',
            'gsf_lab_space',
            'cultivated_grounds_acres',
            'undeveloped_land_acres',
            'climate_region',
        ]


def get_active_submissions(creditset=None,
                           category=None,
                           subcategory=None,
                           credit=None):
    """
        Return a queryset for ALL active (started / finished) credit
        submissions that meet the given criteria.  Only ZERO or ONE
        criteria should be specified - more is redundant and this code
        does not check for consistency.
    """
    submissions = CreditUserSubmission.objects.all()

    if credit:
        submissions = submissions.filter(credit=credit)
    else:
        # This code may result in a nested query. May not be optimized
        # in MySQL - see Performance Considerations at:
        # http://docs.djangoproject.com/en/dev/ref/models/querysets/#in
        credits = []
        if subcategory:
            credits = subcategory.credit_set.all()
        elif category:
            subcategories = Subcategory.objects.filter(category=category)
            credits = Credit.objects.filter(subcategory__in=subcategories)
        elif creditset:
            categories = Category.objects.filter(creditset=creditset)
            subcategories = Subcategory.objects.filter(category__in=categories)
            credits = Credit.objects.filter(subcategory__in=subcategories)

        submissions = submissions.filter(credit__in=credits)

    return submissions.exclude(submission_status=NOT_STARTED)


def get_complete_submissions(creditset=None,
                             category=None,
                             subcategory=None,
                             credit=None):
    """ See get_active_submission above - except only returns those marked
        as complete """
    submissions = get_active_submissions(creditset,
                                         category,
                                         subcategory,
                                         credit)
    return submissions.filter(submission_status='c')


def get_active_field_submissions(field):
    """ Return a queryset for ALL active (non-empty) submissions for the
        given documentations field. """
    FieldClass = DocumentationFieldSubmission.get_field_class(field)
    submissions = FieldClass.objects.filter(
        documentation_field=field).exclude(
            value=None)
    if FieldClass is TextSubmission or FieldClass is LongTextSubmission:
        submissions = submissions.exclude(value='')
    return submissions


def get_na_submissions(applicability_reason):
    """ Return a queryset for all n/a submissions that cite the given
        applicability_reason """
    return CreditUserSubmission.objects.filter(
        applicability_reason=applicability_reason).filter(
            submission_status=NOT_APPLICABLE)


def get_id(object):
    """ Return a valid identifier for the given sumbssion set object """
    return str(object).strip().lower().replace(" & ", "-").replace(" ", "-")


class CategorySubmission(models.Model):
    """
        A Category from a credit set that is being submitted
    """
    submissionset = models.ForeignKey(SubmissionSet)
    category = models.ForeignKey(Category)
    score = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ("submissionset", "category")
        ordering = ("category__ordinal",)

    def __unicode__(self):
        return unicode(self.category)

    def get_crumb_label(self):
        return str(self)

    def get_crumb_url(self):
        return self.get_submit_url()

    def get_institution(self):
        return self.submissionset.institution

    def get_creditset(self):
        return self.submissionset.creditset

    def get_submit_url(self):
        return self.category.get_submit_url(submissionset=self.submissionset)

    def get_id(self):
        """ Return a valid identifier representing this category """
        return get_id(self)

    def get_total_credits(self):
        total = 0
        for sub in self.subcategorysubmission_set.all():
            total = total + sub.get_total_credits()
        return total

    def get_parent(self):
        """ Used for building crumbs """
        return self.submissionset

    def get_scorecard_url(self):
        return '%s%s' % (self.submissionset.get_scorecard_url(),
                         self.category.get_browse_url())

    def get_STARS_score(self):
        """
            Return self.score.

            Recalculate the score if submissionset is rated or under review,
            except if submissionset is rated and already has a score.

            If score is recalculated, self.score is updated and this Category
            is saved.
        """
        if self.submissionset.is_rated() and self.score:
            # cache the score in the model
            return self.score

        scoring_method = self.submissionset.creditset.scoring_method
        if hasattr(self, scoring_method):
            score = getattr(self, scoring_method)
            if (self.submissionset.is_rated or
                    self.submissionset.is_under_review()):

                self.score = score()
                if type(self.score) == tuple:
                    self.score = self.score[0]
                self.save()
            return self.score
        else:
            logger.error(
                "No method (%s) defined to score category submission %s" %
                (scoring_method, self.submissionset.creditset.version))
            return 0

    def get_STARS_v1_0_score(self):
        score, avail = self.get_score_ratio()
        #  score for innovation credits is just the raw score
        #  for all others, it is the proportion of points earned.
        if not self.category.is_innovation():
            # percentage of points earned, 0 - 100
            score = ((100.0 * score) / avail) if avail > 0 else 0
        return score

    def get_STARS_v2_0_score(self, recalculate=False):
        """
            returns the available and achieved points
        """
        return self.get_score_ratio(recalculate)

    def get_claimed_points(self):
        score = 0
        for sub in self.subcategorysubmission_set.all().select_related():
            score += sub.get_claimed_points()
        if self.category.abbreviation == "IN":
            score = 4 if score > 4 else score
        return score

    def get_available_points(self):
        score = 0
        for sub in self.subcategorysubmission_set.all().select_related():
            score += sub.get_available_points()
        if self.category.abbreviation == 'IN':
            score = 4
        return score

    def get_score_ratio(self, recalculate=False):
        """
            Returns the claimed and adjusted available points
        """
        claimed = 0
        available = 0
        for sub in self.subcategorysubmission_set.all().select_related():
            claimed += sub.get_claimed_points(recalculate)
            available += sub.get_adjusted_available_points(recalculate)
        # Innovation and Leadership credits are capped at 4.
        if self.category.abbreviation == "IN":
            claimed = 4 if claimed > 4 else claimed
            available = 4
        return claimed, available

    def get_adjusted_available_points(self, recalculate=False):
        """Gets only the points for credits that have not been labelled as
           Not Applicable"""
        score = 0
        for sub in self.subcategorysubmission_set.all():
            score += sub.get_adjusted_available_points(recalculate=recalculate)
        return score

    def get_not_started_credit_count(self):
        """Get the number of credits that have been marked complete, not
           pursuing, or not applicable"""
        count = 0
        for sub in self.subcategorysubmission_set.all():
            count += sub.get_not_started_credit_count()
        return count

    def get_finished_credit_count(self):
        """Get the number of credits that have been marked complete, not
           pursuing, or not applicable"""
        count = 0
        for sub in self.subcategorysubmission_set.all():
            count += sub.get_finished_credit_count()
        return count

    def get_percent_complete(self):
        """Return the percentage of credits completed in this category: 0 -
           100"""
        total_credits = self.get_total_credits()
        if total_credits == 0:
            return 0
        return int(
            (self.get_finished_credit_count() / float(total_credits)) * 100)

    def get_status(self):
        """Returns a status label for this category or None if not
           started."""
        complete = self.get_percent_complete()
        return (None
                if complete == 0
                else "Complete" if complete == 100
                else "In Progress")

    def get_progress_title(self):
        """ Returns a title for a progress summary on this category """
        return "Complete" if self.get_percent_complete() == 100 else "Progress"

    def is_innovation(self):
        return self.category.is_innovation()


class SubcategorySubmission(models.Model):
    """
        A Category from a credit set that is being submitted
    """
    category_submission = models.ForeignKey(CategorySubmission)
    subcategory = models.ForeignKey(Subcategory)
    description = models.TextField(blank=True, null=True)
    points = models.FloatField(blank=True, null=True)
    # caching for the data displays
    percentage_score = models.FloatField(blank=True, null=True, default=0.0)
    adjusted_available_points = models.FloatField(blank=True, null=True,
                                                  default=0.0)

    class Meta:
        unique_together = ("category_submission", "subcategory")
        ordering = ("subcategory__ordinal",)

    def __unicode__(self):
        return unicode(self.subcategory)

    def get_crumb_label(self):
        return str(self)

    def get_crumb_url(self):
        return self.get_submit_url()

    def get_id(self):
        """ Return a valid identifier representing this subcategory """
        return get_id(self)

    def get_institution(self):
        return self.category_submission.get_institution()

    def get_parent(self):
        """ Used for building crumbs """
        return self.category_submission

    def get_creditset(self):
        return self.category_submission.get_creditset()

    def get_total_credits(self):
        total = 0
        for credit in self.subcategory.credit_set.all():
            if not credit.is_opt_in:
                total += 1
            else:
                try:
                    cus = CreditUserSubmission.objects.get(
                        subcategory_submission=self,
                        credit=credit)
                except CreditUserSubmission.DoesNotExist:
                    # I don't know why this would happen
                    # but it's happening.
                    logger.error(
                        "Credit pk={} has no CreditUserSubmission ".format(
                            credit.pk))
                else:
                    if cus.submission_status != NOT_APPLICABLE:
                        total += 1
        return total

    def get_submissionset(self):
        return self.category_submission.submissionset

    def get_submit_url(self):
        return self.subcategory.get_submit_url(
            submissionset=self.category_submission.submissionset)

    def get_submit_edit_url(self):
        return self.subcategory.get_submit_edit_url(
            submissionset=self.category_submission.submissionset)

    def get_scorecard_url(self):
        return '%s%s' % (
            self.category_submission.submissionset.get_scorecard_url(),
            self.subcategory.get_browse_url())

    def get_complete_credit_count(self):
        """ Find all CreditSubmissions in this subcategory
            that are complete """
        return self.creditusersubmission_set.filter(
            submission_status='c').count()

    def get_pending_credit_count(self):
        return self.creditusersubmission_set.filter(
            submission_status='p').count()

    def get_not_pursuing_credit_count(self):
        return self.creditusersubmission_set.filter(
            submission_status='np').count()

    def get_not_applicable_credit_count(self):
        return self.creditusersubmission_set.filter(
            submission_status=NOT_APPLICABLE).count()

    def get_not_started_credit_count(self):
        return self.creditusersubmission_set.filter(
            submission_status=NOT_STARTED).count()

    def get_finished_credit_count(self):
        """ Get the number of credits that have been marked
        complete, not pursuing, or not applicable """
        total = 0
        for cus in self.creditusersubmission_set.exclude(
                submission_status=NOT_STARTED).exclude(
                    submission_status='p'):
            if not cus.credit.is_opt_in:
                total += 1
            else:
                if cus.submission_status != NOT_APPLICABLE:
                    total += 1
        return total

    def get_claimed_points(self, recalculate=False):
        rated = self.category_submission.submissionset.is_rated()
        # check the cache
        if rated and self.points and self.percentage_score and not recalculate:
            return self.points

        score = 0
        for credit in self.creditusersubmission_set.filter(
                submission_status='c'):
            score += credit.assessed_points

        if self.category_submission.submissionset.is_rated():
            # cache it on the model
            self.points = score
            available = self.get_available_points()
            if available > 0:
                self.percentage_score = score / available
            else:
                self.percentage_score = 0
            self.save()
        return score

    def get_available_points(self):
        points = 0
        for credit in self.subcategory.credit_set.all():
            points += credit.point_value
        return points

    def get_adjusted_available_points(self, recalculate=False):
        """Gets only the points for credits that have not been labelled as
           Not Applicable"""

        rated = self.category_submission.submissionset.is_rated()
        # check the cache
        if rated and self.adjusted_available_points and not recalculate:
            return self.adjusted_available_points

        points = 0
        for credit_submission in self.creditusersubmission_set.all():
            points += credit_submission.get_adjusted_available_points()

        if rated:
            # cache the result
            self.adjusted_available_points = points
            self.save()

        return points

    def get_percent_complete(self):
        """Return the percentage of credits completed in this subcategory: 0
           - 100"""
        total_credits = self.subcategory.credit_set.count()
        if total_credits == 0:
            return 0
        return int(
            (self.get_finished_credit_count() / float(total_credits)) * 100)

    def get_status(self):
        """Returns a status label for this subcatogory or None if not
           started."""
        complete = self.get_percent_complete()
        return (None
                if complete == 0
                else "Complete" if complete == 100
                else "In Progress")

    def get_progress_title(self):
        """ Returns a title for a progress summary on this subcatogory """
        return "Complete" if self.get_percent_complete() == 100 else "Progress"

    def is_innovation(self):
        return self.category_submission.is_innovation()


class ResponsibleParty(models.Model):
    """
        Stores responsible parties for institutions
    """
    institution = models.ForeignKey(Institution)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    department = models.CharField(max_length=128)
    email = models.EmailField()
    phone = PhoneNumberField()

    class Meta:
        ordering = ('last_name', 'first_name')
        verbose_name_plural = "Responsible Parties"

    def __unicode__(self):
        return "%s, %s" % (self.last_name, self.first_name)

    def get_manage_url(self):
        return "/tool/{slug}/manage/responsible-party/{id}/".format(
            slug=self.institution.slug, id=self.id)

    def get_creditusersubmissions(self, order_by=None):
        """
            Returns a queryset of (visible) CreditUserSubmissions related to
            this responsible party.

            order_by arg is a tuple passed to queryset.order_by.
        """
        order_by = order_by or ('credit__subcategory__category__creditset',
                                'credit__subcategory')
        qs = self.creditusersubmission_set
        qs = qs.order_by(*order_by)
        qs = qs.exclude(subcategory_submission__category_submission__submissionset__is_visible=False)  # noqa
        return qs


class CreditSubmission(models.Model):
    """
        A complete submission data set for a credit
        This is really an abstract base class for two types of submissions:

         - a User Submission (normal submission for an institutions
           STARS submission set)

         - a Test Submission (a test case used to validate formulae in
           the Credit Editor)
    """
    credit = models.ForeignKey(Credit)
    available_point_cache = models.FloatField(blank=True, null=True)
    is_unlocked_for_review = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ("credit__type", "credit__ordinal",)

    def __unicode__(self):
        return self.credit.title

    def model_name():
        return u"Credit Submission"
    model_name = staticmethod(model_name)

    def __init__(self, *args, **kwargs):
        super(CreditSubmission, self).__init__(*args, **kwargs)
        self.submission_fields = None  # lazy init

    def get_crumb_label(self):
        return str(self)

    def get_institution(self):
        return self.subcategory_submission.get_institution()

    def get_submission_fields(self, using="default"):
        """
            Returns the list of documentation field submission objects for
            this credit submission

            You can't simply ask
            self.documentationfieldsubmission_set.all() because each
            field may have a different type.

            If this CreditSubmission persists in DB, this method also
            saves empty submission field records for any that are
            missing.

            @return the complete list of DocumentationFieldSubmission
            sub-class objects related to this CreditSubmission
        """
        if not self.submission_fields:  # cache.
            self.submission_fields = (
                self._submission_fields_for_documentation_fields(
                    documentation_field_list=self.credit.documentationfield_set.all(),  # noqa
                    using=using))

        return self.submission_fields

    def get_public_submission_fields(self):

        return self._submission_fields_for_documentation_fields(
            self.credit.documentationfield_set.filter(is_published=True))

    def _submission_fields_for_documentation_fields(
            self,
            documentation_field_list,
            using="default"):
        """Return the list of DocumentationFieldSubmissions for this
        CreditSubmission, creating them if they don't already exist.
        """
        submission_field_list = []
        for field in documentation_field_list:
            SubmissionFieldModelClass = (
                DocumentationFieldSubmission.get_field_class(field))
            if SubmissionFieldModelClass:
                try:
                    submission_field = SubmissionFieldModelClass.objects.get(
                        documentation_field=field, credit_submission=self)
                    # ORM / Model Inheritance issue:
                    #
                    #   DocumentationFieldSubmission has a foreign key to
                    #   CreditSubmission, but object may have reference to
                    #   a sub-class!
                    #
                    #   Hack: (Joseph)  update the reference in the field
                    #   we just loaded.
                    submission_field.credit_submission = self

                except SubmissionFieldModelClass.DoesNotExist:
                    credit_submission = (
                        self if using == "default" else
                        CreditSubmission.objects.using(using).get(pk=self.pk))

                    submission_field = SubmissionFieldModelClass(
                        documentation_field=field,
                        credit_submission=credit_submission)

                    submission_field.save(using=using)

                submission_field_list.append(submission_field)
            else:
                # use a dummy submission_field for tabular
                class TabularSubmissionField():
                    def __init__(self, credit_submission, documentation_field):

                        self.credit_submission = credit_submission
                        self.documentation_field = documentation_field
                        self.documentation_field_id = documentation_field.id

                    def get_value(self):
                        # dummy
                        return None

                    def get_human_value(self, *args, **kwargs):
                        return ""

                    def __unicode__(self):
                        return ("TabularSubmissionField for " +
                                self.credit_submission.credit.title)

                submission_field_list.append(TabularSubmissionField(
                    credit_submission=self,
                    documentation_field=field))

        self.submission_fields = submission_field_list
        return self.submission_fields

    def get_submission_field_values(self):
        """ Returns the list of documentation field values for this
            submission
        """
        return [field.get_value() for field
                in self.get_submission_fields()]

    def get_submission_field_key(self, metric = False):
        """ Returns a dictionary with identifier:value for each submission
            field
        """
        fields = self.get_submission_fields()
        key = {}
        for field in fields:
            value = field.get_value()
            if field.__class__ == NumericSubmission:
                value = field.value if not metric else field.metric_value
            key[field.documentation_field.identifier] = value
        return key

    def print_submission_fields(self):
        print >> sys.stderr, "Fields for CreditSubmission: %s" % self
        fields = self.get_submission_fields()
        for field in fields:
            print >> sys.stderr, field

    # @todo: rename or remove this - potential confusion b/c name conflict
    #        with CreditUserSubmission!!
    #        I don't think this one is actually called anywhere.
    def is_complete(self):
        """ Return True if the Credit Submission is complete."""
        if not self.persists():
            # New submissions are incomplete - don't try to access fields yet!
            return False
        for field in self.get_submission_fields():
            if field.documentation_field.is_required() and not field.value:
                return False
        return True

    def is_test(self):
        """Returns True if this is a test submission."""
        if isinstance(self, CreditTestSubmission):
            return True
        else:
            # Sometimes we see a CreditSubmission that's neither
            # an instance of CreditTestSubmission or
            # CreditUserSubmission. In these cases, we look to
            # the credittestsubmission attribute for guidance.
            # If it points to an existing CreditTestSubmission, we
            # consider this CreditSubmission to be a test.
            try:
                self.credittestsubmission
                return True
            except CreditTestSubmission.DoesNotExist:
                return False

    def persists(self):
        """Does this CreditSubmission persist in the DB?"""
        return self.pk is not None

    def get_parent_available_points(self, use_cache=False):
        if use_cache and self.available_point_cache is not None:
            return self.available_point_cache
        # in most cases there's a fixed point value
        if self.credit.point_minimum is None:
            self.available_point_cache = self.credit.point_value
            return self.credit.point_value

        # but if there's not then we need to execute the formula
        (ran, message, exception, available_points) = (
            self.credit.execute_point_value_formula(self))
        self.available_point_cache = available_points
        return available_points

    @staticmethod
    def round_points(points, log_error=True):
        """
            Convert points to numeric and round to the correct # decimals
            Returns (points, error) where

                - points = rounded numeric point value (or 0 if an
                  error occurred)

                - error = error message or None if conversion was successful
        """
        try:  # Ensure that the result of the formula was a valid points value!
            points = float(points)
            return (round(points, 2), None)
        except Exception, e:
            if log_error:
                logger.error(
                    "Error converting formula result (%s) to numeric type: %s"
                    % (points, e), exc_info=True)
            return (0,
                    "Non-numeric result calculated for points: %s" % points)

    def validate_points(self, points, log_error=True):
        """
             Helper: Validate the points calculated for this submission
             Returns (points, messages), where points are the validated points

             - message is a list of error messages associated with any
               validation errors, which is empty if the the points
               validated.
        """
        messages = []

        # is it numeric?
        points, numeric_error = self.round_points(points, log_error)
        if numeric_error:
            messages.append(numeric_error)

        if points < 0 or points > self.credit.point_value:  # is it in range?
            try:
                error_institution = self.get_institution()
            except AttributeError:
                error_institution = "TEST CREDIT"
            range_error = (
                "Points ({points}) are out of range (0 - {limit}) "
                "(Institution: {institution}; credit: {credit}.)".format(
                    points=points, limit=self.credit.point_value,
                    institution=error_institution,
                    credit=str(self.credit).strip()))
            if log_error:
                logger.error(range_error)
            messages.append(range_error)
            points = 0

        return points, messages

    def get_status_update_url(self):
        return urlresolvers.reverse('institutions:credit-submission-status-update',
                                    kwargs={'pk': self.id})

    def get_help_center_search_url(self):
        return "https://{}/resources-support/help-center/search/{}".format(settings.STARS_BROCHURE_HOST, self.credit.title)


COMPLETE = "c"
IN_PROGRESS = "p"
NOT_PURSUING = "np"
NOT_APPLICABLE = "na"
NOT_STARTED = "ns"

CREDIT_SUBMISSION_STATUSES = {
    "COMPLETE": COMPLETE,
    "IN_PROGRESS": IN_PROGRESS,
    "NOT_PURSUING": NOT_PURSUING,
    "NOT_APPLICABLE": NOT_APPLICABLE,
    "NOT_STARTED": NOT_STARTED
}

CREDIT_SUBMISSION_STATUS_CHOICES_LIMITED = [
    (COMPLETE, 'Complete'),
    (IN_PROGRESS, 'In Progress'),
    (NOT_PURSUING, 'Not Pursuing'),
]

# The NOT_STARTED option isn't accessible in forms and NOT_APPLICABLE
# only sometimes, so we have 3 different lists.
CREDIT_SUBMISSION_STATUS_CHOICES_W_NA = list(
    CREDIT_SUBMISSION_STATUS_CHOICES_LIMITED)
CREDIT_SUBMISSION_STATUS_CHOICES_W_NA.append((NOT_APPLICABLE,
                                              'Not Applicable'))
CREDIT_SUBMISSION_STATUS_CHOICES = list(CREDIT_SUBMISSION_STATUS_CHOICES_W_NA)
CREDIT_SUBMISSION_STATUS_CHOICES.append((NOT_STARTED, 'Not Started'))

# used by template tag to create iconic representation of status:
CREDIT_SUBMISSION_STATUS_ICONS = {
    COMPLETE: ('icon-ok', 'c'),
    IN_PROGRESS: ('icon-pencil', '...'),
    NOT_PURSUING: ('icon-remove', '-'),
    NOT_APPLICABLE: ('icon-tag', '-')
}

REVIEW_CONCLUSIONS = {
    "NOT_REVIEWED": "not-reviewed",
    "MEETS_CRITERIA": "meets-criteria",
    "DOES_NOT_MEET_CRITERIA": "does-not-meet-criteria",
    "NOT_REALLY_PURSUING": "not-really-pursuing"}

REVIEW_CONCLUSION_CHOICES = (
    (REVIEW_CONCLUSIONS["NOT_REVIEWED"], "Not Reviewed"),
    (REVIEW_CONCLUSIONS["MEETS_CRITERIA"], "Meets Criteria"),
    (REVIEW_CONCLUSIONS["DOES_NOT_MEET_CRITERIA"], "Does Not Meet Criteria"),
    (REVIEW_CONCLUSIONS["NOT_REALLY_PURSUING"], "Not Really Pursuing"))


class CreditUserSubmission(CreditSubmission):
    """
        An individual submitted credit for an institutions STARS submission
        set
    """
    subcategory_submission = models.ForeignKey(SubcategorySubmission)
    assessed_points = models.FloatField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    submission_status = models.CharField(
        max_length=8,
        choices=CREDIT_SUBMISSION_STATUS_CHOICES,
        default=NOT_STARTED)
    applicability_reason = models.ForeignKey(ApplicabilityReason,
                                             blank=True,
                                             null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    internal_notes = models.TextField(
        help_text=('This field is useful if you want to store notes for '
                   'other people in your organization regarding this credit. '
                   'They will not be published.'),
        blank=True,
        null=True)
    submission_notes = models.TextField(
        help_text=('Use this space to add any additional information '
                   'you may have about this credit. This will be published '
                   'along with your submission.'),
        blank=True,
        null=True)
    responsible_party_confirm = models.BooleanField(default=False)
    responsible_party = models.ForeignKey(ResponsibleParty,
                                          blank=True,
                                          null=True,
                                          on_delete=models.SET_NULL)
    review_conclusion = models.CharField(
        max_length=32,
        choices=REVIEW_CONCLUSION_CHOICES,
        default=REVIEW_CONCLUSIONS["NOT_REVIEWED"])

    class Meta:
        # @todo: the unique clause needs to be added at the DB level now :-(
        # unique_together = ("subcategory_submission", "credit")
        pass

    def get_flag_url(self):

        link = "%s?content_type=%s&object_id=%d" % (
            urlresolvers.reverse('admin:submissions_flag_add'),
            ContentType.objects.get_for_model(self).id,
            self.id
        )
        return link

    @property
    def flags(self):
        type = ContentType.objects.get_for_model(self)
        return Flag.objects.filter(content_type__pk=type.id, object_id=self.id)

    def get_institution(self):
        return self.subcategory_submission.category_submission.submissionset.institution  # noqa

    def get_submit_url(self):
        category_submission = self.subcategory_submission.category_submission
        submissionset = category_submission.submissionset
        url = urlresolvers.reverse(
            'tool:my_submission:creditsubmission-submit',
            kwargs={
                'institution_slug': submissionset.institution.slug,
                'submissionset': submissionset.id,
                'category_abbreviation':
                    category_submission.category.abbreviation,
                'subcategory_slug':
                    self.subcategory_submission.subcategory.slug,
                'credit_identifier': self.credit.identifier})
        return url

    def get_scorecard_url(self):
        return self.credit.get_scorecard_url(
            self.subcategory_submission.category_submission.submissionset)

    def get_parent(self):
        """ Used for building crumbs """
        return self.subcategory_submission

    def get_creditset(self):
        return self.subcategory_submission.get_creditset()

    def get_submissionset(self):
        return self.subcategory_submission.get_submissionset()

    def is_finished(self):
        """ Indicate if this credit has been marked anything other than
            in progress or not started
        """
        return (self.submission_status != IN_PROGRESS and
                self.submission_status != NOT_STARTED and
                self.submission_status is not None)

    def save(self, calculate_points=True, *args, **kwargs):
        self.last_updated = datetime.now()

        if calculate_points:
            self.assessed_points = float(self._calculate_points())

        # If this is an opt-in credit, NOT_PURSUING is a rather
        # meaningless status, since opt-in credits that a submitter
        # has opted-out of should have a status of NOT_APPLICABLE.
        # Practically, opt-in credit submissions of type
        # NOT_APPLICABLE are filtered out of reports and displays, and
        # that's what we want, and don't want is to see opt-in credits
        # labelled NOT_PURSUING. So if this is an opt-in credit and
        # somebody's trying to save it as NOT_PURSUING, forget that
        # and set the submission_status to NOT_APPLICABLE.
        if self.credit.is_opt_in and self.submission_status == NOT_PURSUING:
            self.submission_status = NOT_APPLICABLE

        # When this CreditUserSubmission is unlocked for review and
        # its submission_status is updated, we need to send some
        # mail. So we need to know what's in the db before we save.
        try:
            before_image = (CreditUserSubmission.objects.get(pk=self.pk)
                            if self.pk else None)
        except CreditUserSubmission.DoesNotExist:
            before_image = None

        # If this CreditUserSubmission is unlocked for review,
        # we want to lock it up if the new submission_status is
        # COMPLETE or NOT_PURSUING or NOT_APPLICABLE.
        if (before_image is not None and
            before_image.is_unlocked_for_review and
            self.submission_status in (COMPLETE,
                                       NOT_PURSUING,
                                       NOT_APPLICABLE)):
            self.is_unlocked_for_review = False

        super(CreditUserSubmission, self).save(*args, **kwargs)

        if (before_image is not None and
            before_image.is_unlocked_for_review and
            not self.is_unlocked_for_review):  # noqa

            self.send_unlocked_credit_submission_updated_email()

    def is_complete(self):
        return self.submission_status == COMPLETE

    def is_na(self):
        return self.submission_status == NOT_APPLICABLE

    def is_pursued(self):
        """ Returns False if this credit is marked NOT_APPLICABLE
            or NOT_PURSUING """
        return (self.submission_status != NOT_APPLICABLE and
                self.submission_status != NOT_PURSUING)

    def mark_as_in_progress(self):
        self.submission_status = IN_PROGRESS

    def get_adjusted_available_points(self):
        """ Gets only the points for credits that have not been labelled as
            Not Applicable
        """
        if self.submission_status == NOT_APPLICABLE:
            return 0
        return self.get_available_points()

    def _calculate_points(self):
        """Returns the number of points calculated for this
           submission
        """
        # Run the calculation only when this credit submission is
        # complete or under review, and is being pursued.
        if ((not self.is_complete() and
             not self.get_submissionset().is_under_review()) or
                not self.is_pursued()):

            return 0

        assessed_points = 0  # default is zero - now re-calculate points...
        validation_error = False

        (ran, message, exception, points, d) = self.credit.execute_formula(
            self, debug=True)

        if ran:  # perform validation on points...
            (points, messages) = self.validate_points(points)
            validation_error = len(messages) > 0

        if not ran or validation_error:
            logger.error("There was an error processing this credit. "
                         "AASHE has noted the error and will work to "
                         "resolve the issue.")
        else:
            assessed_points = points

        return assessed_points

    def send_unlocked_credit_submission_updated_email(self):
        """ Send email to let STARS reviewers know an unlocked
            credit submission has been updated.
        """
        email_template = (
            "/tool/submissions/unlocked_credit_submission_updated_email.html")

        institution = self.get_submissionset().institution

        subject = ("Unlocked Credit Submission Updated: "
                   "{institution}: {credit}".format(
                       institution=institution,
                       credit=self.credit))

        email_context = {"credit_user_submission": self,
                         "institution": institution}

        with open(settings.TEMPLATES[0]['DIRS'][0] + email_template,
                  "rb") as template:
            email_content = build_message(template.read(), email_context)

        email_message = EmailMessage(
            subject=subject,
            body=email_content,
            from_email="stars-reviewers@aashe.org",
            to=["stars-reviewers@aashe.org"],
            headers={"Reply-To": "stars-reviewers@aashe.org"})

        email_message.content_subtype = "html"

        email_message.send()

    def get_available_points(self, use_cache=False):
        '''
            Check if the credit is NP and if it has point_minimum.
            Otherwise return the parent's method for calculating available_points
        '''
        if self.credit.point_minimum is not None and self.submission_status == NOT_PURSUING:
            return math.ceil((self.credit.point_minimum + self.credit.point_value) / 2)
        return self.get_parent_available_points(use_cache=use_cache)


class CreditTestSubmission(CreditSubmission):
    """
        A test data set for a Credit formula - not part of any submission set
    """
    expected_value = models.FloatField(
        blank=True,
        null=True,
        help_text="Point value expected from the formula for this test data")

    def model_name():
        return u"Formula Test Case"
    model_name = staticmethod(model_name)

    def run_test(self):
        """
        Run this test case on the given test data
        @param fields  array of field data for the test case.
        @return: (had_error, messages), where
                   - had_error is true if there was an error
                     executing the test;
                   - messages is a list of error messages
                 Also sets computed_value and test fields in this object.
        """
        self.result = False
        self.computed_value = None
        messages = []

        self.calculate_calculated_fields()

        (ran, msg, exception, points, debugging) = (
            self.credit.execute_formula(self, debug=True))

        if ran:
            try:
                # are we expecting a numeric result?
                self.expected_value = float(self.expected_value)
                (self.computed_value, messages) = self.validate_points(points)
                # Floating point equality to 5rd decimal place
                self.result = (
                    abs(self.computed_value - self.expected_value) < 0.00001)
            # we're not expecting result to be numeric...
            except (TypeError, ValueError):
                self.computed_value = points
                self.result = self.computed_value == self.expected_value
        else:
            # Since this is test, substitute user-friendly
            # message for real error message.
            if isinstance(exception, AssertionError):
                messages.append('Assertion Failed: %s' % exception)
            elif exception:
                messages.append('Formula Error: %s' % exception)
            else:
                messages.append(msg)

        return (len(messages) > 0, messages, debugging)

    def calculate_calculated_fields(self):
        submission_fields = self.get_submission_fields()
        for submission_field in submission_fields:
            if submission_field.documentation_field.type == 'calculated':
                submission_field.calculate()

    def reset_test(self):
        """ reset this test such that the computed_value is None """
        self.computed_value = None
        self.result = self.expected_value == self.computed_value

    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.credit

    def get_edit_url(self):
        return "%s%d/" % (self.credit.get_formula_url(), self.id)

    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%sdelete/" % self.get_edit_url()

    def get_add_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%sadd-test/" % (self.credit.get_formula_url(),)

    def parameter_list(self):
        """ Returns a string with this submission's field values formatted as
            a parameter list.
        """
        return ', '.join([field.__unicode__()
                          for field
                          in self.get_submission_fields()])

    def __unicode__(self):
        return "f( %s ) = %s" % (self.parameter_list(), self.expected_value)

    def get_available_points(self, use_cache=False):
        '''Call CreditSubmission method for reduction of duplication'''
        return self.get_parent_available_points(use_cache=use_cache)


class DataCorrectionRequest(models.Model):
    """
        A request by an institution to make a change to their submission
    """
    date = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    reporting_field = GenericForeignKey('content_type', 'object_id')
    new_value = models.TextField(
        help_text=("Note: if this is a numeric field, be sure to use the "
                   "institution's preference for metric/imperial. You can "
                   "find this in their settings."))
    explanation = models.TextField()
    user = models.ForeignKey(User, blank=True, null=True)
    approved = models.BooleanField(default=False)

    def __unicode__(self):
        return self.reporting_field.documentation_field.title

    def get_absolute_url(self):
        """
            used to link back to the report from the admin
        """
        cus = CreditUserSubmission.objects.get(
            pk=self.reporting_field.credit_submission.id)
        return cus.get_scorecard_url()

    def get_submissionset(self):
        " used to display the submission set in the admin's list_display"
        cus = CreditUserSubmission.objects.get(
            pk=self.reporting_field.credit_submission.id)
        return cus.subcategory_submission.category_submission.submissionset

    def get_required_status(self):
        """
            Used by the admin to indicate if a field is conditionally required
            based on another field
        """
        return self.reporting_field.documentation_field.get_required_display()

    def get_credit(self):
        " Return the credit for the admin list"
        return self.reporting_field.documentation_field.credit

    def save(self):
        """
            Check the approved property to see if this was approved
            If so, confirm that the correction has been applied
        """
        if self.approved:
            try:
                _ = self.applied_correction
            except ReportingFieldDataCorrection.DoesNotExist:
                self.approve()

        return super(DataCorrectionRequest, self).save()

    def approve(self):
        """
            Approving a correction request creates a
            ReportingFieldDataCorrection
        """
        prev_value = self.reporting_field.value
        if prev_value is None:
            prev_value = "--"
        rfdc = ReportingFieldDataCorrection(
            previous_value=prev_value,
            change_date=datetime.today(),
            reporting_field=self.reporting_field,
            explanation=self.explanation,
            request=self)

        if self.reporting_field.documentation_field.type == "choice":
            self.reporting_field.value = Choice.objects.get(
                pk=int(self.new_value))
        elif self.reporting_field.documentation_field.type == "boolean":
            if self.new_value == "Yes":
                self.reporting_field.value = True
            elif self.new_value == "No":
                self.reporting_field.value = False
            else:
                self.reporting_field.value = None

            if rfdc.previous_value is True:
                rfdc.previous_value = "Yes"
            elif rfdc.previous_value is False:
                rfdc.previous_value = "No"
            else:
                rfdc.previous_value = "Unknown"
        elif self.reporting_field.documentation_field.type == "numeric":
            # unit conversion handled by the save() method on the model
            if self.reporting_field.use_metric():
                if self.reporting_field.value is not None:
                    rfdc.previous_value = "%d %s" % (
                        self.reporting_field.metric_value,
                        self.reporting_field.documentation_field.metric_units)
                else:
                    rfdc.previous_value = "---"
                self.reporting_field.metric_value = float(self.new_value)
            else:
                if self.reporting_field.value is not None:
                    rfdc.previous_value = "%d %s" % (
                        self.reporting_field.value,
                        self.reporting_field.documentation_field.us_units)
                else:
                    rfdc.previous_value = "---"
                self.reporting_field.value = float(self.new_value)

        else:
            self.reporting_field.value = self.new_value
        self.reporting_field.save()
        rfdc.save()
        self.approved = True

        # Apply change to overall score.
        cus = CreditUserSubmission.objects.get(
            pk=self.reporting_field.credit_submission.id)
        ss = cus.subcategory_submission.category_submission.submissionset
        score_changed = False
        rating_changed = False
        old_rating = ss.rating
        old_score = ss.score

        if cus.assessed_points != cus._calculate_points():
            cus.assessed_points = cus._calculate_points()
            cus.save()

            score_changed = True

            cus.subcategory_submission.points = None
            cus.subcategory_submission.points = (
                cus.subcategory_submission.get_claimed_points())
            cus.subcategory_submission.save()

            cus.subcategory_submission.category_submission.score = None
            cus.subcategory_submission.category_submission.score = (
                cus.subcategory_submission.category_submission.get_STARS_score())  # noqa
            cus.subcategory_submission.category_submission.save()

            ss.score = None
            ss.score = ss.get_STARS_score()
            ss.save()

            new_rating = ss.get_STARS_rating(recalculate=True)
            if ss.rating != new_rating:
                rating_changed = True
                ss.rating = new_rating
                ss.save()

                institution = ss.institution
                institution.current_rating = institution.get_relative_rating()
                institution.save()

        if ss.pdf_report:
            ss.pdf_report = None
            ss.save()

        # notify institution of approval
        et = EmailTemplate.objects.get(slug='approved_data_correction')
        mail_to = [ss.institution.contact_email]
        if ss.institution.contact_email != self.user.email:
            mail_to.append(self.user.email)
        email_context = {"submissionset": ss,
                         "credit_submission": cus,
                         "score_changed": score_changed,
                         "rating_changed": rating_changed,
                         "old_rating": old_rating,
                         "old_score": old_score}
        et.send_email(mail_to, email_context)


class ReportingFieldDataCorrection(models.Model):
    """
        Represents a change to a particular field in Credit Submission after
        an institution has received a rating.
    """
    request = models.OneToOneField(DataCorrectionRequest,
                                   related_name='applied_correction',
                                   blank=True, null=True)
    previous_value = models.TextField()
    change_date = models.DateField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    reporting_field = GenericForeignKey('content_type', 'object_id')
    explanation = models.TextField(blank=True, null=True)


class DocumentationFieldSubmissionManager(models.Manager):

    def by_submissionset(self, ss):
        """
        Get all the DocumentationFieldSubmissions tied to a SubmissionSet
        """
        lookup = "credit_submission__creditusersubmission"
        lookup += "__subcategory_submission__category_submission"
        lookup += "__submissionset"
        return self.model.objects.filter(**{lookup: ss})


class DocumentationFieldSubmission(models.Model):
    """
        The submitted value for a documentation field (abstract).
    """
    documentation_field = models.ForeignKey(DocumentationField,
                                            related_name="%(class)s_set")
    credit_submission = models.ForeignKey(CreditSubmission)
    corrections = GenericRelation(ReportingFieldDataCorrection,
                                  content_type_field='content_type',
                                  object_id_field='object_id')
    objects = DocumentationFieldSubmissionManager()

    class Meta:
        abstract = True
        unique_together = ("documentation_field", "credit_submission")

    def __unicode__(self):
        """ return the title of this submission field """
        return self.documentation_field.__unicode__()

    def get_flag_url(self):

        link = "%s?content_type=%s&object_id=%d" % (
            urlresolvers.reverse('admin:submissions_flag_add'),
            ContentType.objects.get_for_model(self).id,
            self.id
        )
        return link

    @property
    def flags(self):
        type = ContentType.objects.get_for_model(self)
        return Flag.objects.filter(content_type__pk=type.id, object_id=self.id)

    def get_parent(self):
        """ Used for building crumbs """
        return self.credit_submission

    def get_institution(self):
        parent = CreditUserSubmission.objects.get(
            pk=self.credit_submission.id)
        return parent.get_institution()

    def get_creditset(self):
        return self.credit_submission.creditusersubmission.get_creditset()

    def get_submissionset(self):
        """Returns the SubmissionSet related to this
        DocumentationFieldSubmission.
        """
        return self.credit_submission.creditusersubmission.get_submissionset()

    def persists(self):
        """Does this Submission object persist in the DB?"""
        return (self.pk is not None)

    def get_field_class(field):
        """
           Returns the related DocumentationFieldSubmission model class for a
           particular documentation field
        """
        if field.type == 'text':
            return TextSubmission
        if field.type == 'long_text':
            return LongTextSubmission
        if field.type in ('numeric', 'calculated'):
            return NumericSubmission
        if field.type == 'choice':
            return (ChoiceWithOtherSubmission
                    if field.has_other_choice()
                    else ChoiceSubmission)
        if field.type == 'multichoice':
            return (MultiChoiceWithOtherSubmission
                    if field.has_other_choice()
                    else MultiChoiceSubmission)
        if field.type == 'boolean':
            return BooleanSubmission
        if field.type == 'url':
            return URLSubmission
        if field.type == 'date':
            return DateSubmission
        if field.type == 'upload':
            return UploadSubmission

        return None
    get_field_class = staticmethod(get_field_class)

    def get_human_value(self, get_metric=False):
        """
            Returns a human readable version of the value.

            Pass True as get_metric and for number fields,
            you'll get back a metric value.
        """
        if self.documentation_field.type == 'tabluar':
            return ""
        if self.documentation_field.type == 'upload':
            if self.value:
                return "https://reports.aashe.org%s" % self.value.url
            else:
                return ""
        else:
            # long text has to be truncated for excel
            if not self.value:
                return ""
            else:
                if self.documentation_field.type == 'long_text':
                    str_val = self.value.replace("\r\n", "\n")
                    if len(str_val) > 32000:
                        str_val = "%s ... [TRUNCATED]" % str_val[:32000]
                    return str_val

                elif self.documentation_field.type in ('numeric',
                                                       'calculated'):
                    value = self.metric_value if get_metric else self.value
                    units = (self.documentation_field.metric_units
                             if get_metric
                             else self.documentation_field.units)

                    str_val = "%.2f" % value if value is not None else ''
                    if str_val[-3:] == '.00':
                        str_val = str_val[:-3]
                    if units:
                        return "%s %s" % (str_val, units)
                    return str_val

                elif self.documentation_field.type == "choice":
                    return self.value.choice

                elif self.documentation_field.type == "multichoice":
                    value = ""
                    for choice in self.value.all():
                        if value:
                            value += "|"
                        value += str(choice)
                    return value

                else:
                    return self.value

    def save(self, *args, **kwargs):
        # Only save submission fields if the overall submission has been saved.
        if not self.credit_submission.persists():
            return
        super(DocumentationFieldSubmission, self).save(*args, **kwargs)

    def get_value(self):
        """ Use this accessor to get this submission's value - rather than
            accessing .value directly """
        return self.value

    def is_empty(self):
        if self.documentation_field.type != "multichoice":
            if self.value is None or self.value == "":
                return True
            # if it's a string and nothing but whitespace
            # will need to change when moving to Python3
            if isinstance(self.value, basestring):
                if re.match("^\s+$", self.value) is not None:
                    return True
            return False
        else:  # This is a multichoice field
            return self.value.count() == 0
        return False

    def get_correction_url(self):
        return "%s%d/" % (self.credit_submission.get_scorecard_url(),
                          self.documentation_field.id)


class AbstractChoiceSubmission(DocumentationFieldSubmission):
    class Meta:
        abstract = True

    def __unicode__(self):
        """ return a string representation of the submission' value """
        choice = self.get_value()
        return self._get_str(choice)

    @staticmethod
    def _get_str(choice):
        return ('<%d:%s>' % (choice.ordinal, choice.choice)
                if choice
                else '<None>')

    def get_choice_queryset(self):
        """Return the queryset used to define the choices for this
           submission"""

        return Choice.objects.filter(
            documentation_field=self.documentation_field).filter(
                is_bonafide=True)

    def get_last_choice(self):
        """ Return the last Choice object in the list of choices for this
            submission """
        choices = self.get_choice_queryset()
        if len(choices) > 0:
            return choices[len(choices)-1]  # no negative indexing on QuerySets
        else:
            return None


class ChoiceSubmission(AbstractChoiceSubmission):
    """
        The submitted value for a Single Choice Documentation Field
    """
    value = models.ForeignKey(Choice, blank=True, null=True)

    def get_value(self):
        """ Value is a Choice object, or None """
        return self.value


class AbstractChoiceWithOther(object):
    """
        A base class for sharing the compress / decompress logig needed
        for Choice-with-other type submisssions
    """

    def compress(self, choice, other_value):
        """
            Given a decompressed choice / other value pair into a single
            Choice value Return a single Choice representing the
            selection, or None.  Assumes choice is a Choice and
            other_value has been properly sanatized!  See decompress()
            above, except compress is peformed during clean() in
            ModelChoiceWithOtherField
        """
        if not choice:
            return None
        if choice == self.get_last_choice() and other_value:
            # The value is an 'other' - create the Choice object
            # search for the 'other' choice value first - try to
            # re-use an existing choice.
            find = Choice.objects.filter(
                documentation_field=self.documentation_field).filter(
                    choice=other_value)  # @todo: can this be case insensitive?
            if len(find) > 0:
                choice = find[0]
            else:
                choice = Choice(documentation_field=self.documentation_field,
                                choice=other_value,
                                is_bonafide=False)
                choice.save()

        return choice


class ChoiceWithOtherSubmission(ChoiceSubmission, AbstractChoiceWithOther):
    """
        A proxy model (does not create a new table) for a Choice
        Submission with an 'other' choice
    """
    class Meta:
        proxy = True

    def decompress(self, value):
        """
            Given a single value (the pk for a Choice object),
            return a list of the form: [choiceId, otherValue], where

             - choiceId is the id of the selection choice and
               otherValue is the the text value of the choice, if it
               is a non-bonafide (other) choice.

            This is really the decompress logic for a
            ChoiceWithOtherSelectWidget (MutliWidget), but needs to do
            "model"-type stuff, so it is passed to the widget via the
            form.
        """
        if not value:
            return [None, None]
        # The choice must be in the DB - this algorithm is not
        # foolproof - could use a little more thought.
        try:
            choice = Choice.objects.get(id=value)
        except:
            logger.error("Attempt to decompress non-existing Choice (id=%s)" %
                         value, exc_info=True)
            return [None, None]
        if choice.is_bonafide:  # One of the actual choices
            return [value, None]
        else:                   # whereas non-bonafide choices
                                # represent an 'other' choice.

            # value is not one of the bonafide choices - try to find
            # it in the DB.  The selection is the last choice, and the
            # Choice text is the 'other' field.
            return [self.get_last_choice().pk, choice.choice]

    def compress(self, choice, other_value):
        """
            Given a decompressed choice / other value pair into a
            single Choice value

            Return a single Choice representing the selection, or
            None.

            Assumes choice is a Choice and other_value has been
            properly sanatized!

            See decompress() above, except compress is peformed during
            clean() in ModelChoiceWithOtherField
        """
        # Warn the user about potentially lost data
        last_choice = self.get_last_choice()
        if other_value and choice != last_choice:
            logger.warning(
                "'%s' will not be saved because '%s' was not selected." %
                (other_value, last_choice.choice))
        return super(ChoiceWithOtherSubmission, self).compress(choice,
                                                               other_value)


class MultiChoiceSubmission(AbstractChoiceSubmission):
    """
        The submitted value for a Multi-Choice Documentation Field
    """
    # should be called values, really, since it potentially
    # represents multiple values
    value = models.ManyToManyField(Choice, blank=True)

    def get_value(self):
        """ Value is a list of Choice objects, or None """
        # got to be careful here - many-to-many is only valid
        # after submission has been saved.
        return self.value.all() if self.persists() else None

    def __unicode__(self):
        """ return a string representation of the submission' value """
        choices = self.get_value()
        if not choices:
            return "[ ]"
        return '[%s]' % ','.join([self._get_str(choice) for choice in choices])


class MultiChoiceWithOtherSubmission(MultiChoiceSubmission,
                                     AbstractChoiceWithOther):
    """
        A proxy model (does not create a new table) for a MultiChoice
        Submission with an 'other' choice
    """
    class Meta:
        proxy = True

    def decompress(self, value):
        """
            Given a list of values (list of pk for Choice objects),
            return a list of the form: [[choiceId1, choiceId2],
            otherValue], where

             - choiceId's are the id's of the selected choices and
               otherValue is the the text value of the choice, if it
               is a non-bonafide (other) choice.

            This is really the decompress logic for a
            SelectMultipleWithOtherWidget (MutliWidget), but needs to
            do "model"-type stuff, so it is passed to the widget via
            the form.
        """
        if not value:
            return [[], None]
        # The choice must be in the DB - this algorithm is not
        # foolproof - could use a little more thought.
        choice_list = []
        other = None
        for choice_id in value:
            try:
                choice = Choice.objects.get(id=choice_id)
            except:
                logger.error(
                    "Attempt to decompress non-existing Choice (id=%s)" %
                    choice_id, exc_info=True)
                return [[], None]
            if not choice.is_bonafide:  # An 'other' choice replace
                                        # the choice with the last
                                        # choice.
                if other:
                    logger.error(
                        "Found multiple 'other' choices "
                        "(%s and %s) associated with single "
                        "MultiChoiceWithOtherSubmission (id=%s)" %
                        (other, choice.choice, self.id))
                else:
                    choice_id = self.get_last_choice().pk
                    other = choice.choice
            choice_list.append(choice_id)

        return [choice_list, other]

    def compress(self, choices, other_value):
        """
            Given a decompressed choice list / other value pair into a
            single Choice list, return a list of Choices representing
            the selections, or None.

            Assumes choices is a list of Choices and other_value has
            been properly sanatized!

            See decompress() above, except compress is peformed during
            clean() in ModelMultipleChoiceWithOtherField
        """
        choice_list = []
        for choice in choices:
            choice_list.append(super(MultiChoiceWithOtherSubmission,
                                     self).compress(choice, other_value))

        # Warn the user about potentially lost data
        last_choice = self.get_last_choice()
        if other_value and last_choice not in choices:
            logger.warning(
                "'%s' will not be saved because '%s' was not selected." %
                (other_value, last_choice.choice))

        return choice_list


class URLSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a URL Documentation Field
    """
    value = models.URLField(blank=True, null=True)


class DateSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a Date Documentation Field
    """
    value = models.DateField(blank=True, null=True)


class NumericSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a Numeric Documentation Field

        This DocumentationFieldSubmission has an extra field, `metric_value`

        Logic:
            The form and model use slightly different logic. The form needs to
            know if it should display the `value` or `metric_value` field. And
            the model needs to know if it should convert the data from one
            field to the other.

            This is handled with two methods:
                `requires_duplication` - uses the documentation field
                        - `DocumentationField` has a `units` and
                        - the `metric_units` and `us_units` are not the same
                            (MMBTU is metric, but used the US too)
                `use_metric` - uses institution preference

            Model:
                The model will save both fields when the other could be needed

                The times when population is needed
                    `value` to `metric_value`
                        - duplication required
                        - institutions prefers us units
                    `metric_value` to `value`
                        - duplication required
                        - institutions prefers metric units

                Otherwise, there is no need for the metric field to be
                populated

            Form:
                The form needs to display the correct field and validate.

                Picking the field:
                    `value`:
                        - if the institution doesn't prefer metric
                        - if the institution prefers metric, but duplication
                        isn't required
                    `metric_value`:
                        - if the institution prefers metric and duplication is
                        required

                Validating:
                    if displaying the `metric_field` populate the `value` field
                    prior to validating

            The logic description here is necessary, because these are coupled,
            since the model has to know which value field to use to populate
            the other. For example, if the institution's preference is for
            metric, but the form displays `value` because there are no units,
            then the

            "then the" what?  I'm confused!
    """
    value = models.FloatField(blank=True, null=True)
    metric_value = models.FloatField(blank=True, null=True)

    @property
    def init_track_fields(self):
        return ['value']

    def requires_duplication(self):
        """
            Determines if this instance needs to have both `value` and
            `metric_values` stored in the database
        """
        df = self.documentation_field
        return df.units and (df.us_units != df.metric_units)

    def use_metric(self):
        """
            Logic to determine if the `metric_value` field should be used. This
            is shared with the form, so it makes sense to add it to the model
        """
        if not hasattr(self, 'credit_submission'):
            # It's not a real submission, just an example in
            # the credit editor, just an in-memory, unbound
            # object, and so without a 'credit_submission'
            # attribute.
            return False
        # Test submissions don't have institutions:
        if self.credit_submission.is_test():
            return False
        if self.requires_duplication():
            institution = self.get_institution()
            return institution.prefers_metric_system
        return False

    def run_formula(self, locals, log_exceptions=True):

        globals = {}  # __builtins__ gets added automatically

        # exec formula in restricted namespace
        try:
            exec self.documentation_field.formula in globals, locals
        except AssertionError:
            raise
        except Exception, exc:
            if log_exceptions:
                logger.exception(
                    "Formula Exception for formula `{formula}`: "
                    "{exception}; "
                    "Documentation field: {documentation_field_edit_url}; "
                    "locals: {locals}.".format(
                        formula=self.documentation_field.formula,
                        exception=str(exc),
                        documentation_field_edit_url=self.documentation_field.get_edit_url(),
                        documentation_field=self.documentation_field,
                        locals={key: value for key, value in locals.items()
                                if (type(value) in (int, float) or
                                    value is None)}))
            return None
        return locals['value']

    def calculate(self, log_exceptions=True):
        """
        Calculate self.documentation_field.formula.
        """
        if not self.documentation_field.formula:
            self.value = None
            return

        # get the key that relates field identifiers to their values
        imperial_locals = self.credit_submission.get_submission_field_key()
        imperial_locals.update({"value": None})
        self.value = self.run_formula(imperial_locals, log_exceptions=True)

        if self.requires_duplication():
            metric_locals = self.credit_submission.get_submission_field_key(metric=True)
            metric_locals.update({"value": None})
            self.metric_value = self.run_formula(metric_locals, log_exceptions=True)


    def save(self,
             recalculate_related_calculated_fields=True,
             log_calculation_exceptions=True,
             *args, **kwargs):
        """
            Override the save method to
                1. generate the metric value, and
                2. recalculate any related calculated fields, when neccesary.
        """

        if self.requires_duplication():
            if self.use_metric():
                if self.metric_value is not None:
                    units = self.documentation_field.metric_units
                    self.value = units.convert(self.metric_value)
                else:
                    self.value = None
            else:
                if self.value:
                    units = self.documentation_field.us_units
                    self.metric_value = units.convert(self.value)
                else:
                    self.metric_value = None

        super(NumericSubmission, self).save(*args, **kwargs)

        if (self.value != self._original_value and
            recalculate_related_calculated_fields):  # noqa

            # If this field is used in any calculated fields ...
            for calculated_field in (
                    self.documentation_field.calculated_fields.all()):
                # ... recalculate those fields:

                for calculated_field_submission in (
                        NumericSubmission.objects.filter(
                            documentation_field=calculated_field,
                            credit_submission=self.credit_submission).exclude(
                                pk=self.pk)):

                    calculated_field_submission.calculate(
                        log_exceptions=log_calculation_exceptions)

                    if (calculated_field_submission.value !=
                        calculated_field_submission._original_value):  # NOQA

                        calculated_field_submission.save(
                            recalculate_related_calculated_fields,
                            log_calculation_exceptions,
                            *args, **kwargs)


def numeric_submission_post_init(sender, instance, **kwargs):
    for field in instance.init_track_fields:
        setattr(instance,
                '_original_%s' % field,
                getattr(instance, field, None))


post_init.connect(
    numeric_submission_post_init,
    sender=NumericSubmission,
    dispatch_uid='stars.apps.submissions.models.numeric_submission_post_init')


class TextSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a Text Documentation Field
    """
    value = models.CharField(max_length=255, blank=True, null=True)


class LongTextSubmission(DocumentationFieldSubmission):
    """
        The submitted value for Long Text Documentation Field
    """
    value = models.TextField(blank=True, null=True)


def upload_path_callback(instance, filename):
    """
        Dynamically alters the upload path based on the instance
        secure/<org_id>/<creditset_id>/<credit_id>/<field_id>/<file_name>.<ext>
    """

    if instance.credit_submission.__class__.__name__ == "CreditUserSubmission":
        field = instance.documentation_field
        credit = field.credit
        creditset = field.credit.subcategory.category.creditset
        institution = instance.get_institution()
        path = "secure/%d/%d/%d/%d/%s" % (institution.id, creditset.id,
                                          credit.id, field.id, filename)
        return path
    else:
        # if this is a test submission use a different URL
        return "uploads/test_cases/%s" % filename


class UploadSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a File Upload Documentation Field
        @todo: custom storage engine to rename files
    """
    value = models.FileField(
        upload_to=upload_path_callback,
        blank=True,
        max_length=255,
        null=True)

    def get_filename(self):
        """ Returns the name of the file w/out the full path. """
        return os.path.basename(self.value.name)

    def get_admin_url(self):
        url = urlresolvers.reverse(
            'admin:submissions_uploadsubmission_change',
            args=(self.id,))
        return url


class BooleanSubmission(DocumentationFieldSubmission):
    """
        The submitted value for a Boolean Documentation Field
    """
    value = models.NullBooleanField(blank=True, null=True)

    def __unicode__(self):
        if self.value is True:
            return "Yes"
        elif self.value is False:
            return "No"
        else:
            return "---"


PAYMENT_REASON_CHOICES = (
    ('member_reg', 'member_reg'),
    ('nonmember_reg', 'nonmember_reg'),
    ('member_renew', 'member_renew'),
    ('nonmember_renew', 'nonmember_renew'),
    ('international', 'international')
)

PAYMENT_TYPE_CHOICES = (
    ('credit', 'credit'),
    ('check', 'check'),
    ('later', 'pay later'),
)

# used by template tag to create iconic representation of paymnet
PAYMENT_TYPE_ICONS = {
    'credit': ('creditcards.png', 'Paid by credit'),
    'check': ('check.png', 'Paid by check'),
    'later': ('flag_red.png', 'Awaiting payment'),
}


class Payment(models.Model):
    """
        Any payment associated with submissions such as registration
    """
    submissionset = models.ForeignKey(SubmissionSet)
    date = models.DateTimeField()
    amount = models.FloatField()
    user = models.ForeignKey(User)
    reason = models.CharField(max_length=16, choices=PAYMENT_REASON_CHOICES)
    type = models.CharField(max_length=8, choices=PAYMENT_TYPE_CHOICES)
    confirmation = models.CharField(
        max_length=16, blank=True, null=True,
        help_text='The CC confirmation code or check number')

    def __unicode__(self):
        return "%s $%.2f" % (self.date, self.amount)

    @classmethod
    def get_manage_url(cls):
        return "%spayments/" % settings.MANAGE_INSTITUTION_URL

    @classmethod
    def get_admin_url(cls):
        return "%spayments/" % settings.ADMIN_URL

    def get_admin_institution_url(self):
        return self.submissionset.institution.get_admin_payments_url()

    def get_edit_url(self):
        return "%s%d/edit/" % (self.get_admin_url(), self.id)

    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%s%d/delete/" % (self.get_admin_url(), self.id)

    def get_receipt_url(self):
        """ Returns a URL for the page where staff can send a receipt """
        return "%s%d/receipt/" % (self.get_admin_url(), self.id)

    def get_institution(self):
        return self.submissionset.institution


class SubmissionInquiry(models.Model):
    """
        An inquiry by a member of the public about any inaccurate data in
        a public report
    """

    submissionset = models.ForeignKey(SubmissionSet)
    date = models.DateTimeField(auto_now_add=True)
    anonymous = models.BooleanField(default=False)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    affiliation = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=32, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    email_address = models.EmailField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    additional_comments = models.TextField(
        blank=True, null=True,
        help_text=("Include any other comments about the Submission, "
                   "including the Submission Boundary and Subcategory "
                   "Descriptions."))

    class Meta:
        verbose_name_plural = "Submission Inquiries"

    def __unicode__(self):
        return self.submissionset.institution.name


class CreditSubmissionInquiry(models.Model):
    """
        An inquiry, tied to a SubmissionInquiry about a particular credit.
    """

    submission_inquiry = models.ForeignKey(SubmissionInquiry)
    credit = models.ForeignKey(Credit)
    explanation = models.TextField()

    class Meta:
        verbose_name_plural = "Credit Submission Inquiries"

    def __unicode__(self):
        return self.credit.title


class ExtensionRequest(models.Model):
    """
        Schools can request a 6 month extension for their submission
    """

    submissionset = models.ForeignKey(SubmissionSet)
    old_deadline = models.DateField()
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return str(self.date)


class SubcategoryQuartiles(models.Model):
    """Cached statistics for Subcategories.

    Caches the quartiles for submissions, grouped by subcategory and institution_type.

    Values cached (first, second, third, fourth) are the highest numbers
    of each quartile.  The numbers represent the percentage of available
    points granted to a submission, not the number of points granted.
    """
    subcategory = models.ForeignKey(Subcategory)
    institution_type = models.CharField(max_length=128,
                                        default='')
    first = models.FloatField(default=0)
    second = models.FloatField(default=0)
    third = models.FloatField(default=0)
    fourth = models.FloatField(default=0)

    class Meta:
        unique_together = ("subcategory", "institution_type")

    def calculate(self):
        """Calculate the quartiles.  Only count rated submissions.
        """
        subcategory_submissions = SubcategorySubmission.objects.filter(
            subcategory=self.subcategory,
            category_submission__submissionset__status=RATED_SUBMISSION_STATUS)
        points_percent = []

        for subcategory_submission in subcategory_submissions:
            if (subcategory_submission.get_submissionset().get_institution_type() ==  # noqa
                self.institution_type):  # noqa

                adjusted_available_points = (
                    subcategory_submission.get_adjusted_available_points())

                if adjusted_available_points:

                    points_percent.append(
                        (subcategory_submission.get_claimed_points() /
                         adjusted_available_points) * 100)

        if sum(points_percent):
            array = numpy.array(points_percent)
            self.first, self.second, self.third, self.fourth = (
                numpy.percentile(array, numpy.arange(25, 101, 25)))
        else:
            self.first = self.second = self.third = self.fourth = 0
        self.save()


CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS = {
    "BEST_PRACTICE": "best-practice",
    "REVISION_REQUEST": "revision-request",
    "SUGGESTION_FOR_IMPROVEMENT": "suggestion-for-improvement"}

CREDIT_SUBMISSION_REVIEW_NOTATION_KIND_CHOICES = (
    (CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS["BEST_PRACTICE"],
     "Best Practice"),
    (CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS["REVISION_REQUEST"],
     "Revision Request"),
    (CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS["SUGGESTION_FOR_IMPROVEMENT"],
     "Suggestion For Improvement"))


class CreditSubmissionReviewNotation(models.Model):

    credit_user_submission = models.ForeignKey(CreditUserSubmission)
    kind = models.CharField(
        max_length=32,
        choices=CREDIT_SUBMISSION_REVIEW_NOTATION_KIND_CHOICES)
    comment = models.TextField(blank=True, null=True)
    send_email = models.BooleanField(blank=True, default=True)
    email_sent = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ("kind",
                    "credit_user_submission__credit__identifier",
                    "id")

    def is_unlocking_kind(self):
        """Is this a kind of Notation that should unlock a Credit Submission
           when it's under review?
        """
        unlocking_kinds = [
            CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS[
                "REVISION_REQUEST"],
            CREDIT_SUBMISSION_REVIEW_NOTATION_KINDS[
                "SUGGESTION_FOR_IMPROVEMENT"]]
        return self.kind in unlocking_kinds

    def save(self, *args, **kwargs):
        new_credit_submission_review_notification = not self.pk

        if self.pk:
            # Don't let the kind of this CreditSubmissionReviewNotation change.
            self.kind = (
                CreditSubmissionReviewNotation.objects.get(pk=self.pk).kind)

        super(CreditSubmissionReviewNotation, self).save(*args, **kwargs)

        if (new_credit_submission_review_notification and
            self.is_unlocking_kind() and
            not self.credit_user_submission.is_unlocked_for_review):  # noqa

            self.credit_user_submission.is_unlocked_for_review = True
            self.credit_user_submission.save(calculate_points=False)


@receiver(pre_delete)
def pre_delete_credit_submission_review_notation(sender, instance, **kwargs):
    """If the CreditSubmissionReviewNotation being deleted is the only one
       for the related CreditSubmission that would cause it to be
       unlocked for review, lock that mother back up.
    """
    if sender == CreditSubmissionReviewNotation:
        credit_user_submission = instance.credit_user_submission
        if credit_user_submission.is_unlocked_for_review:
            for review_notation in (
                    credit_user_submission.creditsubmissionreviewnotation_set.
                    exclude(pk=instance.pk)):
                if review_notation.is_unlocking_kind():
                    return  # Keep the Credit Submission unlocked
        credit_user_submission.is_unlocked_for_review = False
        credit_user_submission.save(calculate_points=False)
