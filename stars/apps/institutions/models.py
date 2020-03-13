import collections
from datetime import date
from dateutil.relativedelta import relativedelta
from logging import getLogger

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models import Max
from django.core.mail import send_mail
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from iss.models import Organization

from stars.apps.credits.models import CreditSet


logger = getLogger('stars')


@receiver(user_logged_in)
def pending_accounts_callback(sender, **kwargs):
    """
        Catch the `user_logged_in` signal and convert any
        Pending Accounts for the logged in user
    """
    user = kwargs['user']
    PendingAccount.convert_accounts(user)


class SubscriptionPurchaseError(Exception):
    pass


class ClimateZone(models.Model):
    """
        Climate Zones. Making this a model allows staff to create
        zones that are outside of the USDOE climate regions
    """
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class MemberSuiteInstitutionManager(models.Manager):

    def get_queryset(self):
        qs = super(MemberSuiteInstitutionManager, self).get_queryset()
        return qs.exclude(exclude_from_website=True)


# HEY! Here's something to notice: though the model below is called
# MemberSuiteInstitution, it's a subclass of Organization, not
# Institution, as you might assume.
class MemberSuiteInstitution(Organization):

    objects = MemberSuiteInstitutionManager()

    class Meta:
        proxy = True

    def __str__(self):
        if self.state:
            return '{}, {}'.format(self.org_name, self.state)
        else:
            return self.org_name

    def update_related_institution(self):
        try:
            institution = Institution.objects.get(ms_institution=self)
        except Institution.DoesNotExist:
            return
        else:
            institution.name = self.org_name
            institution.update_from_iss()
            institution.save()


class InstitutionManager(models.Manager):
    """
        Adds some custom query functionality to the Institution object
    """

    def get_rated(self):
        """ All submissionsets that have been rated """
        return Institution.objects.filter(
            enabled=True).filter(current_rating__isnull=False)

    def get_participants_and_reports(self):
        return Institution.objects.filter(
            enabled=True).exclude(name='AASHE Example University')


class InvalidAccessLevelError(Exception):
    pass


