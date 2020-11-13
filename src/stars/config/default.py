"""
    Default config file for development in a local environment.
"""

from settings import *
import os

homedir = os.path.expanduser('~')

# no emails during local dev
ADMINS = None
MANAGERS = ADMINS

# Default database config places a sqlite db at ~/stars_default.db
# You can change the path of the sqlite db or use mysql or postgre...
DATABASES = {
    'default': {
        # 'NAME': '/Users/jamstooks/sqlite/stars_test.db',
        # 'ENGINE': 'sqlite3',
        'NAME': os.path.join(homedir, 'stars_default.db'),
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

# Media is served by django when using the dev server (bin/django runserver)
# but user uploads will be stored in the MEDIA_ROOT.
# you should probably change this to something other than ~/stars_media
MEDIA_ROOT = os.path.join(homedir, 'stars_media')

# Working with the LIVE IRC domain by default. Not all nodes exist in dev/stage.
IRC_DOMAIN = WWW_IRC_DOMAIN

# Change the server you authenticate with (see settings.py for variable definitions)
SSO_SERVER_URI = DEV_SSO_SERVER_URI
STARS_DOMAIN = DEV_STARS_DOMAIN
SSO_API_KEY = DEV_SSO_API_KEY

XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True

SOUTH_TESTS_MIGRATE = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/stars-cache',
    }
}
