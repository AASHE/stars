# Python image to use.
FROM gcr.io/aashe-migration/stars-base-image:c8ce4dda-5de1-4e7d-8537-f7b974c1323d

# Set the working directory to /app
WORKDIR /app

# Make directories for django and celery
RUN mkdir -p /var/www/ \
    mkdir -p /var/www/stars \
    mkdir -p /var/www/stars/media \
    mkdir -p /var/www/stars/static \
    mkdir -p /var/www/stars/logs \
    mkdir -p /var/www/stars/src/

# Copy the rest of the working directory contents into the container at /app
COPY . . 

RUN chmod +x run-celery.sh

RUN chmod +x run-django.sh