class Institution(models.Model):
    """
        This model represents a STARS institution. The institution name
        is a mirror of Salesforce and will require regular updating
    """
    objects = InstitutionManager()

    ms_institution = models.OneToOneField(MemberSuiteInstitution,
                                          null=True,
                                          blank=True)

    slug = models.SlugField(unique=True, max_length=255)
    enabled = models.BooleanField(
        help_text=("This is a staff-only flag for disabling an "
                   "institution. An institution will NOT appear on "
                   "the STARS Institutions list until it is enabled."),
        default=True)
    contact_first_name = models.CharField("Liaison First Name", max_length=32)
    contact_middle_name = models.CharField("Liaison Middle Name",
                                           max_length=32,
                                           blank=True,
                                           null=True)
    contact_last_name = models.CharField("Liaison Last Name", max_length=32)
    contact_title = models.CharField("Liaison Title", max_length=255,
                                     blank=True, null=True)
    contact_department = models.CharField("Liaison Department", max_length=64,
                                          blank=True, null=True)
    contact_email = models.EmailField("Liaison Email", blank=True, null=True)
    executive_contact_first_name = models.CharField(max_length=32,
                                                    blank=True,
                                                    null=True)
    executive_contact_middle_name = models.CharField(max_length=32,
                                                     blank=True,
                                                     null=True)
    executive_contact_last_name = models.CharField(max_length=32,
                                                   blank=True,
                                                   null=True)
    executive_contact_title = models.CharField(max_length=64,
                                               blank=True,
                                               null=True)
    executive_contact_department = models.CharField(max_length=64,
                                                    blank=True,
                                                    null=True)
    executive_contact_email = models.EmailField(blank=True, null=True)
    executive_contact_address = models.CharField(max_length=128,
                                                 blank=True,
                                                 null=True)
    executive_contact_city = models.CharField(max_length=16,
                                              blank=True,
                                              null=True)
    executive_contact_state = models.CharField(max_length=2,
                                               blank=True,
                                               null=True)
    executive_contact_zip = models.CharField(max_length=8,
                                             blank=True,
                                             null=True)

    # Contact information for the president
    president_first_name = models.CharField(max_length=32,
                                            blank=True,
                                            null=True)
    president_middle_name = models.CharField(max_length=32,
                                             blank=True,
                                             null=True)
    president_last_name = models.CharField(max_length=32,
                                           blank=True,
                                           null=True)
    president_title = models.CharField(max_length=64, blank=True, null=True)
    president_email = models.EmailField(blank=True, null=True)
    president_address = models.CharField(max_length=128, blank=True, null=True)
    president_city = models.CharField(max_length=32, blank=True, null=True)
    president_state = models.CharField(max_length=2, blank=True, null=True)
    president_zip = models.CharField(max_length=8, blank=True, null=True)

    charter_participant = models.BooleanField(default=False)
    stars_staff_notes = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True,
                                        blank=True,
                                        null=True,
                                        db_index=True)
    international = models.BooleanField(default=False)

    name = models.CharField(max_length=255)
    aashe_id = models.IntegerField(unique=True, blank=True, null=True)
    fte = models.IntegerField(blank=True, null=True)
    is_pcc_signatory = models.NullBooleanField(default=False)
    is_member = models.NullBooleanField(default=False)
    is_pilot_participant = models.NullBooleanField(default=False)
    country = models.CharField(max_length=128, blank=True, null=True)
    institution_type = models.CharField(max_length=128, blank=True, null=True)

    current_rating = models.ForeignKey("credits.Rating", blank=True, null=True)
    rating_expires = models.DateField(blank=True, null=True)
    current_submission = models.ForeignKey("submissions.SubmissionSet",
                                           blank=True,
                                           null=True,
                                           related_name="current")
    current_subscription = models.ForeignKey("Subscription",
                                             blank=True,
                                             null=True,
                                             related_name='current')
    rated_submission = models.ForeignKey("submissions.SubmissionSet",
                                         blank=True,
                                         null=True,
                                         related_name='rated')
    latest_expired_submission = models.ForeignKey(
        "submissions.SubmissionSet",
        blank=True,
        null=True,
        related_name='latest_expired')
    prefers_metric_system = models.BooleanField(default=False)
    is_test_institution = models.BooleanField(default=False,
                                              db_index=True)

    @property
    def is_participant(self):
        # Import in here to avoid circular dependency.
        from stars.apps.submissions.models import REVIEW_SUBMISSION_STATUS
        # Folks with a report in review mode always get full access.
        submission = self.current_submission
        if (submission and
            (submission.status == REVIEW_SUBMISSION_STATUS)):  # noqa

            return True

        else:
            return (self.current_subscription and
                    self.current_subscription.access_level ==
                        Subscription.FULL_ACCESS)  # noqa

    def __unicode__(self):
        return self.name

    @classmethod
    def get_institution_types(cls):
        institution_type_values = cls.objects.exclude(
            institution_type=None).values(
                'institution_type').distinct()
        institution_types = [
            institution_type_value["institution_type"]
            for institution_type_value
            in institution_type_values]
        return institution_types

    @property
    def access_level(self):
        # Import in here to avoid circular dependency.
        from stars.apps.submissions.models import REVIEW_SUBMISSION_STATUS

        submission = self.current_submission

        if (submission and
            (submission.status == REVIEW_SUBMISSION_STATUS)):  # noqa

            # Everybody gets full access while their submission
            # is in review mode.
            return Subscription.FULL_ACCESS

        elif self.current_subscription:
            return self.current_subscription.access_level

        else:
            return Subscription.BASIC_ACCESS

    def older_than_three_years(self):
        try:
            return (date.today() > (self.rated_submission.date_submitted +
                                    relativedelta(years=3)))
        except AttributeError:
            return False
        return True

    def get_relative_rating(self):
        """New ratings aren't always considered an Insitution's 'current'
        rating.  A 'Reporter' rating, for instance, shouldn't obscure
        any higher-rated submission that has not yet expired.

        """
        # Import in here to avoid circular dependency.
        from stars.apps.submissions.models import RATING_VALID_PERIOD

        if (self.current_rating and
            self.current_rating.name == "Reporter"):  # noqa
            # Is there another public, rated submission for this
            # Institution with a current, non-reporter rating?
            other_submissions = self.submissionset_set.filter(
                rating__publish_score=True,
                date_submitted__gte=(
                    date.today() -
                    RATING_VALID_PERIOD)).exclude(
                        rating__name="Reporter").order_by(
                            "-date_submitted")
            if other_submissions:
                return other_submissions[0].rating
            else:
                return self.current_rating
        else:
            return self.current_rating

    def update_current_rating(self):
        # Clear current_rating if it's expired.
        if self.rating_expires and self.rating_expires <= date.today():
            # if the rated submission has expired remove the rating
            self.current_rating = None
            self.rating_expires = None
        else:
            # update the rating
            self.current_rating = self.get_relative_rating()

    def update_current_subscription(self):

        def look_for_current_subscription():
            for sub in self.subscription_set.all():
                if (sub.start_date <= date.today() and
                    sub.end_date >= date.today()):  # noqa
                    self.current_subscription = sub
                    break

        # Check subscription is current
        if self.current_subscription:
            if (self.current_subscription.start_date <= date.today() and
                self.current_subscription.end_date >= date.today()):  # noqa
                pass
            else:
                self.current_subscription = None
                # if it has expired, check and see if there is another
                # that is current
                look_for_current_subscription()
        # If no current subscription, look for one:
        else:
            look_for_current_subscription()

    def update_from_iss(self):
        "Method to update properties from the parent org in the ISS"

        FieldMapping = collections.namedtuple('FieldMapping',
                                              'stars_field iss_field decode')

        field_mappings = (FieldMapping(stars_field="name",
                                       iss_field="org_name",
                                       decode=True),
                          FieldMapping(stars_field="aashe_id",
                                       iss_field="account_num",
                                       decode=False),
                          FieldMapping(stars_field="institution_type",
                                       iss_field="institution_type",
                                       decode=False),
                          FieldMapping(stars_field="fte",
                                       iss_field="enrollment_fte",
                                       decode=False),
                          FieldMapping(stars_field="is_pcc_signatory",
                                       iss_field="is_signatory",
                                       decode=False),
                          FieldMapping(stars_field="is_member",
                                       iss_field="is_member",
                                       decode=False),
                          FieldMapping(stars_field="is_pilot_participant",
                                       iss_field="pilot_participant",
                                       decode=False),
                          FieldMapping(stars_field="country",
                                       iss_field="country",
                                       decode=True))

        iss_org = self.profile

        if iss_org:
            for fm in field_mappings:
                val = getattr(iss_org, fm.iss_field)
                if not isinstance(val, unicode) and fm.decode and val:
                    # decode if necessary from the latin1
                    val = val.decode('latin1').encode('utf-8')
                setattr(self, fm.stars_field, val)

            # additional membership logic for child members
            if not self.is_member:
                if getattr(iss_org, 'member_type') == "Child Member":
                    self.is_member = True

        else:
            logger.warning("No ISS institution found %s" % (
                self.name.decode('utf-8')))

    def get_admin_url(self):
        """ Returns the base URL for AASHE Staff to administer aspects of
        this institution """
        return "%sinstitution/%d/" % (settings.ADMIN_URL, self.id)

    def get_masquerade_url(self):
        """ Returns the URL for AASHE Staff to masquerade this institution """
        return "%sinstitution/masquerade/%d/" % (settings.ADMIN_URL, self.id)

    def get_manage_url(self):
        """ Returns the URL for institution admins to edit this institution """
        return settings.MANAGE_INSTITUTION_URL

    def get_admin_payments_url(self):
        """ Returns the URL for administering this institution's payments """
        return "%spayments/" % self.get_admin_url()

    def has_multiple_submissions(self):
        """ Return True if this institution has more than one
        submission set """
        return self.submissionset_set.count() > 1

    def get_submissions(self, include_unrated=False):
        """ Return the institutions SubmissionSets, reverse chron.,
        perhaps excluding the unrated ones """
        submissions = self.submissionset_set.all()
        if not include_unrated:  # include only rated submissions
            submissions = submissions.filter(
                status='r').filter(
                is_visible=True).filter(
                is_locked=False)
        return submissions.order_by("-date_registered")

    def get_latest_submission(self, include_unrated=False):
        """ Return the institutions most recent SubmissionSet,
        perhaps excluding the unrated ones """
        try:
            return self.get_submissions(
                include_unrated).order_by("-date_submitted")[0]
        except:
            return None

    def get_location_string(self):
        """Returns a string specifying the location of this institution."""
        if self.profile is not None:
            location = self.profile.city
            if location is not None:
                for field in (self.profile.state, self.profile.country_iso):
                    if location and field:
                        location += ', '
                    location += field
            else:
                location = ''
        else:
            location = ''
        return location

    def get_payments(self):
        """ Return the latest payment for this institution """
        payments = []
        for ss in self.submissionset_set.all():
            for p in ss.payment_set.all():
                payments.append(p)
        return payments

    def get_active_submission(self):
        """ Returns the current SubmissionSet for this institution """
        return self.current_submission

    def set_active_submission(self, submission_set):
        """ Set this institution's active SubmissionSet """
        self.current_submission = submission_set
        self.save()

    def get_latest_rated_submission(self):
        """ Returns the most recent rated SubmissionSet for this
        institution """
        if self.submissionset_set.filter(status='r').count() > 0:
            return self.submissionset_set.filter(
                status='r').order_by('-date_submitted')[0]

    def is_registered(self, creditset=None):
        """ Return True if this institution is registered for the given
        credit set creditset - if None, the latest creditset will be
        checked. """
        if not creditset:
            creditset = CreditSet.objects.get_latest()

        for submission in self.submissionset_set.all():
            if submission.creditset == creditset:
                return True
        # assert: no submission has been registered for the given credit
        # set for this institution
        return False

    def is_published(self):
        """ Returns true if the institution has a rating that's less
        than three years old or if the institution has a current paid
        submission """

        if self.enabled:
            for ss in self.submissionset_set.all():
                if ss.status == "r":
                    return True
                elif ss.is_enabled():
                    return True

        return False

    @property
    def profile(self):
        return self.ms_institution

    def is_member_institution(self):
        """
            Searches stars_member_list.members for the institution
            returns True if this institution exists
        """
        return self.is_member

    def set_slug_from_iss_institution(self, iss_institution_id):
        """
            Sets the slug field based on an institution row from the ISS
        """
        try:
            if self.aashe_id is None:
                self.aashe_id = iss_institution_id
            state = (self.profile.state.lower() if self.profile.state
                     else "no-state")
            slug_base = '%s-%s' % (self.profile.org_name, state)
            self.slug = slugify(slug_base)
        except Exception as e:
            logger.error("Can't set slug for %s: %s" % (
                self.profile.org_name, e), exc_info=True)
            self.slug = iss_institution_id

    def get_last_subscription_end(self):
        """
            Gets the end date for the last subscription in
            all subscriptions for this institution
        """
        last_subscription_end = None
        if self.subscription_set.count() > 0:
            last_subscription_end = self.subscription_set.all().aggregate(
                Max('end_date'))['end_date__max']
        return last_subscription_end

    def get_liaison_name(self):
        return ' '.join([self.contact_first_name or '',
                         self.contact_middle_name or '',
                         self.contact_last_name or '']).replace('  ', ' ')

    def get_liaison_email(self):
        return self.contact_email


