import ast
import math
import re
from datetime import date
from logging import getLogger

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db import transaction
from django.db.models.signals import post_init
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_unicode
from jsonfield import JSONField
from sorl.thumbnail import ImageField

from stars.apps.credits.utils import get_next_variable_name
from mixins import VersionedModel
from utils import get_array_for_tabular_fields

RATING_DURATION = 365 * 3
DUMMY_UNIT_LABEL = ""

logger = getLogger("stars")


# from pagedown.widgets import AdminPagedownWidget


class IncrementalFeature(models.Model):
    key = models.SlugField(unique=True)
    description = models.TextField()

    # formfield_overrides = {
    #     models.TextField: {'widget': AdminPagedownWidget}
    # }

    def __unicode__(self):
        return self.key


class CreditSetManager(models.Manager):
    def get_latest(self):
        """
            Returns the latest creditset (usually the one currently open for
            registration)
        """
        try:
            return (
                super(CreditSetManager, self)
                .get_queryset()
                .filter(release_date__lte=date.today())
                .order_by("-release_date")[0]
            )
        except:
            return None


def _get_next_ordinal(objects):
    """
        Helper: Retrieve the next ordinal in sequence for the given queryset
        identifying an ordered set of objects.

        This could be subject to a concurrency issue if two objects are
        saved simultaneously!

        Ideally, Django would allow us to simply use an auto-incrementing
        field for this... :-P

        # doctest
        >>> from django.core import management
        >>> management.call_command("flush", verbosity=0, interactive=False)
        >>> cs = CreditSet.objects.create(release_date="2010-01-01", tier_2_points=0.25)
        >>> cat = Category.objects.create(creditset=cs, title="Cat 1", abbreviation='Test', max_point_value=1, description="this is a test")
        >>> Category.objects.get(pk=1).ordinal
        0
        >>> cat = Category.objects.create(creditset=cs, title="Cat 2", abbreviation='Test', max_point_value=1, description="this is a test")
        >>> Category.objects.get(pk=2).ordinal
        1
        >>> _get_next_ordinal(cat.creditset.category_set.all())
        2
        >>> _get_next_ordinal(cat.subcategory_set.all())
        0
    """
    ordinal = 0
    list = objects.order_by("-ordinal")
    if list.count() > 0:
        last = list[0]
        ordinal = last.ordinal + 1
    return ordinal


# These choices are the names of scoring methods in the SubmissionSet
# model used to score a credit set.
# Method names stored in the DB have a maximum length of 25 characters
SCORING_METHOD_CHOICES = (
    ("get_STARS_v1_0_score", "STARS 1.0 Scoring"),
    ("get_STARS_v2_0_score", "STARS 2.0 Scoring"),
)

IDENTIFIER_CHOICES = (("get_1_0_identifier", "1.0"), ("get_1_1_identifier", "1.1"))


