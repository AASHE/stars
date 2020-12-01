#!/bin/bash

# Migrate Django after each build
python manage.py migrate

# Collect website static assets
python manage.py collectstatic --noinput

# Start Django
python manage.py runserver 0.0.0.0:8080 --noreload

