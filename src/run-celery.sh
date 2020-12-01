#!/bin/bash

#Start Celery Workers
celery -A stars worker --config stars/celery.py --loglevel=DEBUG &

#Start Celery Beat
celery beat --config stars/celery.py -A stars -s /var/www/stars/logs/beat.db --loglevel=DEBUG