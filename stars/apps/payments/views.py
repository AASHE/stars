from abc import ABCMeta, abstractmethod

from django.contrib import messages
from django.contrib.formtools.wizard.views import SessionWizardView
from django.http import (HttpResponse,
                         HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.utils import simplejson as json

from . import forms
from ..institutions.models import Subscription, SubscriptionPurchaseError
from ..registration.models import (ExpiredDiscountCodeError,
                                   InvalidDiscountCodeError,
                                   get_current_discount)

PAY_WHEN = 'pay_when'

SUCCESS, FAILURE = True, False


def amount_due_more_than_zero(wizard):
    """Pulls the amount due from the request session, if it's there, and
    returns True if it's greater than 0.00.  Otherwise, returns False.

    For use in SubscriptionPaymentWizard constructor, in the
    condition_dict argument, to determine if the payment options
    form should be shown.  (Don't want to show it if the amount
    due is 0.00).

    Usage:

        from django.conf.urls import patterns

        from payments.views import (amount_due_more_than_zero,
                                    SubscriptionPaymentWizard)

        urlpatterns = patterns('',
            (r'^contact/$', SubscriptionPaymentWizard.as_view(
                SubscriptionPaymentWizard.FORM_LIST,
                condition_dict={
                    str(SubscriptionPaymentWizard.PAYMENT_OPTIONS):
                    amount_due_more_than_zero})))

    """
    return bool(wizard.request.session.get('amount_due', 0.00))


class SubscriptionPaymentWizard(SessionWizardView):

    __metaclass__ = ABCMeta

    PRICE, PAYMENT_OPTIONS, SUBSCRIPTION_CREATE = 0, 1, 2

    TEMPLATES = {
        PRICE: "payments/subscription_price.html",
        PAYMENT_OPTIONS: "payments/subscription_payment_options.html",
        SUBSCRIPTION_CREATE: "payments/subscription_payment_create.html"}

    FORMS = [(PRICE, forms.SubscriptionPriceForm),
             (PAYMENT_OPTIONS, forms.SubscriptionPaymentOptionsForm),
             (SUBSCRIPTION_CREATE, forms.DummySubscriptionCreateForm)]

    FORM_LIST = [form[1] for form in FORMS]

    subscription_purchase_outcome = FAILURE  # safety in pessimism

    @property
    @abstractmethod
    def success_url(self):
        raise NotImplementedError('subclass of SubscriptionPaymentWizard '
                                  'must define success_url')

    @abstractmethod
    def get_institution(self):
        pass

    def get_template_names(self):
        return [self.TEMPLATES[int(self.steps.current)]]

    def post(self, *args, **kwargs):
        if self.request.is_ajax() and int(self.steps.current) == self.PRICE:
            form = self.get_form(data=self.request.POST)
            return self._process_step_price(form=form)
        else:
            return super(SubscriptionPaymentWizard, self).post(*args,
                                                               **kwargs)

    def process_step(self, form):
        {self.PRICE: self._process_step_price,
         self.PAYMENT_OPTIONS: self._process_step_payment_options,
         self.SUBSCRIPTION_CREATE: self._process_step_subscription_create}[
             int(self.steps.current)](form)

        return super(SubscriptionPaymentWizard, self).process_step(form)

    def get_context_data(self, form, **kwargs):
        context = super(SubscriptionPaymentWizard, self).get_context_data(
            form, **kwargs)
        extra_context_methods = {
            self.PRICE: self._get_context_data_price,
            self.PAYMENT_OPTIONS: self._get_context_data_payment_options,
            self.SUBSCRIPTION_CREATE:
                self._get_context_data_subscription_create}

        current_step = int(self.steps.current)
        extra_context = extra_context_methods[current_step](form, **kwargs)
        context.update(extra_context)

        return context

    def _get_context_data_price(self, form, **kwargs):
        context = {}

        (subscription_start_date, subscription_end_date) = (
            Subscription.get_date_range_for_new_subscription(
                self.get_institution()))

        context['subscription_start_date'] = subscription_start_date
        context['subscription_end_date'] = subscription_end_date

        prices = Subscription.get_prices_for_new_subscription(
            institution=self.get_institution())

        context['prices'] = prices

        return context

    def _get_context_data_payment_options(self, form, **kwargs):
        context = {}
        context['amount_due'] = self.request.session['amount_due']
        return context

    def _get_context_data_subscription_create(self, form, **kwargs):
        context = {}
        # TODO: is this necessary? can a template resolve {{ var }}
        # to request.session[var]?
        context['amount_due'] = self.request.session['amount_due']
        context['pay_when'] = self.pay_when
        return context

    def _process_step_price(self, form):
        ajax_data = {}
        if self.request.is_ajax():
            promo_code_id = '_'.join(('id', form.add_prefix('promo_code')))
            promo_code = self.request.POST[promo_code_id]
        else:
            promo_code_name = form.add_prefix('promo_code')
            promo_code = self.request.POST[promo_code_name]
        try:
            ajax_data['prices'] = Subscription.get_prices_for_new_subscription(
                institution=self.get_institution(),
                promo_code=promo_code)
        except (ExpiredDiscountCodeError, InvalidDiscountCodeError) as ex:
            # promo code provided is invalid or expired, so throw it
            # away:
            promo_code = None
            # get the prices without a promo code:
            ajax_data['prices'] = Subscription.get_prices_for_new_subscription(
                institution=self.get_institution())
            if self.request.is_ajax():
                # send the error back to the caller:
                promo_code_id = 'id_{step}-promo_code'.format(
                    step=self.steps.current)
                ajax_data['form-errors'] = {promo_code_id: ex.message}
                return HttpResponseBadRequest(json.dumps(ajax_data),
                                              mimetype='application/json')
        finally:
            # always store the promo_code and amount_due in the
            # session, exception or not, is_ajax() or not:
            self.request.session['promo_code'] = promo_code
            self.request.session['amount_due'] = ajax_data['prices']['total']

            if self.request.session['amount_due'] <= 0.00:
                # When the amount due is zero (e.g., when a 100%
                # discount code is used), the Payment Options view is
                # skipped, so self.request.session[PAY_WHEN] doesn't
                # get set.  Since pay_when is used to determine which
                # Subscription Create form to display (pay later or
                # pay now by credit card), we'll set pay_when to
                # PAY_LATER here -- this prevents asking for credit
                # card info when the subscription is free.
                self.request.session[PAY_WHEN] = Subscription.PAY_LATER

        if self.request.is_ajax():
            discount = get_current_discount(promo_code)
            if discount:
                ajax_data.update({'discount_amount': discount.amount,
                                  'discount_percentage': discount.percentage})
                return HttpResponse(json.dumps(ajax_data),
                                    mimetype='application/json')

    def _process_step_payment_options(self, form):
        # Pass on the payment option selected:
        self.request.session[PAY_WHEN] = form.cleaned_data[PAY_WHEN]

    def _process_step_subscription_create(self, form):
        """Purchases a subscription, and maybe takes a payment for it."""
        if self.pay_when == Subscription.PAY_NOW:
            card_num = form.cleaned_data['card_number']
            exp_date = self.get_exp_date(form)
        else:
            card_num = None
            exp_date = None

        promo_code = self.request.session.get('promo_code')

        try:
            subscription = Subscription.purchase(
                institution=self.get_institution(),
                pay_when=self.pay_when,
                user=self.request.user,
                promo_code=promo_code,
                card_num=card_num,
                exp_date=exp_date)
        except SubscriptionPurchaseError as spe:
            messages.error(self.request, str(spe))
            self.subscription_purchase_outcome = FAILURE
            # return self.render_revalidation_failure(
            #     step=str(SUBSCRIPTION_CREATE),
            #     form=form)
        else:
            self.subscription_purchase_outcome = SUCCESS
            messages.info(self.request,
                          """Thank you!
                          Your new subscription lasts from
                          {start} to {finish}.""".format(
                              start=subscription.start_date,
                              finish=subscription.end_date))

    def get_exp_date(self, form):
        """
            Returns the expiration date from `form`, in the format
            the credit card processor expects, a string of 'MMYYYY'.
        """
        exp_date_month = form.cleaned_data['exp_month']
        exp_date_year = form.cleaned_data['exp_year']
        exp_date = exp_date_month + exp_date_year
        return exp_date

    @property
    def pay_when(self):
        """Just a shorthand for self.request.session[PAY_WHEN]."""
        return self.request.session[PAY_WHEN]

    def render_done(self, form, **kwargs):
        if self.subscription_purchase_outcome == SUCCESS:
            return super(SubscriptionPaymentWizard, self).render_done(
                form, **kwargs)
        else:
            # return self.render_revalidation_failure(
            #     step=str(SUBSCRIPTION_CREATE),
            #     form=self.form_list[str(SUBSCRIPTION_CREATE)],
            #     initial_dict={str(SUBSCRIPTION_CREATE): form.cleaned_data})
            return self.render(
                form,
                initial_dict={
                    str(self.SUBSCRIPTION_CREATE): form.cleaned_data})

    def done(self, forms, **kwargs):
        return HttpResponseRedirect(self.success_url)

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        if int(step) == self.SUBSCRIPTION_CREATE:
            correct_pay_when_form = {
                Subscription.PAY_LATER: forms.SubscriptionPayLaterForm,
                Subscription.PAY_NOW: forms.SubscriptionPayNowForm}[
                    self.pay_when]
            self.form_list[str(self.SUBSCRIPTION_CREATE)] = (
                correct_pay_when_form)
        return super(SubscriptionPaymentWizard, self).get_form(step,
                                                               data,
                                                               files)