class CreditSet(VersionedModel):
    version = models.CharField(max_length=5, unique=True)
    release_date = models.DateField()
    tier_2_points = models.FloatField()
    is_locked = models.BooleanField(
        default=False,
        verbose_name="Lock Credits",
        help_text="When a credit set is locked, most credit editor "
        "functions will be disabled.",
    )
    scoring_method = models.CharField(max_length=25, choices=SCORING_METHOD_CHOICES)
    credit_identifier = models.CharField(
        max_length=25, choices=IDENTIFIER_CHOICES, default="get_1_1_identifier"
    )
    supported_features = models.ManyToManyField(IncrementalFeature)
    objects = CreditSetManager()

    class Meta:
        ordering = ("release_date",)

    def __init__(self, *args, **kwargs):
        super(CreditSet, self).__init__(*args, **kwargs)
        self._unlock_confirmed = False
        self._confirm_unlock_attempt = False
        # not required until an attempt to unlock is actually made

    def __unicode__(self):
        return "v%s" % self.version

    def __getattr__(self, item):
        """
            overriding this to have a has_*_feature property that test
            supported features
        """
        pattern = "has_(.*)_feature"
        m = re.match(pattern, item)
        if m:
            return self.has_feature(m.groups()[0])

        return super(CreditSet, self).__getattribute__(item)

    def has_feature(self, feature_key):
        if self.supported_features.filter(key=feature_key):
            return True
        return False

    def get_edit_url(self):
        return "/tool/credit-editor/%d/" % self.id

    def get_submit_url(self, submissionset):
        # Here's a hack -- now that institution.slug is integrated
        # into our URLs, models in this credits app need to know what
        # institution we're dealing with, to divine the correct URLs.
        # Because the URLs from the models in the credits app are used
        # for models in the submissions app -- and there is a direct
        # connection between submissions models and institutions, so
        # wah.  Setting the default value of `institution_slug` to
        # None just for what the heck maybe this gets called from
        # other places (like a credit editor? that would make sense,
        # and imply no institution) and though I can't imagine how it
        # would work w/o an institution_slug, my imagination is
        # constrained by caffeine, l-theanine, modafinil, and a
        # relative lack of sleep. Yay for focus!
        #
        # Right, focus. Same thing for submissionset_id as institution_slug
        # blabbed about above.
        #
        # Why not provide links to the models in the submissions app that
        # correspond to those in apps.credits.models, rather than links to
        # the credits models?
        if submissionset:
            return reverse(
                "tool:my_submission:submission-summary",
                kwargs={
                    "institution_slug": submissionset.institution.slug,
                    "submissionset": submissionset.id,
                },
            )
        else:
            return "/tool/submissions/"

    def get_report_url(self, submissionset):
        """ This is a bit convoluted - really we want the report URL for the
            submission objects, but when building the credit_outline menu,
            we only have the credit objects.

            My 'hack' was to have the credit object build out the url,
            but have the submissionset provide the base url.
        """
        return submissionset.get_report_url()

    def get_unlock_url(self):
        return "%sconfirm-unlock/" % self.get_edit_url()

    def get_locked_url(self):
        return "%slocked/" % self.get_edit_url()

    def get_parent(self):
        """ Returns the parent element for crumbs """
        return None

    def get_children(self):
        """ Returns a queryset with child credit model objects - for hierarchy
        """
        return self.category_set.all()

    def get_rating(self, score):
        """ Returns a rating for this creditset for the given total score """
        for rating in self.rating_set.all():  # sorted in descending
            # value by score
            if score >= rating.minimal_score:
                return rating
        # oh-oh - we didn't find any suitable rating.
        logger.warning(
            "No valid rating could be found for score "
            "%s in creditset %s" % (score, self)
        )
        return Rating(name="Rating Unavailable", minimal_score=0, creditset=self)

    def get_version_identifier(self):
        """ Returns this credit set version name as a legal Python identifier
        """
        import re

        name = self.version
        if not name[0].isalpha():  # ensure first character is alpha
            name = "v%s" % name
        # replace punctuation with underscores:
        name = re.sub(r'[\-\'\.,?/;:"~!@#$%^&*()+]', "_", name)
        return name

    def num_normal_categories(self):
        """ Returns the number of non-innovation categories in this set """
        return self.category_set.exclude(abbreviation="IN").count()

    def num_submissions(self):
        """ Return the number of credit submissions started for this category
        """
        from stars.apps.submissions.models import get_active_submissions

        return get_active_submissions(creditset=self).count()

    def unlock(self):
        """ Clients must use this method to perform a confirmed unlock. """
        self.is_locked = False
        self._unlock_confirmed = True
        self.save()

    def unlock_attempt_requires_confirmation(self):
        """
            Returns True if a failed attempt was made to unlock this
            creditset without using unlock(), False otherwise
        """
        return self.is_locked and self._confirm_unlock_attempt

    def save(self, *args, **kwargs):
        """ Enforce unlock protocol and Log changes to the credit set
            lock status """
        try:
            pre_save = CreditSet.objects.get(pk=self.pk)
            lock_changed = pre_save.is_locked != self.is_locked

            # Unconfirmed lock attempt: determine if confirmation is
            # required and reset lock if so.
            if lock_changed and not self.is_locked and not self._unlock_confirmed:
                self._confirm_unlock_attempt = (
                    self.is_released() and self.num_submissions() > 0
                )
                if self._confirm_unlock_attempt:
                    self.is_locked = pre_save.is_locked
                    lock_changed = False
            else:
                self._confirm_unlock_attempt = False

            # Log any significant changes to the lock
            if lock_changed and self.is_released():
                lock_status = "LOCKED" if self.is_locked else "UN-LOCKED"
                logger.info("Released Credit Set %s was %s" % (self, lock_status))
        except ObjectDoesNotExist:
            pass  # saving a new credit set - locks don't apply - carry on.

        super(CreditSet, self).save(*args, **kwargs)

    def is_released(self):
        """ Returns True if the current date is past the credit set release
            date """
        from datetime import date

        return self.release_date and (self.release_date <= date.today())

    def get_pulldown_credit_choices(self, level=1, first="----"):
        """
            Provide the choices for a pulldown menu of all the credits in the
            creditset using categories and subcategories for navigation

            The level indicates how far up the links go. Level one will
            only include ids for credits, but level 3 will include ids
            for credits, subcategories and categories.
        """
        choices = [("", first)]

        for category in self.category_set.all():
            id = category.id
            if level < 3:
                id = "-1"
            choices.append((id, category.title.upper()))

            for subcategory in category.subcategory_set.all():
                id = subcategory.id
                if level < 2:
                    id = "-1"
                choices.append(("-1", " "))
                choices.append((id, "%s" % subcategory.title))
                choices.append(("-1", "=" * 14))

                for credit in subcategory.get_tier1_credits():
                    choices.append(
                        (credit.id, "%s: %s" % (credit.get_identifier(), credit.title))
                    )
                t2 = subcategory.get_tier2_credits()
                if t2:
                    choices.append(("-1", "-" * 10))
                    for credit in t2:
                        choices.append(
                            (
                                credit.id,
                                "%s: %s" % (credit.get_identifier(), credit.title),
                            )
                        )
            choices.append(("-1", " "))
        return choices

    def get_credits(self):
        """Returns all the credits for this Credit Set."""
        categories = Category.objects.filter(creditset=self)
        subcategories = Subcategory.objects.filter(category__in=categories)
        return Credit.objects.filter(subcategory__in=subcategories)

    def has_subcategory_description_feature(self):
        """ Checks if the creditset should have subcat descriptions """
        return self.has_feature("subcategory_description")

    def has_president_letter_feature(self):
        """ Checks if the creditset should have president letter during submission """
        return self.has_feature("pres_letter_in_submission_process")


class Rating(models.Model):
    """
        The official stars ratings: Platinum, Gold, Silver, Bronze, Reporter
    """

    name = models.CharField(max_length=16)
    minimal_score = models.SmallIntegerField(
        help_text="The minimal STARS score required to achieve this rating"
    )
    creditset = models.ForeignKey(CreditSet)
    image_200 = models.ImageField(
        upload_to="seals",
        blank=True,
        null=True,
        help_text="A version of the image that fits w/in a 200x200 " "pixel rectangle",
    )
    image_large = models.ImageField(
        upload_to="seals",
        blank=True,
        null=True,
        help_text="A large version of the image that fits w/in a 1200x1200 "
        "pixel rectangle",
    )
    map_icon = models.ImageField(upload_to="seals", blank=True, null=True)
    publish_score = models.BooleanField(default=True)

    class Meta:
        ordering = ("-minimal_score",)

    def __unicode__(self):
        return self.name

    def __cmp__(self, other):
        """ Used for ordering by descending minimal_score """
        return cmp(other.minimal_score, self.minimal_score)

    def get_edit_url(self):
        return "%sratings/" % (self.creditset.get_edit_url(),)

    def get_delete_url(self):
        return "%s%d/delete/" % (self.get_edit_url(), self.id)

    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.creditset

    def get_children(self):
        """ Returns a queryset with child credit model objects -
            for hierarchy """
        return None

    def get_large_image_path(self):
        """
            Returns the full path to the image. Best practice is to have a
            trailing "/" on MEDIA_ROOT, but we check to make sure it's there
        """
        if len(settings.MEDIA_ROOT) > 1 and settings.MEDIA_ROOT[-1] == "/":
            return "%s%s" % (settings.MEDIA_ROOT, self.image_large)
        else:
            return "%s/%s" % (settings.MEDIA_ROOT, self.image_large)


