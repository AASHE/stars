#!/usr/bin/env python

"""
    Tests the connection with Cybersource's payment gateway in TEST MODE.
    
    usage: python manage.py execfile tests/cybersource.py
"""

from django.conf import settings
from django.template import Context, loader

import urllib2
from xml.etree.ElementTree import fromstring
from datetime import datetime

from stars.apps.registration.views import process_payment

account = {
    "merchant_id": settings.CYBERSOURCE_MERCHANT_ID,
    "password": settings.CYBERSOURCE_SOAP_KEY,
}
payment_dict = {
    'cc_number': "4111111111111111",
    'exp_month': 12,
    'exp_year': 2010,
    'cv_number': 123,
    'billing_address': "123 street",
    'billing_city': "city",
    'billing_state': "ma",
    'billing_zipcode': "01234",
    'country': "USA",
    'billing_firstname': "john",
    'billing_lastname': "doe",
    'billing_email': 'ben@aashe.org',
}
product_dict = {
    'price': 1,
    'quantity': 1,
    'name': "STARS Participant Registration",
}
account = {
    "merchant_id": settings.CYBERSOURCE_MERCHANT_ID,
    "password": settings.CYBERSOURCE_SOAP_KEY,
}

result = process_payment(payment_dict, [product_dict], ref_code="Test: %s" % datetime.now().isoformat(), test_mode=True, debug=True)

print result

