from settings import *

HIDE_REPORTING_TOOL = False
DEBUG = True

# no emails during local dev
ADMINS = ()
MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '/Users/jamstooks/sqlite/stars.db'

# Stand alone mode indicates that the server will be running using
# the django dev server so we will need to serve the static files (see urls.py)
STANDALONE_MODE = True

MEDIA_ROOT = '/Users/jamstooks/aashe/STARS/src/media/stars/'

SSO_SERVER_URI = WWW_SSO_SERVER_URI
STARS_DOMAIN = DEV_STARS_DOMAIN
SSO_API_KEY = DEV_SSO_API_KEY

AASHE_MYSQL_SERVER = "67.192.170.227"

CYBERSOURCE_URL = CYBERSOURCE_TEST_URL