class MigrationHistory(models.Model):
    institution = models.ForeignKey(Institution)
    date = models.DateTimeField(auto_now_add=True)
    source_ss = models.ForeignKey("submissions.SubmissionSet",
                                  related_name="migration_sources")
    target_ss = models.ForeignKey("submissions.SubmissionSet",
                                  related_name="migration_targets")

    def __unicode__(self):
        return "%s - %s (%s)" % (self.source_ss.creditset.version,
                                 self.target_ss.creditset.version,
                                 self.date)


RATINGS_PER_SUBSCRIPTION = 1
SUBSCRIPTION_DURATION = 365


class SubscriptionManager(models.Manager):
    """Filter archived Subscriptions."""

    def get_queryset(self):
        qs = super(SubscriptionManager, self).get_queryset()
        qs = qs.exclude(archived=True)
        return qs

    def include_archived(self):
        qs = super(SubscriptionManager, self).get_queryset()
        return qs

    def archived(self):
        qs = super(SubscriptionManager, self).get_queryset()
        qs = qs.exclude(archived=False)
        return qs


class Subscription(models.Model):
    """
    Describes a subscription to the reporting tool.
    """
    objects = SubscriptionManager()

    ms_id = models.CharField(max_length=64, blank=True, null=True)
    ms_institution = models.ForeignKey(MemberSuiteInstitution,
                                       blank=True,
                                       null=True)
    institution = models.ForeignKey(Institution,
                                    blank=True,
                                    null=True,
                                    on_delete=models.SET_NULL)
    name = models.CharField(max_length=512, blank=True, null=True)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)

    access_level = models.CharField(max_length=8,
                                    choices=(("Basic", "Basic"),
                                             ("Full", "Full")),
                                    default="Basic")

    ratings_allocated = models.SmallIntegerField(
        default=RATINGS_PER_SUBSCRIPTION)
    ratings_used = models.IntegerField(default=0)
    amount_due = models.FloatField(default=0)
    reason = models.CharField(max_length=16, blank=True, null=True)
    paid_in_full = models.BooleanField(default=False)
    late = models.BooleanField(default=False)

    archived = models.BooleanField(default=False, db_index=True)

    MEMBER_BASE_PRICE = 900
    NONMEMBER_BASE_PRICE = 1400

    PAY_LATER = 'later'
    PAY_NOW = 'now'

    BASIC_ACCESS = "Basic"  # Don't change this. It's the default access level.
    FULL_ACCESS = "Full"

    class Meta:
        ordering = ['-start_date']

    def get_available_ratings(self):
        return self.ratings_allocated - self.ratings_used

    def is_renewal(self):
        return 'renew' in self.reason

    def __unicode__(self):
        if self.ms_institution:
            return "%s (%s - %s)" % (self.ms_institution.org_name,
                                     self.start_date,
                                     self.end_date)
        else:
            return "No MS Institution (%s - %s)" % (
                self.start_date,
                self.end_date)


