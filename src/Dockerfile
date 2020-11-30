# Python image to use.
FROM gcr.io/aashe-migration/stars-base-image:a0bfd050-d8e4-4ac1-868c-434b4739f306

RUN apt-get update
RUN apt-get install \
    libpangocairo-1.0-0 \
    -y

# Set the working directory to /app
WORKDIR /app

# copy the requirements file used for dependencies
#COPY requirements.txt .

# Install any needed packages specified in requirements.txt
#RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make directory for celery beat
RUN mkdir -p /var/www/stars/logs

# Copy the rest of the working directory contents into the container at /app
COPY . .

RUN chmod +x run-celery.sh

# Migrate Django after each build
RUN python manage.py migrate

# Collect website static assets
RUN django collectstatic

# Start the server when the container launches
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8080", "--noreload"]