class Category(VersionedModel):
    creditset = models.ForeignKey(CreditSet)
    title = models.CharField(max_length=64)
    abbreviation = models.CharField(
        max_length=6,
        help_text=(
            "Typically a 2 character code for the category. e.g.,"
            "ER for Education & Research"
        ),
    )  # TODO validation
    ordinal = models.SmallIntegerField(default=-1)
    max_point_value = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    include_in_report = models.BooleanField(default=True)
    include_in_score = models.BooleanField(default=True)

    class Meta:
        ordering = ("ordinal",)
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.title

    def __cmp__(self, other):
        """ Used for ordering by ordinal """
        return cmp(self.ordinal, other.ordinal)

    def get_creditset(self):
        return self.creditset

    def get_edit_url(self):
        return "%s%d/" % (self.creditset.get_edit_url(), self.id)

    def get_submit_url(self, submissionset=None):
        return "%s#ec_%d" % (self.creditset.get_submit_url(submissionset), self.id)

    def get_scorecard_url(self, submissionset):
        return "%s%s" % (submissionset.get_scorecard_url(), self.get_browse_url())

    def get_browse_url(self):
        return "#ec_%d" % self.id

    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return reverse("admin:credits_category_delete", args=(self.id,))

    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.creditset

    def get_children(self):
        """ Returns a queryset with child credit model objects -
            for hierarchy """
        return self.subcategory_set.all()

    def has_dependents(self):
        """ Return true if this Category has dependent objects lower in
            the credit hierarchy """
        return self.subcategory_set.all().count() > 0

    def get_dependents(self):
        """ Returns a list of dictionaries (name, queryset) for each
            set of objects directly dependent on this Category """
        return [{"name": "Subcategories", "queryset": self.subcategory_set.all()}]

    def is_innovation(self):
        """ Return True if this is an innovation category (which are
            scored differently) """
        return self.abbreviation == "IN"

    def num_submissions(self):
        """ Return the number of credit submissions started for this
            category """
        from stars.apps.submissions.models import get_active_submissions

        return get_active_submissions(category=self).count()

    def get_short_name(self):
        return self.abbreviation

    @transaction.atomic
    def update_ordering(self):
        """
            Updates all the credit numbers for credits in this category.

            Credits must be re-numbered whenever a sub-category or credit
            is Added, Deleted, or Re-ordered.

            Careful not to re-order more than once in these cases:
              (1) e.g., when a sub-category is deleted and thus goes on to
                  delete all credits
              (2) e.g., when a credit is saved, causes a re-number, which
                  in turn saves the credits, ...

             Returns True if the ordering was changed, false otherwise.
        """
        order_changed = False
        t1_count = 1
        t2_count = 1
        for sub in self.subcategory_set.all():
            for credit in sub.credit_set.all().order_by("ordinal").filter(type="t1"):
                if credit.number != t1_count:
                    credit.number = t1_count
                    credit.identifier = credit.get_identifier()
                    credit.save()
                    order_changed = True
                t1_count += 1
            # reset t1 count if version = 1.0
            if not self.creditset.has_feature("continuous_t2_numbering"):
                t2_count = 1
            for credit in sub.credit_set.all().order_by("ordinal").filter(type="t2"):
                if credit.number != t2_count:
                    credit.number = t2_count
                    credit.identifier = credit.get_identifier()
                    credit.save()
                    order_changed = True
                t2_count += 1
        return order_changed

    def save(self, *args, **kwargs):
        if self.ordinal == -1:
            self.ordinal = _get_next_ordinal(self.creditset.category_set.all())
        super(Category, self).save(*args, **kwargs)


class Subcategory(VersionedModel):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, blank=True, null=True)
    ordinal = models.SmallIntegerField(default=-1)
    max_point_value = models.IntegerField(default=0)
    description = models.TextField()
    passthrough = models.BooleanField(
        default=False,
        help_text=(
            "makes the subcategory sorta invisible, for use with "
            "Inst. Characteristics"
        ),
    )

    class Meta:
        ordering = (
            "category",
            "ordinal",
        )
        verbose_name_plural = "Subcategories"

    def __unicode__(self):
        return self.title

    def __cmp__(self, other):
        """ Used for ordering by ordinal """
        return cmp(self.ordinal, other.ordinal)

    def get_creditset(self):
        return self.category.get_creditset()

    def get_edit_url(self):
        return "%s%d/" % (self.category.get_edit_url(), self.id)

    def get_submit_url(self, submissionset=None):
        return "%s_%d" % (self.category.get_submit_url(submissionset), self.id)

    def get_submit_edit_url(self, submissionset=None):
        return "%s%s/%s/" % (
            self.category.creditset.get_submit_url(submissionset),
            self.category.abbreviation,
            self.slug,
        )

    def get_scorecard_url(self, submissionset):
        return "%s%d" % (submissionset.get_scorecard_url(), self.get_browse_url())

    def get_browse_url(self):
        return "#ec_%d_%d" % (self.category.id, self.id)

    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.category

    def get_children(self):
        """ Returns a queryset with child credit model objects - for
            hierarchy
        """
        return self.credit_set.all()

    def get_tier1_credits(self):
        return self.credit_set.filter(type="t1")

    def get_tier2_credits(self):
        return self.credit_set.filter(type="t2")

    def has_dependents(self):
        """ Return true if this Subcategory has dependent objects lower in
            the credit hierarchy """
        return self.credit_set.all().count() > 0

    def get_dependents(self):
        """ Returns a list of dictionaries (name, queryset) for each set of
            objects directly dependent on this Subcategory """
        return [{"name": "Credits", "queryset": self.credit_set.all()}]

    def num_submissions(self):
        """ Return the number of credit submissions started for this
            subcategory """
        from stars.apps.submissions.models import get_active_submissions

        return get_active_submissions(subcategory=self).count()

    def update_ordering(self):
        """
            Updates all the credit numbers for credits in this category.
            Returns True if the ordering was changed, false otherwise.
        """
        return self.category.update_ordering()

    def delete_and_update(self):
        """ Delete this sub-category and ensure category gets notified. """
        category = self.category
        self.delete()
        category.update_ordering()

    def save(self, *args, **kwargs):
        if self.ordinal == -1:
            self.ordinal = _get_next_ordinal(self.category.subcategory_set.all())
        self.slug = slugify(self.title)
        super(Subcategory, self).save(*args, **kwargs)

    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return reverse("admin:credits_subcategory_delete", args=(self.id,))