METHOD_CHOICES = (('credit', 'credit'),
                  ('check', 'check'))


class SubscriptionPayment(models.Model):
    """
    Payments are applied to subscriptions

    @todo: add a signal on save to update subscription.paid_in_full
    """
    subscription = models.ForeignKey(Subscription)
    date = models.DateTimeField()
    amount = models.FloatField()
    user = models.ForeignKey(User)
    method = models.CharField(max_length=8, choices=METHOD_CHOICES)
    confirmation = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return "%s: $%.2f (%s)" % (self.subscription.institution,
                                   self.amount, self.date)


class RegistrationReason(models.Model):
    """
        Possible reasons to register for STARS
    """
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title


class RegistrationSurvey(models.Model):
    """
        An optional survey for new registrants
    """
    institution = models.ForeignKey('Institution')
    user = models.ForeignKey(User)
    source = models.TextField("How did you hear about STARS?",
                              blank=True, null=True)
    reasons = models.ManyToManyField('RegistrationReason',
                                     blank=True)
    other = models.CharField(max_length=64, blank=True, null=True)
    primary_reason = models.ForeignKey('RegistrationReason',
                                       related_name='primary_surveys',
                                       blank=True, null=True)
    enhancements = models.TextField("Is there anything AASHE can do or "
                                    "provide to improve your experience "
                                    "using STARS (resources, trainings, "
                                    "etc.)?", blank=True, null=True)

    def __unicode__(self):
        return self.institution.__unicode__()


