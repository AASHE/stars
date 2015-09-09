from __future__ import absolute_import

import os

from celery import Celery
from celery.utils.log import get_task_logger

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stars.settings')

from django.conf import settings
from django.core.management import call_command

app = Celery('stars')
logger = get_task_logger(__name__)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task(name='tasks.beacon')
def beacon():
    print("BEATING!")


@app.task(name='tasks.run_cleanup')
def run_cleanup():
    print "running cleanup task"
    call_command('cleanup')