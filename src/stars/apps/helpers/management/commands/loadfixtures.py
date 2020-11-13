import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db.models import get_apps

"""
    Given a list of prefixes, such as 'v0.5', this command will search for all
    matching fixtures within STARS and call loaddata to load the fixture to the DB.
    This is useful for:
     - initializing the DB with base data for a given credit set(s)
     - loading a suite of test fixtures for testing
"""
class Command(BaseCommand):
    help = 'Searches for and installs a suite of STARS fixture(s) in the database.'
    args = "[fixture_prefix fixture_prefix ...]"

    def handle(self, *fixture_prefix, **options):
        verbosity = int(options.get('verbosity', 1))
        
        if not fixture_prefix:  # load all version fixtures
            fixture_prefix = ('v',) # STARS creditset fixtures are all prefixed with a version number.
        for prefix in fixture_prefix:
            fixtures = _get_stars_fixtures(prefix, verbosity)
            for fixture in fixtures:
                call_command('loaddata', fixture, **options)

def _get_stars_fixtures(prefix, verbosity):
    """
    Returns a list of fixture files with the given prefix.

    This works by looking for a fixtures directory in each installed application 
    -- if it exists, all fixture files beginning with the given prefix are included.
    """    
    if not prefix:  
        return []
    fixtures = []
    
    app_fixtures = [os.path.join(os.path.abspath(os.path.dirname(app.__file__)), 'fixtures') for app in get_apps()]
    fixture_dirs = app_fixtures + list(settings.FIXTURE_DIRS) + ['']

    for fixture_dir in fixture_dirs:
        if fixture_dir.find('stars') == -1 or not os.path.exists(fixture_dir):
            continue
        
        if verbosity > 1:
            print "Looking for '%s' fixtures in %s..." % (prefix, fixture_dir)

        fixture_files = os.listdir(fixture_dir)
        for fixture_file in fixture_files:
            if fixture_file.startswith(prefix):
                if verbosity > 1:
                    print "Adding fixture %s..." % fixture_file
                fixtures.append(os.path.join(fixture_dir, fixture_file))
    return fixtures