class RespondentRegistrationReason(models.Model):
    """
        Possible reasons to register for CSDC
    """
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title


class RespondentSurvey(models.Model):
    """
        An optional survey for new respondents
    """
    institution = models.ForeignKey('Institution')
    user = models.ForeignKey(User)
    source = models.TextField("How did you hear about the CSDC?",
                              blank=True, null=True)
    reasons = models.ManyToManyField('RespondentRegistrationReason',
                                     blank=True)
    other = models.CharField(max_length=64, blank=True, null=True)
    potential_stars = models.NullBooleanField("Is your institution "
                                              "considering registering as "
                                              "a STARS participant?",
                                              blank=True, null=True)

    def __unicode__(self):
        return self.institution.__unicode__()


class InstitutionPreferences(models.Model):
    """Tracks preferences and site-wide settings for an institution.

        Every preference should have default value, and code that
        access prefernces should simply create a new prefernce model
        if one does not exist for an institution yet.

        Preferences can be re-set to default simply by deleting the
        preference model for an institution.
    """
    institution = models.OneToOneField(Institution, primary_key=True,
                                       related_name='preferences',
                                       editable=False)
    notify_users = models.BooleanField(default=True)


STARS_USERLEVEL_CHOICES = settings.STARS_PERMISSIONS


class BaseAccount(models.Model):
    """
        A 'multi-table inheritance' base class - ensures all accounts
        have unique id's.  This is important because the different
        kinds of Accounts are mixed together in lists and so must have
        uniuqe id's between them so their id's uniquely identify them
        in the list.  Multi-table inheritance is a way of ensuring
        that each child class record has a unique id.
    """
    pass