CREDIT_TYPE_CHOICES = (("t1", "Tier 1"), ("t2", "Tier 2"))


class Credit(VersionedModel):
    subcategory = models.ForeignKey(Subcategory)
    title = models.CharField(max_length=64)
    ordinal = models.SmallIntegerField(
        help_text="The order of this credit within sub-category.",
        default=-1,
        db_index=True,
    )
    number = models.SmallIntegerField(
        help_text="The number of this credit within the main category. "
        'EX: "ER Credit 1"',
        default=-1,
    )
    point_value = models.FloatField(
        help_text="The maximum points awarded for this credit."
    )
    point_minimum = models.FloatField(
        blank=True,
        null=True,
        help_text=(
            "If not blank, then this is the minimum value in "
            "the max available point range."
        ),
    )
    point_variation_reason = models.TextField(
        blank=True,
        null=True,
        help_text=(
            "An explanation of why the available points " "vary for this credit"
        ),
    )
    point_value_formula = models.TextField(
        "Max point value formula",
        blank=True,
        null=True,
        help_text=("Formula to compute the maximum available points " "for a credit"),
    )
    formula = models.TextField(
        "Points Calculation Formula",
        blank=True,
        null=True,
        default="points = 0",
        help_text="Formula to compute credit points from values of the "
        "reporting fields",
    )
    validation_rules = models.TextField(
        "Custom Validation",
        blank=True,
        null=True,
        help_text="A Python script that provides custom validation for " "this credit.",
    )
    type = models.CharField(max_length=2, choices=CREDIT_TYPE_CHOICES, db_index=True)
    applicability = models.TextField(blank=True, null=True)
    criteria = models.TextField()
    scoring = models.TextField()
    measurement = models.TextField(blank=True, null=True)
    staff_notes = models.TextField("AASHE Staff Notes", blank=True, null=True)
    identifier = models.CharField(max_length=16, default="ID?", db_index=True)
    show_info = models.BooleanField(
        default=True, help_text="Indicates if this credit will have the 'info' tab"
    )

    is_required = models.BooleanField(
        default=False,
        help_text=("Must this credit be completed before submitting for " "a rating?"),
    )
    is_opt_in = models.BooleanField(
        default=False, help_text="Is this an opt-in credit?"
    )
    resources = models.TextField(
        blank=True, null=True, help_text="A list of resources related to this credit"
    )

    class Meta:
        ordering = ("ordinal",)

    def __unicode__(self):
        return "%s: %s" % (self.identifier, self.title)

    def __cmp__(self, other):
        """ Used for ordering by ordinal """
        return cmp(self.ordinal, other.ordinal)

    def get_creditset(self):
        return self.subcategory.get_creditset()

    def get_edit_url(self):
        return "%s%d/" % (self.subcategory.get_edit_url(), self.id)

    def get_scorecard_url(self, submissionset):
        return "%s%s" % (submissionset.get_scorecard_url(), self.get_browse_url())

    def get_browse_url(self):
        return "%s/%s/%s/" % (
            self.subcategory.category.abbreviation,
            self.subcategory.slug,
            self.identifier,
        )

    def is_tier2(self):
        """ Returns True iff this credit is a Tier 2 credit """
        return self.type == "t2"

    def get_identifier(self):
        """ Returns the indentifying string for the credit ex:
            'ER Credit 10' """
        callback = self.subcategory.category.creditset.credit_identifier
        if hasattr(self, callback):
            return getattr(self, callback)()

        logger.error("No identifier could be found for credit %s" % self.id)
        return self.get_1_0_identifier()

    def get_1_0_identifier(self):
        if self.is_tier2():
            return "Tier2-%d" % self.number
        return "%s-%s" % (self.subcategory.category.abbreviation, self.number)

    def get_1_1_identifier(self):
        if self.is_tier2():
            return "%s-T2-%d" % (self.subcategory.category.abbreviation, self.number)
        return "%s-%s" % (self.subcategory.category.abbreviation, self.number)

    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.subcategory

    def get_children(self):
        """ Returns a queryset with child credit model objects -
            for hierarchy """
        return None
        # Credits are leaf nodes in the menu hierarchy (although not in
        # the model hierarchy)

    def has_dependents(self):
        """ Return true if this Credit has dependent objects lower
            in the credit hierarchy """
        return (
            self.documentationfield_set.all().count() > 0
            or self.applicabilityreason_set.all().count() > 0
        )

    def get_dependents(self):
        """ Returns a list of dictionaries (name, queryset) for each
            set of objects directly dependent on this Subcategory """
        from stars.apps.submissions.models import CreditTestSubmission

        return [
            {"name": "Reporting Fields", "queryset": self.documentationfield_set.all()},
            {
                "name": "Applicability Reasons",
                "queryset": self.applicabilityreason_set.all(),
            },
            {
                "name": "Formula Test Cases",
                "queryset": CreditTestSubmission.objects.filter(credit=self),
            },
        ]

    def num_submissions(self):
        """ Return the number of active submissions for this credit """
        return self.get_active_submissions().count()

    def get_active_submissions(self):
        """ Return a queryset with the active submissions for this credit """
        from stars.apps.submissions.models import get_active_submissions

        return get_active_submissions(credit=self)

    def get_complete_submissions(self):
        """ Return a queryset with the completed submissions for
            this credit """
        from stars.apps.submissions.models import get_complete_submissions

        return get_complete_submissions(credit=self)

    def delete_and_update(self):
        """ Delete this credit and ensure sub-category gets notified. """
        subcategory = self.subcategory
        self.delete()
        subcategory.update_ordering()

    def save(self, *args, **kwargs):
        self.identifier = self.get_identifier()
        if self.ordinal == -1:
            self.ordinal = _get_next_ordinal(
                self.subcategory.credit_set.filter(type=self.type)
            )
        # Set the defaults for t2 credits
        if self.is_tier2():
            t2_points = self.subcategory.category.creditset.tier_2_points
            self.point_value = t2_points
            self.scoring = u"%.2f points available." % t2_points
            self.formula = (
                u"""if A == True:
    points = %.2f
else:
    points = 0"""
                % t2_points
            )
        super(Credit, self).save(*args, **kwargs)

    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return reverse("admin:credits_credit_delete", args=(self.id,))

    def get_formula_url(self):
        """ Returns the URL of the page to edit the forumula for
            this credit """
        return "%sformula/" % self.get_edit_url()

    def get_next_field_identifier(self):
        """
            Helper: return the next identifier for a new documentation
            field for this credit

            @return a unique two-character identifier, of form "AB"
        """
        fields = self.documentationfield_set.all().values_list("identifier", flat=True)
        return get_next_variable_name(fields)

    def execute_formula(self, submission, debug=False):
        """
            Execute the formula for this credit for the given submission data

            @param submission: a CreditSubmission for this credit containing
                               data values to evaluate formula against

            @return: (Boolean, String/None, Exception/None, Type) = (success,
                                                                     message,
                                                                     exception,
                                                                     points)
                - success: True if formula executed without exception
                - message: suitable to report the result to the user or None
                - exception: if not success or None
                - points: the results of the formula execution (may not
                  be numeric!!)
            if debug == true:
                - debugging: any debugging output from the formula
        """
        # get the key that relates field identifiers to their values
        field_key = submission.get_submission_field_key()
        available_points = submission.get_available_points(use_cache=False)
        points = 0
        debugging = ""
        try:
            if self.formula:
                # exec formula in restricted namespace
                globals = {}  # __builtins__ gets added automatically
                locals = {
                    "points": points,
                    "AVAILABLE_POINTS": available_points,
                    "debugging": debugging,
                }
                locals.update(field_key)
                exec self.formula in globals, locals
                points = locals["points"]
                debugging = locals["debugging"]
        # Assertions may be used in formula for extra validation -
        # assume assertion text is intended for user
        except AssertionError, e:
            return (False, "%s" % e, e, points)
        except Exception, e:
            logger.exception("Formula Exception: %s" % e)
            if not debug:
                return (
                    False,
                    "There was an error processing this credit. AASHE "
                    "has noted the error and will work to resolve the "
                    "issue.",
                    e,
                    points,
                )
            else:
                debugging += "\n***Exception***\n %s" % e
                return (
                    False,
                    "There was an error processing this credit. AASHE "
                    "has noted the error and will work to resolve the "
                    "issue.",
                    e,
                    points,
                    debugging,
                )
        if not debug:
            return (True, "Formula executed successfully", None, points)
        else:
            return (True, "Formula executed successfully", None, points, debugging)

    def execute_validation_rules(self, submission):
        """
            Execute the validation rules for this credit for the given
            submission data

            @param submission: a CreditSubmission or CreditSubmissionForm for
                               this credit containing data values to validate

            @return: errors, warnings
                - errors: a dictionary of errors, using the field's
                          identifier as the key for each error
                    - may contain an 'top' key for credit-wide errors;
                    - will be empty if validation passed without error
                - warnings: ditto but for warnings rather than errors.
        """
        # get the key that relates field identifiers to their values
        field_key = submission.get_submission_field_key()
        errors = {}
        warnings = {}
        try:
            if self.validation_rules:
                # exec the validation in restricted namespace
                globals = {}  # __builtins__ gets added automatically
                locals = {"errors": errors, "warnings": warnings}
                locals.update(field_key)
                exec self.validation_rules in globals, locals
                errors, warnings = locals["errors"], locals["warnings"]
        # Assertions may be used in validation to ensure conditions
        # for validation are met - assume any assertion text is
        # intended for user
        except AssertionError, e:
            if str(e):
                errors["top"] = "%s" % e
        except Exception, e:
            logger.exception("Validation Exception: %s" % e)
            errors["top"] = (
                "There was an error processing this credit. "
                "AASHE has noted the error and will work to "
                "resolve the issue."
            )
        return errors, warnings

    def execute_point_value_formula(self, submission):
        """
            Execute the point value formula for this credit for the
            given submission data

            @param submission: a CreditSubmission for this credit containing
                               data values to evaluate formula against

            @return: (Boolean, String/None, Exception/None, Type) = (success,
                                                                     message,
                                                                     exception,
                                                                     points)
                - success: True if formula executed without exception
                - message: suitable to report the result to the user or None
                - exception: if not success or None
                - points: the results of the formula execution (may not
                  be numeric!!)
        """
        if self.point_value_formula is None:
            logger.error("Point Formula Executed without Formula for %s" % self)
            return (True, "Formula failed to run", None, self.point_value)

        # get the key that relates field identifiers to their values
        field_key = submission.get_submission_field_key()
        available_points = self.point_value  # default
        try:
            # exec formula in restricted namespace
            globals = {}  # __builtins__ gets added automatically
            locals = {"MAX_POINTS": self.point_value, "MIN_POINTS": self.point_minimum}
            locals.update(field_key)
            exec self.point_value_formula in globals, locals
            available_points = locals["available_points"]
        # Assertions may be used in formula for extra validation -
        # assume assertion text is intended for user
        except AssertionError, e:
            return (False, "%s" % e, e, available_points)
        except Exception, e:
            logger.exception("Formula Exception: %s" % e)
            return (
                False,
                "There was an error processing this credit. AASHE "
                "has noted the error and will work to resolve the issue.",
                e,
                available_points,
            )
        return (True, "Formula executed successfully", None, available_points)

    def compile_formula(self):
        """ See global compile_formula function... """
        return compile_formula(self.formula)

    def compile_validation_rules(self):
        """ See global compile_formula function... """
        return compile_formula(self.validation_rules, "Validation Rules")

    def get_child_fields(self):
        """
            Returns a list of fields that are nested in another tabular field
        """
        df_excludes = []
        for df in self.documentationfield_set.all().filter(type="tabular"):
            for row in df.tabular_fields["fields"]:
                for cell in [cell for cell in row if cell != ""]:
                    df_excludes.append(int(cell))
        return df_excludes

    def get_nested_documentation_fields(self):
        """
            Returns a list of documentation fields, excluding those that are
            nested in the table of another
        """
        return self.documentationfield_set.exclude(id__in=self.get_child_fields())

    def update_abbreviation_identifier(self):
        """ Resave the credit identifier """


