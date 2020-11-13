"""
    This file configures the development environment on the aashe server.
    Apache bypasses settings.py and calls this file explicitly for setup.
"""

from settings import *

# Celery
CELERY_RESULT_DBURI = "sqlite:///var/www/stars/stars-celery-results.db"
CELERY_CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

ANALYTICS_ID = "UA-1056760-7"

#THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pgmagick_engine.Engine"
THUMBNAIL_ENGINE = "sorl.thumbnail.engines.pil_engine.Engine"
THUMBNAIL_FORMAT = 'PNG'

INSTALLED_APPS = INSTALLED_APPS + ('memcache_status',)

XMLRPC_VERBOSE = False

#if manage.py test was called, use test settings
if 'test' in sys.argv:
    
    CACHE_BACKEND = "file:///tmp/stars-cache"