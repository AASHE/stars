# Django project settings loader
# Note: systems don't have to use this file to get the local settings
# apache calls /config/[env].py explicitly

import os
import re
import sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

ALLOWED_HOSTS = ('*',)

# if there is a "local.py" file then use that
if os.path.exists(os.path.join(ROOT_PATH, "config/local.py")):
    config = "local"
else:
    # any environment can have its own configuration file
    config = os.environ.get("CONFIG", None)

    # if it's not set in an environment variable you can
    # key the configurations off of project path (can have regular expression)
    # in this case it's path, but you could use computer name or something else
    if not config:
        configs = {
            '/Users/rerb/src/.*': 'bob',
            '/Users/rerb/.*': 'bob',
            '/Users/tylor/src/.*': 'bob',
        }

        # find the first key that matches the ROOT_PATH
        config = 'settings'
        for k in configs.keys():
            m = re.match("(%s)" % k, ROOT_PATH)
            if m:
                config = configs[k]
                break

print >> sys.stderr, "USING CONFIG: %s" % config

# Import the configuration settings file
config_module = __import__('config.%s' % config, globals(), locals(), 'stars')

# Load the config settings properties into the local scope.
for setting in dir(config_module):
    if setting == setting.upper():
        locals()[setting] = getattr(config_module, setting)
