from datetime import date
from logging import getLogger

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models

logger = getLogger('stars')


class InvalidDiscountCodeError(Exception):
    pass


class ExpiredDiscountCodeError(Exception):
    pass


class NoActiveAutomaticDiscountError(Exception):
    pass


def get_current_discount(code):
    """
    Returns the ValueDiscount with code == `code` if it's currently
    applicable.

    Raises InvalidDiscountCodeError if there's no match on `code`,
    and ExpiredDiscountCodeError if the discount has expired.
    """
    try:
        discount = ValueDiscount.objects.get(code=code)
    except ValueDiscount.DoesNotExist:
        raise InvalidDiscountCodeError(
            '{code} is not a valid discount code'.format(code=code))

    if discount.current:
        return discount
    else:
        raise ExpiredDiscountCodeError(
            'Discount code {code} has expired'.format(code=code))


def get_automatic_discount(extra_globals=None,
                           extra_locals=None):
    """
    Returns the AutomaticDiscount that's in effect now.
    If there is one.
    """
    try:
        automatic_discount = ValueDiscount.objects.get(
            automatic=True,
            start_date__lte=date.today(),
            end_date__gte=date.today())
    except ValueDiscount.DoesNotExist:
        raise NoActiveAutomaticDiscountError

    if (automatic_discount and
        automatic_discount.discount_applies(extra_globals=extra_globals,
                                            extra_locals=extra_locals)):
        return automatic_discount
    else:
        raise NoActiveAutomaticDiscountError


class ValueDiscount(models.Model):

    code = models.CharField(unique=True,
                            max_length=36)
    amount = models.PositiveIntegerField(
        help_text='Discount Amount')
    applicability_filter = models.TextField(blank=True)
    automatic = models.BooleanField(default=False)
    description = models.CharField(blank=True,
                                   max_length=78)
    percentage = models.PositiveIntegerField(
        default=0,
        help_text='Discount Percentage',
        validators=[MaxValueValidator(100)])
    start_date = models.DateField(help_text='Valid From')
    end_date = models.DateField(help_text='Valid Until')

    def __unicode__(self):
        return (u'code={code}, amount={amount}, '
                u'percentage={percentage} '
                u'start_date={start_date}, end_date={end_date}').format(
                    **self.__dict__)

    def _amount_or_percentage_required(self):
        """Ensure amount or percentage are specified.
        """
        if (self.amount in (0, None)) and (self.percentage in (0, None)):
            raise ValidationError("An amount or percentage must be specified.")
        return True

    def _amount_and_percentage_disallowed(self):
        """Ensure both amount and percentage are not specified.
        """
        if (self.amount > 0) and (self.percentage > 0):
            raise ValidationError("Only an amount or percentage can "
                                  "be specified, not both.")
        return True

    def _start_date_before_end_date(self):
        """Ensure start_date is before end_date.
        """
        if self.start_date > self.end_date:
            raise ValidationError("Start date can't be before end date.")
        return True

    def clean(self):
        if not self._amount_or_percentage_required():
            raise ValidationError('amount or percentage required')
        if not self._amount_and_percentage_disallowed():
            raise ValidationError('only amount or percentage are allowed')
        if not self._start_date_before_end_date():
            raise ValidationError('start date must come before end date')
        if (self.automatic and
            self._overlapping_automatic_discount()):
            raise ValidationError(
                'cannot have overlapping automatic discounts')

    def apply(self, price):
        """Apply this discount, and return the discounted price."""
        if self.amount:
            return price - self.amount
        elif self.percentage:
            return price - (price * (self.percentage / 100.0))

    @property
    def current(self):
        """Is this discount effective today?"""
        today = date.today()
        return (self.start_date <= today and
                self.end_date >= today)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(ValueDiscount, self).save(*args, **kwargs)

    def _overlapping_automatic_discount(self):
        """Is there any other AutomaticDiscount that overlaps
        with this one's start and end dates?
        """
        return (
            # Any others with start_date within this discount's range?
            ValueDiscount.objects.filter(
                automatic=True,
                start_date__range=(self.start_date,
                                   self.end_date)).exclude(
                                       id=self.id).exists() or
            # Any others with end_date within this discount's range?
            ValueDiscount.objects.filter(
                automatic=True,
                end_date__range=(self.start_date,
                                 self.end_date)).exclude(
                                     id=self.id).exists() or
            # Any others with start_date before this discount's range
            # and end_date after it?
            (
                ValueDiscount.objects.filter(
                    automatic=True,
                    start_date__lte=self.start_date).exclude(
                        id=self.id).exists() and
                ValueDiscount.objects.filter(
                    automatic=True,
                    end_date__gte=self.end_date).exclude(
                        id=self.id).exists()
            )
        )

    def discount_applies(self,
                         extra_globals=None,
                         extra_locals=None):
        """eval()'s applicability_filter, and returns the result.
        
        If applicability_filter is blank, returns True.

        If an exception is raised while eval()'ing applicability_filter,
        returns False.

        extra_globals are added to globals(), extra_locals()
        are added to locals() before eval()'ing.
        """
        if extra_globals:
            expandable_globals = dict(globals().items() +
                                      extra_globals.items())
        else:
            expandable_globals = globals()
            
        if extra_locals:
            expandable_locals = dict(locals().items() +
                                     extra_locals.items())
        else:
            expandable_locals = locals()

        if self.applicability_filter:
            try:
                return eval(self.applicability_filter,
                            expandable_globals,
                            expandable_locals)
            except Exception as exc:
                logger.error(
                    "eval() of applicability_filter failed; "
                    "AutomaticDiscount.code is {code}: {exc}".format(
                        code=self.code,
                        exc=exc))
                return False
        else:
            return True  # Automatic discounts are automatic by default.