def compile_formula(formula, label="Formula"):
    """
        Global function provided so that field validation has access to
        wrapped compile functionality

        Attempt to compile a formula.
        @return (boolean, message)
            - If the formula is None or compiles successfully, return true
            - If the formula fails to compile, return false

        #doctest:
        >>> compile_formula("")
        (True, 'No Formula specified')
        >>> compile_formula("A=3\\n points = 2 if A>3 else 1")
        (False, 'Formula did not compile: unexpected indent (Formula, line 2)')
        >>> compile_formula("A=3\\npoints = 2 if A>3 else 1")
        (True, 'Formula compiled - code is valid.')

    """
    if formula:
        try:
            compile(formula, label, "exec")
            return (True, "%s compiled - code is valid." % label)
        except Exception, e:
            return (False, "%s did not compile: %s" % (label, e))
    else:
        return (True, "No %s specified" % label)


class ApplicabilityReason(VersionedModel):
    """
        Models reasons why a particular credit might be allowed to be
        considered not-applicable
    """

    credit = models.ForeignKey(Credit)
    reason = models.CharField(max_length=128)
    help_text = models.TextField(null=True, blank=True)
    ordinal = models.IntegerField()

    class Meta:
        ordering = ("ordinal",)

    def __unicode__(self):
        return self.reason

    def get_absolute_url(self):
        return "%sapplicability/" % self.credit.get_edit_url()

    def get_edit_url(self):
        return "%s%d/" % (self.get_absolute_url(), self.id)

    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return reverse(
            "tool:credit_editor:applicability-reason-delete", args=(self.id,)
        )

    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.credit

    def num_submissions(self):
        """ Return the number of credit submissions where this
            ApplicabilityReason was cited """
        from stars.apps.submissions.models import get_na_submissions

        return get_na_submissions(applicability_reason=self).count()

    def delete(self):
        """ Override delete to update any submissions that reference this
            reason - otherwise the whole submission would be deleted! """
        from stars.apps.submissions.models import get_na_submissions

        submissions = get_na_submissions(applicability_reason=self)
        for submission in submissions:
            submission.applicability_reason = None
            submission.mark_as_in_progress()
            submission.save()
        super(ApplicabilityReason, self).delete()

    def save(self, *args, **kwargs):
        if self.ordinal == -1:
            self.ordinal = _get_next_ordinal(self.credit.applicabilityreason_set.all())
        super(ApplicabilityReason, self).save(*args, **kwargs)


