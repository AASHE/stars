import collections
from datetime import date, timedelta
from logging import getLogger

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import PhoneNumberField
from django.template.defaultfilters import slugify
from django.db.models import Max
from django.core.mail import send_mail
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from stars.apps.credits.models import Category, CreditSet
from stars.apps.registration.models import get_current_discount
from stars.apps.notifications.models import EmailTemplate

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


BASIC_ACCESS = "basic"
FULL_ACCESS = "full"


class Institution(models.Model):
    """
        This model represents a STARS institution. The institution name
        is a mirror of Salesforce and will require regular updating
    """
    objects = InstitutionManager()
    slug = models.SlugField(max_length=255)
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
    contact_title = models.CharField("Liaison Title", max_length=255)
    contact_department = models.CharField("Liaison Department", max_length=64)
    contact_phone = PhoneNumberField("Liaison Phone")
    contact_phone_ext = models.SmallIntegerField("Extension",
                                                 blank=True,
                                                 null=True)
    contact_email = models.EmailField("Liaison Email")
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

    charter_participant = models.BooleanField()
    stars_staff_notes = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True,
                                        blank=True,
                                        null=True,
                                        db_index=True)
    international = models.BooleanField(default=False)

    # ISS properties
    name = models.CharField(max_length=255)
    aashe_id = models.IntegerField(unique=True, blank=True, null=True)
    org_type = models.CharField(max_length=32, blank=True, null=True)
    fte = models.IntegerField(blank=True, null=True)
    is_pcc_signatory = models.NullBooleanField(default=False)
    is_member = models.NullBooleanField(default=False)
    is_pilot_participant = models.NullBooleanField(default=False)
    country = models.CharField(max_length=128, blank=True, null=True)

    # State properties
    is_participant = models.BooleanField(
        default=False,
        help_text=("An institution that isn't a participant is simply "
                   "considered a Survey Respondent"))
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

    def __unicode__(self):
        return self.name

    @classmethod
    def get_org_types(cls):
        institutions = cls.objects.values('org_type').distinct()
        org_types = []
        for institution in institutions:
            if institution['org_type']:
                org_types.append(institution['org_type'])
        return org_types

    @property
    def access_level(self):
        """Shadows is_participant, now that we don't have participants
        and respondents, but institutions with full or basic access."""
        if self.is_participant:
            return FULL_ACCESS
        else:
            return BASIC_ACCESS

    @access_level.setter
    def access_level(self, level):
        if level not in [BASIC_ACCESS, FULL_ACCESS]:
            raise InvalidAccessLevelError(level)
        self.is_participant = (level == FULL_ACCESS)

    def update_status(self):
        """
            Update the status of this institution, based on subscriptions and
            submissions

            NOTE: does not save the institution
        """
        # Update current_rating
        if self.rating_expires and self.rating_expires <= date.today():
            # if the rated submission has expired remove the rating
            self.rated_submission = None
            self.current_rating = None
            self.rating_expires = None

            # @todo should i add an automated email here or put it
            # in notifications?

        # Check subscription is current
        if self.current_subscription:
            if (self.current_subscription.start_date <= date.today() and
                self.current_subscription.end_date >= date.today()):
                self.is_participant = True
            else:
                self.is_participant = False
                self.current_subscription = None
                # if it has expired, check and see if there is another
                # that is current
                for sub in self.subscription_set.all():
                    if (sub.start_date <= date.today() and
                        sub.end_date >= date.today()):
                        self.is_participant = True
                        self.current_subscription = sub
                        break
        else:
            self.is_participant = False

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
                          FieldMapping(stars_field="org_type",
                                       iss_field="carnegie_class",
                                       decode=True),
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

        def get_institutional_boundary_credit(creditset):
            category = Category.objects.filter(creditset=creditset).get(
                title='Institutional Characteristics')
            subcategory = category.subcategory_set.get(
                title='Institutional Characteristics')
            ib_credit = subcategory.credit_set.get(
                title='Institutional Boundary')
            return ib_credit

        def get_org_type(self, carnegie_class):
            """Get org type, based on Salesforce Carnegie Classifications
            for pre 2.0 submissions, and the submission's Institutional
            Characteristics for 2.0+ submissions.
            """
            # Import way down here to avoid circular dependency:
            from stars.apps.submissions.models import CreditUserSubmission

            submission = self.get_latest_rated_submission()

            # No rated submission?  Or rated submission a pre-2.0 creditset?
            # Then check the most recently created submission.  That's the
            # one that's being worked on.  Right?
            if not submission or submission.creditset.version < '2':
                try:
                    submission = self.submissionset_set.filter(
                        institution=self).order_by(
                            '-date_submitted').order_by(
                                '-date_created')[0]
                except IndexError:
                    pass

            if (submission and submission.creditset.version >= '2'):

                # Get IB credit for this submission.
                ib_credit = get_institutional_boundary_credit(
                    creditset=submission.creditset)

                cus = CreditUserSubmission.objects.filter(
                    credit=ib_credit).get(
                        subcategory_submission__category_submission__submissionset=submission)

                try:
                    sf = [sf for sf in cus.get_submission_fields()
                          if sf.documentation_field.title.lower() ==
                          'institution type'][0]
                except IndexError:  # No institution type submission field.
                    return carnegie_class

                if sf.get_human_value():
                    return sf.get_human_value()

            return carnegie_class

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

            # handle org-type specially:
            self.org_type = get_org_type(self,
                                         carnegie_class=getattr(
                                             iss_org, 'carnegie_class'))
        else:
            logger.warning("No ISS institution found %s" % (self.name))

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
        if self.profile:
            location = self.profile.city
            for field in (self.profile.state, self.profile.country_iso):
                if location and field:
                    location += ', '
                location += field
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
                status='r').order_by('date_submitted')[0]

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
        from issdjango.models import Organizations
        try:
            org = Organizations.objects.get(account_num=self.aashe_id)
            return org
        except Organizations.DoesNotExist:
            logger.info("No ISS institution found for aashe_id %s" %
                        self.aashe_id)
        except Organizations.MultipleObjectsReturned:
            logger.warning("Multiple ISS Institutions for aashe_id %s" %
                           self.aashe_id)
        return None

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
            slug_base = '%s-%s' % (self.profile.org_name,
                                   self.profile.state.lower())
            self.slug = slugify(slug_base)
        except Exception, e:
            logger.error("ISS Institution profile relationship error: %s" % e,
                         exc_info=True)
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
        return ' '.join([self.contact_first_name,
                         self.contact_middle_name,
                         self.contact_last_name]).replace('  ', ' ')

    def get_liaison_phone(self):
        phone = self.contact_phone
        if self.contact_phone_ext:
            if phone:
                phone += ' x' + str(self.contact_phone_ext)
            else:
                phone = 'x' + str(self.contact_phone_ext)
        return phone

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


