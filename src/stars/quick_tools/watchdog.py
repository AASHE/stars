
from django.shortcuts import render_to_response, get_object_or_404

from stars.apps.helpers import watchdog
"""
    Tests for the watchdog error logging module
    
    usage: python manage.py execfile tests/watchdog.py
    
    THIS HAS BEEN CONVERTED INTO A DOCTEST
"""

print "---------------TESTING watchdog function -------------------------"
try:
    watchdog.log("Test", "Test message sent to Watchdog", watchdog.ERROR)
except Exception, e:
        print "Nope: %s" % e