DOCUMENTATION_FIELD_TYPES = (
    ("text", "text"),
    ("long_text", "long text"),
    ("numeric", "numeric"),
    ("boolean", "yes/no"),
    ("choice", "choose one"),
    ("multichoice", "choose many"),
    ("url", "url"),
    ("date", "date"),
    ("upload", "upload"),
    ("tabular", "tabular"),
    ("calculated", "calculated")
    #  ('multiple_upload', 'multiple upload'),
)

REQUIRED_TYPES = (
    ("opt", "optional"),
    ("cond", "conditionally required"),
    ("req", "required"),
)

from django import forms

TYPE_TO_WIDGET = {
    "text": forms.TextInput,
    "long_text": forms.Textarea,
    "numeric": forms.TextInput,
    "boolean": forms.Select,
    "url": forms.TextInput,
    "date": forms.TextInput,
    "upload": forms.FileInput,
    "choice": forms.Select,
    "tabular": forms.Textarea,  # @todo - custom
    "calculated": forms.TextInput,
}


class Unit(models.Model):
    name = models.CharField(max_length=32)
    equivalent = models.ForeignKey("Unit", null=True, blank=True)
    # This is the ratio of this unit to its equivalent.
    # For example, if this unit is Square Feet, then the ratio is 0.092903
    # because 1 Square Foot is 0.092903 Square Meters
    ratio = models.FloatField(
        null=True,
        blank=True,
        default=1.0,
        help_text="Ex: 0.092903 for Square Feet because 1sqf = 0.092903sqm",
    )
    is_metric = models.BooleanField(default=False)

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        if self.name == DUMMY_UNIT_LABEL:
            return ""

        return self.name

    def correct_variation(self, quantity):
        """
            adjusts for variation in conversions caused by float conversions

            example: 2000 can convert to metric and then back to 1999.99212013
            ideally, this should convert back to 2000
        """
        round_up = math.ceil(quantity)
        if round_up - quantity < 0.01:
            return round_up

        round_down = math.floor(quantity)
        if quantity - round_down < 0.01:
            return round_down

        return quantity

    def convert(self, quantity):
        """Return the quantity of equivalent Units."""
        return self.correct_variation(quantity * self.ratio)

    def revert(self, quantity):
        """Revert `quantity` from the equivalent Unit to this Unit.

        Assumes self.ratio is not None or 0.0
        """
        return self.correct_variation(quantity / self.ratio)

    def save(self, *args, **kwargs):
        """Don't save any nonsensible ratios -- i.e., 0 or None."""
        if self.ratio:
            super(Unit, self).save(*args, **kwargs)
        else:
            raise Exception("ratio must be set and non-zero")