class Subscription(models.Model):
    """
    Describes a subscription to the reporting tool.
    """
    institution = models.ForeignKey(Institution)
    start_date = models.DateField()
    end_date = models.DateField()
    ratings_allocated = models.SmallIntegerField(
        default=RATINGS_PER_SUBSCRIPTION)
    ratings_used = models.IntegerField(default=0)
    amount_due = models.FloatField()
    reason = models.CharField(max_length='16', blank=True, null=True)
    paid_in_full = models.BooleanField(default=False)
    late = models.BooleanField(default=False)

    MEMBER_BASE_PRICE = 900
    NONMEMBER_BASE_PRICE = 1400

    PAY_LATER = 'later'
    PAY_NOW = 'now'

    class Meta:
        ordering = ['-start_date']

    @classmethod
    def create(cls, institution, *args, **kwargs):
        """
            Creates a new Subscription. The Subscription's reason,
            start_date, and end_date are calculated.

            Returns a tuple of the Subscription created, and a boolean
            indicating if a promo discount was applied when the amount
            due was ciphered.

            Note that the Subscription created has *not* been save()'d.

            Doing this via a static factory method rather than in
            __init__, because tweaking __init__ on a Model causes
            weird things to happen.

            Will propagate any errors raised if an invalid or
            expired promo_code is provided.
        """
        # promo_code is a kwarg we need to pop off kwargs before passing it
        # to Subscription():
        try:
            promo_code = kwargs.pop('promo_code')
        except KeyError:
            promo_code = False

        subscription = cls(institution=institution, *args, **kwargs)

        subscription.reason = subscription._calculate_reason()

        (subscription.start_date,
         subscription.end_date) = subscription._calculate_date_range()

        prices = subscription.calculate_prices(promo_code=promo_code)

        subscription.amount_due = prices['total']

        return subscription

    @classmethod
    def get_date_range_for_new_subscription(cls, institution):
        """
           Provides the start and end dates for a new subscription
           for an institution, without actually creating the subscription.
           This allows one to, for example, show a user what the dates
           will be before getting confirmation from them that they want
           to buy the subscription.
        """
        subscription = cls.create(institution=institution)
        date_range = (subscription.start_date, subscription.end_date)
        # deleting the subscription here for what the hell maybe
        # garbage-collection reasons, maybe just because it feels
        # better; it hasn't been saved to the db yet . . .
        assert subscription.id is None
        # . . . so just deleting the reference should . . . oh hell,
        # I don't know, it just seems explicit and right
        del subscription

        return date_range

    @classmethod
    def get_prices_for_new_subscription(cls, institution, promo_code=False):
        """
           Provides the price for a new subscription for an institution,
           without actually creating the subscription.  This allows
           one to, for example, show a user what the price will be
           before getting confirmation from them that they want to buy
           the subscription.

           Returns a dictionary containing the price, the
           amount discounted for a promo code, and the amount
           discounted by applying the early renewal discount.
        """
        subscription = cls.create(institution=institution,
                                  promo_code=promo_code)
        prices = subscription.calculate_prices(promo_code=promo_code)
        # deleting the subscription here for what the hell maybe
        # garbage-collection reasons, maybe just because it feels
        # better; it hasn't been saved to the db yet . . .
        assert subscription.id is None
        # . . . so just deleting the reference should . . . oh hell,
        # I don't know, it just seems explicit and right
        del subscription

        return prices

    @classmethod
    def purchase(cls, institution, pay_when, user,
                 promo_code=None, card_num=None, exp_date=None,
                 cvv=None):
        """
           Encapsulates the purchase process.

               1. If paying now, a credit card charge is made.
               2. Post-purchase email is sent.
               3. The institution related to this subscription is updated.

           Returns the subscription purchased.

             institution: institution that's purchasing the subscription

             pay_when: either self.PAY_NOW or self.PAY_LATER

             user: user making the payment

             promo_code: discount code

             card_num: credit card number as string

             exp_date: credit card expiration date as string, "MMYYYY"

             cvv: security code as a string

           Raises a SubscriptionPurchaseError if there's a problem
           charging a credit card.

           card_num, exp_date and cvv are required if pay_when == self.PAY_NOW.
        """
        # See pitiful comment in pay() for why import from credit_card
        # happens here, rather in the top level.
        from stars.apps.payments.simple_credit_card import (
            CreditCardProcessingError)

        subscription = cls.create(institution=institution,
                                  promo_code=promo_code)

        subscription.save()

        if pay_when == cls.PAY_NOW:
            try:
                subscription_payment = subscription.pay(
                    user=user,
                    amount=subscription.amount_due,
                    card_num=card_num,
                    exp_date=exp_date,
                    cvv=cvv)
            except CreditCardProcessingError as ccpe:
                subscription.delete()
                raise SubscriptionPurchaseError(str(ccpe))
        else:  # pay_when == self.PAY_LATER:
            # Update self.paid_in_full in the special case
            # where the subscription is free:
            if subscription.amount_due == 0.00:
                subscription.paid_in_full = True
                subscription.save()
            subscription_payment = None

        subscription._send_post_purchase_email(
            pay_when=pay_when,
            additional_email_address=user.email,
            subscription_payment=subscription_payment)

        subscription._update_institution_after_purchase()

        return subscription

    def calculate_prices(self, promo_code=None):
        """
            Calculates the prices for this subscription.

            Returns a dictionary containing the price, and the
            constituent elements used to arrive at the price;
            the base price, amount discounted for a promo code,
            and the amount discounted by applying the early
            renewal discount.

            If the promo_code is invalid or expired, an exception
            from registration.models.get_current_discount() will
            arise; it's not caught here, so beware.
        """
        base_price = self.NONMEMBER_BASE_PRICE

        running_total = base_price

        if self.institution.is_member:
            member_discount = (self.NONMEMBER_BASE_PRICE -
                               self.MEMBER_BASE_PRICE)
            running_total -= member_discount
        else:
            member_discount = 0

        gets_early_renewal_discount = (
            self.qualifies_for_early_renewal_discount())

        if gets_early_renewal_discount:
            pre_discount_price = running_total
            running_total = self._apply_early_renewal_discount(running_total)
            early_renewal_discount = pre_discount_price - running_total
        else:
            early_renewal_discount = 0

        if promo_code:
            pre_promo_price = running_total
            running_total = self._apply_promo_code(running_total, promo_code)
            promo_discount = pre_promo_price - running_total
        else:
            promo_discount = 0

        return {'total': running_total,
                'base_price': base_price,
                'member_discount': member_discount,
                'promo_discount': promo_discount,
                'early_renewal_discount': early_renewal_discount}

    def get_available_ratings(self):
        return self.ratings_allocated - self.ratings_used

    def is_renewal(self):
        return 'renew' in self.reason

    def pay(self, user, amount, card_num, exp_date, cvv):
        """
            Make a payment on this subscription.

                user: user making the payment

                amount: dollar amount to apply

                card_num: credit card number as string

                exp_date: credit card expiration date as string, "MMYYYY"

            Returns the SubscriptionPayment created.

            Any CreditCardProcessingError raised when charging a credit
            card will be propagated.
        """
        # Importing credit_card way down here to avoid some weird import
        # side-effects that I'm just too tired to track down right now.
        # After importing this in the top level of this module,
        # Institution.get_latest fails, because within get_latest(),
        # Institution is None.  Importing here, within pay(), doesn't
        # cause that unpleasant side-effect.
        import stars.apps.payments.simple_credit_card as credit_card

        ccpp = credit_card.CreditCardPaymentProcessor()
        subscription_payment = ccpp.process_subscription_payment(
            subscription=self,
            user=user,
            amount=amount,
            card_num=card_num,
            exp_date=exp_date,
            cvv=cvv)

        self.amount_due -= amount

        self.paid_in_full = self.amount_due == 0.00

        self.save()

        # Tack last 4 digits from credit card onto subscription payment,
        # so they're available in the post payment email template.  Note
        # the digits aren't saved to the database, and they'll be forgotten
        # when this subscription_payment object gets garbage collected.
        subscription_payment.last_four = card_num[-4:]

        return subscription_payment

    def __unicode__(self):
        return "%s (%s - %s)" % (self.institution.name,
                                 self.start_date,
                                 self.end_date)

    def _apply_promo_code(self, price, promo_code=None):
        """
            Returns price, after applying any promotional discount
            tied to promo_code.

            Any exceptions raised in get_current_discount() are
            propagated.
        """
        if promo_code:
            discount = get_current_discount(code=promo_code)
            if discount:
                price = discount.apply(price)

        return price

    def _apply_early_renewal_discount(self, price):
        """
           Apply the early renewal discount to a subscription price.

           This is a simple calculation, broken out into its own
           method to encapsulate it.  So, for instance, test code
           doesn't need to know the calculation to check pricing.
        """
        return price / 2

    def _calculate_date_range(self):
        """
            Calculates the start and end dates for a new subscription.
            Returns a tuple of start_date and end_date.
        """
        start_date = self._calculate_start_date()
        end_date = start_date + timedelta(days=SUBSCRIPTION_DURATION)
        return (start_date, end_date)

    def _calculate_reason(self):
        """
            Calculates the reason for a new subscription.
            It's a renewal or (initial) registration, for a member or
            a nonmember.
        """
        institution_type = ('member'
                            if self.institution.is_member_institution()
                            else 'nonmember')
        subscription_type = ('renew'
                             if self.institution.subscription_set.count()
                             else 'reg')
        return '_'.join([institution_type, subscription_type])

    def _calculate_start_date(self):
        """
            Calculates the start date for a new subscription, taking into
            account any current subscription.
        """
        start_date = self._get_latest_subscription_end()
        if start_date and start_date >= date.today():
            start_date += timedelta(days=1)
        else:
            start_date = date.today()
        return start_date

    def _get_latest_subscription(self):
        """
           Returns the latest subscription for this institution, ordered
           by end_date.
        """
        subscriptions = Subscription.objects.filter(
            institution=self.institution).order_by('-end_date')
        if hasattr(self, 'id'):  # this might not be saved yet, so no id.
            subscriptions = subscriptions.exclude(id=self.id)
        try:
            return subscriptions[0]
        except IndexError:
            return None

    def _get_latest_subscription_end(self):
        """
           Returns the end date of the latest subscription for this
           institution.
        """
        latest_subscription = self._get_latest_subscription()
        if latest_subscription:
            return latest_subscription.end_date
        else:
            return None

    def _send_email(self, slug, mail_to, context):
        et = EmailTemplate.objects.get(slug=slug)
        et.send_email(mail_to, context)

    def _send_post_purchase_email(self, pay_when,
                                  additional_email_address=None,
                                  subscription_payment=None):
        mail_to = [self.institution.contact_email]

        if (additional_email_address and
            additional_email_address != self.institution.contact_email):
            mail_to.append(additional_email_address)

        if pay_when == self.PAY_LATER:
            self._send_post_purchase_pay_later_email(mail_to=mail_to)
        else:  # pay_when == self.PAY_NOW:
            self._send_post_purchase_pay_now_email(
                mail_to=mail_to,
                subscription_payment=subscription_payment)

    def _send_post_purchase_executive_renewal_email(self):
        if self.institution.executive_contact_email:
            exec_mail_to = [self.institution.executive_contact_email]
            exec_slug = 'reg_renewal_exec'
            exec_email_context = {'institution': self.institution}
            self._send_email(slug=exec_slug, mail_to=exec_mail_to,
                             context=exec_email_context)

    def _send_post_purchase_welcome_executive_email(self):
        if self.institution.executive_contact_email:
            exec_mail_to = [self.institution.executive_contact_email]
            exec_slug = 'welcome_exec'
            exec_email_context = {'institution': self.institution}
            self._send_email(slug=exec_slug, mail_to=exec_mail_to,
                             context=exec_email_context)

    def _send_post_purchase_pay_later_email(self, mail_to):
        if self.is_renewal():
            slug = "reg_renewal_unpaid"
        else:
            slug = "welcome_liaison_unpaid"
            self._send_post_purchase_welcome_executive_email()
        email_context = {'price': self.amount_due}
        self._send_email(slug=slug, mail_to=mail_to, context=email_context)

    def _send_post_purchase_pay_now_email(self, mail_to, subscription_payment):
        if self.is_renewal():
            slug = 'reg_renewed_paid'
            self._send_post_purchase_executive_renewal_email()
        else:
            slug = 'welcome_liaison_paid'
            self._send_post_purchase_welcome_executive_email()
        email_context = {'institution': self.institution,
                         'payment': subscription_payment}
        self._send_email(slug=slug, mail_to=mail_to, context=email_context)

    def qualifies_for_early_renewal_discount(self):
        """
            Returns True if this subscription's institution should get
            a discount for renewing early-ish.

            Institutions get half-off their submission if they
            renew before their current subscription ends, or within
            90 days after their previous subscription ended.
        """
        previous_subscription_end = self._get_latest_subscription_end()

        if previous_subscription_end:

            # if last subscription end was less than 90 days ago
            # or it hasn't expired
            td = timedelta(days=90)
            return date.today() <= previous_subscription_end + td

        return False

    def _update_institution_after_purchase(self):
        """
            Updates the subscription-related attributes of this
            subscription's institution.
        """
        self.institution.current_subscription = (
            self.institution.current_subscription or self)
        self.institution.is_participant = True
        self.institution.save()


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
    method = models.CharField(max_length='8', choices=METHOD_CHOICES)
    confirmation = models.CharField(max_length='16', blank=True, null=True)

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
                                     blank=True, null=True)
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
                                     blank=True, null=True)
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
    terms_of_service = models.BooleanField()
    # user_level is a role
    user_level = models.CharField("Role", max_length='6',
                                  choices=STARS_USERLEVEL_CHOICES)

    class Meta:
        abstract = True

    def get_manage_url(self):
        return reverse('account-list',
                       kwargs={'institution_slug': self.institution.slug})

    def get_edit_url(self):
        return reverse('account-edit',
                       kwargs={'institution_slug': self.institution.slug,
                               'pk': self.id})

    def get_delete_url(self):
        return reverse('account-delete',
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
        # HACK alert - Django stores a default of now() in last_login
        #              field when account is created.
        #            - as a result, last_login < date_joined when user
        #              hasn't logged in yet.
        #  - seems a bit fragile, but that's really the only way I can
        #    think of to determine if user has not logged in yet...

        if self.is_pending():
            return None
        last_login = self.user.last_login.replace(microsecond=0)
        date_joined = self.user.date_joined.replace(microsecond=0)
        return (None if (self.user.last_login < self.user.date_joined) else
                self.user.last_login)

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

    @classmethod
    def update_account(cls, admin, notify_user, institution, user_level,
                       **user_params):
        """
            Create or update an account

            admin is the user who is doing the update - used for
            notifying user of account change.

            user_params are passed through to cls to uniquely identify
            or create account.

            returns the updated or newly created account.
        """
        has_changed = True
        is_create = False
        try:
            # See if there is already a  Account for this user
            account = cls.objects.get(institution=institution, **user_params)
            if account.user_level != user_level:
                account.user_level = user_level
            else:
                has_changed = False
        except cls.DoesNotExist:
            # Or create one
            account = cls(institution=institution, user_level=user_level,
                          **user_params)
            is_create = True
        account.save()

        # Notify the user only if something actually changes AND admin
        # wanted to notify them.
        if has_changed and notify_user:
            action = (StarsAccount.NEW_ACCOUNT if is_create else
                      StarsAccount.CHANGE_ROLE)
            account.notify(action, admin, institution)

        return account


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
