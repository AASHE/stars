"""
    Personal config file for development in Jesse's local environment.
"""

from settings import *

HIDE_REPORTING_TOOL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
TESTING=True

# no emails during local dev
ADMINS = ('jesse.legg@aashe.org',)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': 'stars_jesse',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
    }
}

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

MEDIA_ROOT = '/Users/src/jesse/stars-project/media/'

IRC_DOMAIN = WWW_IRC_DOMAIN

SSO_SERVER_URI = WWW_SSO_SERVER_URI
STARS_DOMAIN = WWW_STARS_DOMAIN
SSO_API_KEY = WWW_SSO_API_KEY

#AASHE_MYSQL_SERVER = "67.192.170.227"#"mysql.aashe.net" #"174.143.240.117"
AASHE_MYSQL_SERVER = "localhost"
AASHE_MYSQL_LOGIN = "root"
AASHE_MYSQL_PASS = ""

XMLRPC_VERBOSE = False
XMLRPC_USE_HASH = True

CYBERSOURCE_URL = CYBERSOURCE_TEST_URL

# #if manage.py test was called, use test settings
# if 'test' in sys.argv:
#     DATABASES['default']['ENGINE'] = 'sqlite3'
#     DATABASES['default']['NAME'] = '/Users/jesse/src/stars_tests.db'