class DocumentationField(VersionedModel):
    credit = models.ForeignKey(Credit)
    header = models.TextField(
        "Header",
        blank=True,
        null=True,
        default="",
        help_text=("HTML to display before field " "in Reporting Tool"),
    )
    title = models.CharField("Promt/Question", max_length=255)
    type = models.CharField(
        max_length=16, choices=DOCUMENTATION_FIELD_TYPES, db_index=True
    )
    last_choice_is_other = models.BooleanField(
        default=False,
        help_text="If selected, the last choice provides a box to enter "
        "a user-defined choice",
    )
    min_range = models.IntegerField(
        help_text="Numeric: minimum integer value, Date: earliest year.",
        blank=True,
        null=True,
    )
    max_range = models.IntegerField(
        help_text="Text: max character count, LongText: max word count, "
        "Numeric: max integer value, Date: latest year.",
        blank=True,
        null=True,
    )
    units = models.ForeignKey(Unit, null=True, blank=True)
    inline_help_text = models.TextField(null=True, blank=True)
    tooltip_help_text = models.TextField(null=True, blank=True)
    ordinal = models.FloatField(default=-1.0, db_index=True)
    required = models.CharField(
        max_length=8,
        choices=REQUIRED_TYPES,
        default="req",
        help_text="If a field is conditionally required it is important "
        "to note that in the help-text and to define a custom "
        "validation rule.",
    )
    # Field identifier for the Formula editor - auto-generated.
    identifier = models.CharField(max_length=2, db_index=True)
    is_published = models.BooleanField(
        default=True,
        help_text="This documentation field will be displayed in the "
        "public report. Applies to 99.99% of fields.",
    )
    tabular_fields = JSONField(blank=True, null=True)
    formula_terms = models.ManyToManyField(
        "self",
        related_name="calculated_fields",
        help_text="Fields used in this field's formula calculation.",
        blank=True,
        symmetrical=False,
    )
    copy_from_field = models.ForeignKey(
        "self",
        related_name="source_field",
        on_delete=models.SET_NULL,
        help_text="Field whose value can be copied into this field.",
        null=True,
        blank=True,
    )
    formula = models.TextField(
        "Calculation Formula",
        blank=True,
        null=True,
        default="",
        help_text="Formula to compute field value",
    )
    imperial_formula_text = models.CharField(
        max_length=255, blank=True, null=True, help_text="Imperial formula text"
    )
    metric_formula_text = models.CharField(
        max_length=255, blank=True, null=True, help_text="Metric formula text"
    )

    class Meta:
        ordering = ("ordinal",)
        unique_together = ("credit", "identifier")

    @property
    def init_track_fields(self):
        return ["formula"]

    def get_creditset(self):
        return self.credit.get_creditset()

    def get_sub_table(self):
        return get_array_for_tabular_fields(self)

    def save(self, *args, **kwargs):
        """ 1. Assign identifier and ordinal;

        """
        if not self.identifier:
            self.identifier = self.credit.get_next_field_identifier()
        if self.ordinal == -1.0:
            self.ordinal = _get_next_ordinal(self.credit.documentationfield_set.all())

        # If this DocumentationField's formula is new or has changed,
        # update it's list of formula terms, then recalculate any
        # CreditSubmissions that depend on the formula.
        update_terms_and_dependents = False
        if self.formula:
            if not self.pk or (  # new formula
                self.formula != self._original_formula
            ):  # changed formula  # noqa
                update_terms_and_dependents = True
        elif self._original_formula:  # from formula to blank formula
            update_terms_and_dependents = True

        super(DocumentationField, self).save(*args, **kwargs)

        if update_terms_and_dependents:
            self.update_formula_terms()
            self.recalculate_dependent_submissions()
        if self.type == "tabular":
            self.reorder_tabular_children()

    def recalculate_dependent_submissions(self):
        """Recalculate all calculated CreditSubmissions that depend on this
        DocumentationFields's formula.
        """
        from stars.apps.submissions.models import NumericSubmission

        dependent_submissions = NumericSubmission.objects.filter(
            documentation_field=self
        )

        for dependent_submission in dependent_submissions:
            dependent_submission.calculate()
            if (
                dependent_submission.value != dependent_submission._original_value
            ):  # NOQA

                dependent_submission.save()

    def update_formula_terms(self):
        """Update the set of fields upon which this fields' calculation
        depends.  No-op for fields that aren't calculated fields.
        """
        if self.type != "calculated":
            return

        formula_terms = self.get_formula_terms()  # parses forumula
        formula_fields = self.get_fields_for_terms(terms_list=formula_terms)  # hits db

        self.formula_terms.clear()  # hits db?
        self.formula_terms.add(*formula_fields)  # hits db?

    def get_formula_terms(self):
        """Return a list of terms used in self.formula.
        """
        if not self.formula:
            return []
        try:
            parsed_formula = ast.parse(self.formula)
        except Exception, exc:
            logger.warning(
                "Unparseable formula: '{formula}' in {id} ({exc})".format(
                    formula=self.formula,
                    id="DocumentationField(pk=" + str(self.pk) + ")",
                    exc=exc,
                )
            )
            return []
        terms = [
            node.id
            for node in list(ast.walk(parsed_formula))
            if isinstance(node, ast.Name)
        ]
        return terms

    def get_fields_for_terms(self, terms_list):
        """Return a QuerySet of DocumentationFields whose identifiers
        match the terms in `terms_list`.
        """
        return DocumentationField.objects.filter(
            credit=self.credit, identifier__in=terms_list
        )

    def __unicode__(self):
        """ Limit the length of the text representation to 50 characters """
        label = smart_unicode(
            self.title, encoding="utf-8", strings_only=False, errors="strict"
        )
        MAX = 100
        if len(label) > MAX:
            l, b, r = label[0:MAX].rpartition(" ")
            if not l:
                l = label[0:MAX]
            label = u"%s ..." % l
        return label

    def get_escaped_tooltip_help_text(self):
        if self.tooltip_help_text:
            return self.tooltip_help_text.replace('"', "'")
        else:
            return ""

    def __cmp__(self, other):
        """ Used for ordering by ordinal """
        return cmp(self.ordinal, other.ordinal)

    def get_edit_url(self):
        return "%s%d/" % (self.credit.get_edit_url(), self.id)

    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.credit

    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return reverse("admin:credits_documentationfield_delete", args=(self.id,))

    def is_required(self):
        """ Return true if this field is required to complete a submission """
        return self.required == "req"

    def is_conditionally_required(self):
        """ Return true if this field is conditionally required """
        return self.required == "cond"

    def is_upload(self):
        """ Return true if this field is a file upload """
        return self.type == "upload"

    def is_single_choice(self):
        """ Return true if this field is a single choice """
        return self.type == "choice"

    def is_multi_choice(self):
        """ Return true if this field is a multi-choice """
        return self.type == "multichoice"

    def is_choice(self):
        """ Return true if this field is a choice """
        return self.type.endswith("choice")

    def has_other_choice(self):
        """ Return True iff this field specifies a choice with other
            type selection """
        return self.last_choice_is_other

    def can_have_min_max(self):
        """ Return True if the min / max options apply to this field. """
        return (
            self.type in ("text", "long_text", "numeric", "date")
            and not self.is_choice()
        )

    def can_have_units(self):
        """ Return True if the units option apply to this field. """
        return (
            self.type in ("text", "long_text", "numeric", "calculated")
            or self.is_choice()
        )

    @property
    def metric_units(self):
        if self.units:
            if self.units.is_metric:
                return self.units
            else:
                return self.units.equivalent

    @property
    def us_units(self):
        if self.units:
            if not self.units.is_metric:
                return self.units
            else:
                return self.units.equivalent

    def num_submissions(self):
        """ Return the number of credit submissions where this
            DocumentationField is in use """
        return self.get_active_submissions().count()

    def get_active_submissions(self):
        """ Return queryset with the FieldSubmissions where this
            DocumentationField is in use """
        from stars.apps.submissions.models import get_active_field_submissions

        return get_active_field_submissions(self)

    def get_widget(self):
        """ Returns the appropriate widget for this type of field """
        return TYPE_TO_WIDGET[self.type]

    def reorder_tabular_children(self):
        """
            Reassign the ordinal value of child documentation fields in
            tabular field.
        """
        i = self.ordinal + 0.01
        for row in self.tabular_fields["fields"]:
            for cell in [cell for cell in row if cell != ""]:
                field = DocumentationField.objects.get(pk=int(cell))
                field.ordinal = i
                field.save()
                i += 0.01


