#!/bin/bash

echo "started"


# Migrate Django after each build
python manage.py migrate

echo "after migrate"

# Collect website static assets
python manage.py collectstatic --noinput

echo "after collectstatic"

python manage.py runserver 0.0.0.0:8080 --noreload

echo "after start django"