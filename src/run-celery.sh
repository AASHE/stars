#!/bin/bash

#Start Celery Workers
celery -A stars --config src/stars/celery.py loglevel=DEBUG &

#Start Celery Beat
celery beat --config src/stars/celery.py -A stars -s /var/www/stars/logs/beat.db loglevel=DEBUG &