def documentation_field_post_init(sender, instance, **kwargs):
    for field in instance.init_track_fields:
        setattr(instance, "_original_%s" % field, getattr(instance, field, None))


post_init.connect(
    documentation_field_post_init,
    sender=DocumentationField,
    dispatch_uid="stars.apps.credits.models.documentation_field_post_init",
)  # noqa


class Choice(VersionedModel):
    """
        A choice for a documentation field
        Stores both 'official' (bonafide) choices defined by STARS and
        user-defined choices.
    """

    documentation_field = models.ForeignKey(DocumentationField)
    choice = models.CharField("Choice", max_length=255)
    ordinal = models.SmallIntegerField(default=-1)
    # 'bonafide' choices are defined by STARS staff, other choices are
    # user=defined
    is_bonafide = models.BooleanField(default=True)

    class Meta:
        ordering = ("ordinal",)

    def __unicode__(self):
        return self.choice

    def __cmp__(self, other):
        """ Used for ordering by ordinal """
        return cmp(self.ordinal, other.ordinal)

    def get_absolute_url(self):
        return "%schoice/" % self.documentation_field.get_edit_url()

    def get_edit_url(self):
        return "%s%d/" % (self.get_absolute_url(), self.id)

    def get_delete_url(self):
        """ Returns the URL of the page to confirm deletion of this object """
        return "%sdelete/" % self.get_edit_url()

    def get_parent(self):
        """ Returns the parent element for crumbs """
        return self.documentation_field

    def save(self, *args, **kwargs):
        if self.ordinal is None or self.ordinal == -1:
            self.ordinal = _get_next_ordinal(self.documentation_field.choice_set.all())
        super(Choice, self).save(*args, **kwargs)

    def num_submissions(self):
        """ Return the number of credit submissions where this Choice was
            cited """
        from stars.apps.submissions.models import get_active_field_submissions

        return get_active_field_submissions(choice=self).count()
