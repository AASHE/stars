from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models


class InvalidDiscountCodeError(Exception):
    pass


class ExpiredDiscountCodeError(Exception):
    pass


def get_current_discount(code):
    """
    Returns the ValueDiscount with code == `code` if it's currently
    applicable.

    Raises InvalidDiscountCodeErrorf if there's no match on `code`,
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


class ValueDiscount(models.Model):

    code = models.CharField(unique=True,
                            max_length=36)
    amount = models.PositiveIntegerField(
        help_text='Discount Amount')
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
        if (self.amount == 0) and (self.percentage == 0):
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
        return (self._amount_or_percentage_required() and
                self._amount_and_percentage_disallowed() and
                self._start_date_before_end_date())

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
