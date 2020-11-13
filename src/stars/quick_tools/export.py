#!/usr/bin/env python

from stars.apps.custom_forms.models import TAApplication
from stars.apps.institutions.models import RegistrationSurvey
from stars.apps.helpers.export import export_to_file

# export_to_file(TAApplication, 'ta_app.csv', media_prefix='http://stars.aashe.org/media/')

export_to_file(RegistrationSurvey, 'survey.csv')