class AbstractAccount(BaseAccount):
    """
        Abstract base class for StarsAccount and Pendingccount.

        Logically, this stuff could go in the BaseAccount class, but
        there are 2 reasons to use an Abstract base class here:

        1) so that the reverse relation, institution.starsaccount_set, works
        2) so that unique_together constraints can be handled by Django
    """
    institution = models.ForeignKey(Institution)
    terms_of_service = models.BooleanField(default=False)
    # user_level is a role
    user_level = models.CharField("Role", max_length=6,
                                  choices=STARS_USERLEVEL_CHOICES)

    class Meta:
        abstract = True

    def get_manage_url(self):
        return reverse('tool:manage:account-list',
                       kwargs={'institution_slug': self.institution.slug})

    def get_edit_url(self):
        return reverse('tool:manage:account-edit',
                       kwargs={'institution_slug': self.institution.slug,
                               'pk': self.id})

    def get_delete_url(self):
        return reverse('tool:manage:account-delete',
                       kwargs={'institution_slug': self.institution.slug,
                               'pk': self.id})

    def is_pending(self):
        return False

    def has_access_level(self, access_level):
        """
            Allows for access comparison on an institution that may
            not be their `current_institution`

            `settings.STARS_PERMISSIONS` is a tuple with the highest
            level coming first
        """

        # see if the user level matches
        if access_level == self.user_level:
            return True
        # see if the user has a higher level
        else:
            for perm in STARS_USERLEVEL_CHOICES:
                if perm[0] == access_level:
                    break
                if perm[0] == self.user_level:
                    return True

        return False

    def last_access(self):
        """
            Return the date of the last access to this account, or None
            Currently, this just uses the date of user's last login to STARS.
        """
        if self.is_pending():
            return None
        return self.user.last_login

    # Each action below corresponds to an e-mail template for a
    # notification message
    NEW_ACCOUNT = 'new_account.txt'
    CHANGE_ROLE = 'change_role.txt'
    DELETE_ACCOUNT = 'delete_account.txt'

    def get_formatted_message(self, action, admin, institution):
        """
            Format an e-mail message with the information from this entry
        """
        from django.template.loader import render_to_string
        template = "tool/manage/emails/%s" % action
        context = {'account': self, 'admin': admin, 'institution': institution}
        return render_to_string(template, context)

    def notify(self, action, admin, institution):
        """
            Notify account holder about an action taken on their
            account action must be one of the action constants defined
            by this class above
        """
        # et = EmailTemplate.objects.get(slug='invite_notification')

        send_mail('STARS Account notification for: %s' % self.user.email,
                  self.get_formatted_message(action, admin, institution),
                  settings.EMAIL_HOST_USER, [self.user.email],
                  fail_silently=True)


class StarsAccount(AbstractAccount):
    """This Model associates users with institutions at different access
       levels

       Although the institutions field is d, clients should not assume
       it is always non-None (see DuckAccount below)

       Accounts serve permissions for users on institutuions -

          - PRIVATE: user_level should generally be treated as private

          - BEST PRACTICES: use request.user.has_perm( perm ) to check
            access rights!
    """
    user = models.ForeignKey(User)

    # is_selected is True if the user has this account selected - we
    # need this so we can persist the user's account on logout.
    is_selected = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "institution")

    def __unicode__(self):
        return "%s" % self.user.email

    def select(self):
        """Make this account the user's active account, and so de-select all
           of user's other accounts.
        """
        if not self.is_selected:
            for account in self.user.starsaccount_set.filter(is_selected=True):
                account.deselect()
            self.is_selected = True
            self.save()

    def deselect(self):
        """
            De-select this account, and persist the change.
        """
        self.is_selected = False
        self.save()

    @staticmethod
    def get_selected_account(user):
        """
            Return the account the given user currently has selected, or None
            Ideally, this method would be part of the user object... but...
        """
        account = user.starsaccount_set.filter(is_selected=True)
        # there should only be one account selected at a time:
        return account[0] if account else None

    def has_perm(self, perm):
        """
            Return True if this account grants user the given permission.
            CAREFUL: only checks permission - does not do complete access
            rights check.
            Clients should call request.user.has_perm(perm) to verify user
            access rights within current request context.
            - perm: One of settings.STARS_PERMISSIONS
        """
        return _has_perm(self, perm)


def _has_perm(account, perm):
    """ Helper so that StarsAccount and DuckAccount can share logic """
    # anyone with an account can view, admin users can submit,
    # otherwise permissions and roles are synonymous
    return (perm == 'view' or
            (perm == 'submit' and account.user_level == 'admin') or
            perm == account.user_level)


class PendingAccount(AbstractAccount):
    """ Represents a StarsAccount for a 'user' without an IRC account.

        Since there is no way to create a User object for them, they
        can't have an StarsAccount, so we create a PendingAccount and
        convert it to a StarsAccount on their first login.

        All the logic around PendingAccounts assumes:
          - PendingAccounts are only ever created for users without AASHE
            accounts
          - the first time the user logs in to STARS, all PendingAccounts
            are converted to StarsAccounts
    """
    user_email = models.EmailField()

    class Meta:
        unique_together = ("user_email", "institution")

    def __unicode__(self):
        return "%s" % self.user_email

    def is_pending(self):
        return True

    def _get_user(self):
        """
            Clients want to treat self as if it were a StarsAccount,
            which has a User field.
            so we need to fulfill calls to account.user.x
            So, we create a DuckUser, which (hopefully) supplies all
            the methods clients will call on!
        """
        return DuckUser(self.user_email)
    user = property(_get_user, )

    @staticmethod
    def convert_accounts(user):
        """
            Convert to StarsAccounts any accounts pending for the given user.
            If any accounts are converted, one is selected and returned,
            otherwise, if the user has no pending accounts, returns None.
        """
        pending_accounts = PendingAccount.objects.filter(
            user_email__iexact=user.email)
        account = None
        # seems unlikely there will be more than 1, but it could happen...
        for pending in pending_accounts:
            # Confirm the account doesn't already exist
            try:
                account = StarsAccount.objects.get(
                    user__email=pending.user_email,
                    institution=pending.institution)
                account.user_level = pending.user_level
            except StarsAccount.DoesNotExist:
                account = StarsAccount(user=user,
                                       institution=pending.institution,
                                       user_level=pending.user_level)

            account.save()
            pending.delete()

        if account:  # selected account will be the last account converted
            account.select()
        return account


class DuckUser(object):
    """
        If it waddles like a User, and quacks like a User...
        Except:
            - DuckUsers have no persistence, no DB backend, and no queries.
            - DuckUsers have a very limited set of capabilities - just
              enough to satisfy our current needs.
        Why?
            - to satisfy the needs of PendingAccount
     """

    def __init__(self, user_email):
        self.email = user_email

    def __str__(self):
        return "%s" % self.email

    def get_full_name(self):
        return self.__str__()


class DuckAccount(object):
    """If it walks like a StarsAccount, and quacks like a StarsAccount...
        Except:
            - DuckAccounts have no persistence, no DB backend, and no queries.
            - by default DuckAccounts have no permssions - they must be
              set explicitly
            - institution may be None.  CAREFUL - potential issues -
              clients of StarsAccount should not make that assumption!
        Why?
            - testing: useful to be able to create mock user accounts
              on the fly
            - staff:  don't have accounts, which may lead to special
              case logic.
            - reduced duplication: current_inst is currently duplicated
              in user and user.account - there may be other such cases
              in future

        This is not being used right now - it was just an idea I was
        toying with... may be useful in future.
    """

    def __init__(self, user, institution=None, user_level=None):
        self.user = user
        self.institution = institution
        self.user_level = user_level

    def __str__(self):
        return "%s (quack)" % self.user

    def has_perm(self, perm):
        return _has_perm(self, perm)


class AccountInvite(models.Model):
    """
        When an institution admin invites a user to join
    """
    pass
