1. Base playbook.yml runs all roles which include the entire build
2. common-role - install and update common packages
   1. sudo apt-get update
   2. sudo apt-get install openssl, libssl-dev, libssl-doc
   3. sudo apt-get install fail2ban
   4. sudo apt-get install ntp ntpdate
   5. sudo apt-get upgrade
3. aashe-users-role - create users on all servers
   1. Create all users contained in /vars/users.yml
   2. Add SSH keys to servers for users
4. mysql-server-role - create database servers
   1. sudo apt-get update
   2. Update mysql configuration
      - https://github.com/AASHE/mysql-server-role/blob/master/templates/my.cnf.j2
   1. Create Database
      1. dbname: "{{app_name}}"
      2. app_name: stars
   2. Create DB Users
      1. name={{dbuser}}
         - dbuser: stars
      2. password={{dbpass}}
         - dbpass = (Unsure how set)
      3. priv=*.*:ALL
      4. state=present
      5. host={{webserver_ip}}
         - webserver_ip: 127.0.0.1
      6. restart msql-server
5. django-gunicorn-supervisor - setup application servers
   1. **install_packages.yml**
      1. Install Packages
         1. sudo apt-get update
         2. sudo apt-get install binutils, build-essential, git, libncurses5-dev, libjpeg-dev, memcached, mercurial, nginx, python-dev, python-pip, supervisor
         3. (apt-specific packages) sudo apt-get install libffi-dev, libmysqlclient-dev, libmysqlclient20, libxml2-dev, libxslt1-dev, mysql-common, python-mysqldb, graphviz, build-essential, python-dev, python-pip, python-cffi, libcairo2, libpango-1.0-0, libpangocairo-1.0-0, libgdk-pixbuf2.0-0, libffi-dev, shared-mime-info
         4. (test packages) sudo apt-get install phantomjs
      2. pip install virtualenv
   2. **create_users_groups.yml** - create application users
      1. Create app user
         - name={{ app_user }}
         - app_user: "{{ app_name }}"
         - app_name: stars
      2. Create app group
         - app_group: webapps
      3. Add user to group
   3. **releaser_keys.yml** (setup keys for git access for code)
   4. **create_paths.yml** (create all directories, mode 0775 with owner as stars:webapps)
      1. Create directories
         - mkdir -p /var/www/
         - mkdir -p /var/www/stars/
         - mkdir -p /var/www/stars/media/
         - mkdir -p /var/www/stars/static/
         - mkdir -p /var/www/stars/logs/
      2. Create src directory (for non local builds)
         - mkdir -p /var/www/stars/src/
   5. **get_source.yml** (Get Source code and save to /var/www/stars/src/)
      - repo: "git@github.com:AASHE/stars.git"
      - branch: master
   6. **newrelic.yml** (Install newrelic)
      1. pip install newrelic (into virtualenv)
      2. Update newrelic ini file
         1. https://github.com/AASHE/django-gunicorn-supervisor/blob/master/templates/newrelic.ini.j2
   7. **setup_virtualenv.yml** - create python virtual environment
      - Check if venv exists
      - Ensure path exists
      - Create venv for django
      - Run postactivate script
        - https://github.com/AASHE/django-gunicorn-supervisor/blob/master/templates/postactivate.j2
        - This sets environment variables
      - pip install
        - pip install pip==19.1.1
        - pip install ndg-httpsclient
        - pip install pyasn1
        - pip install pyopenssl==19.0.0
        - pip install -r /var/www/stars/src/requirements.txt
      - pip install (dev packages)
        - pip install -r /var/www/stars/src/requirements_dev.txt
      - pip install (test packages)
        - pip install -r /var/www/stars/src/requirements_test.txt
    8. **config_django_app.yml** - Configures the web application, and collects static assets
       1. fake the djcelery migration
          - sudo python3 manage.py migrate --fake djcelery --noinput
       2. django migrate
          - sudo python3 manage.py migrate
       3. django collectstatic
    9. **config_ssl.yml**
       1. create ssl directory
          - mkdir -p /etc/nginx/ssl
       2. create ssl crt (mode 0664 with owner as stars:webapps)
          - /etc/nginx/ssl/local_stars.crt
       3. create ssl key (mode 0664 with owner as stars:webapps)
          - /etc/nginx/ssl/local_stars.key
       4. Restart nginx
    10. **config_nginx.yml**
        1. create nginx config file in /etc/nginx/sites-enabled/stars.conf
          - template: https://github.com/AASHE/django-gunicorn-supervisor/blob/master/templates/nginx.ssl.conf.j2
        2. Delete default symbolic linked website on nginx
          - sudo rm /etc/nginx-sites-enabled/default
        3. Write supervisor configuration to /etc/supervisor/conf.d/stars.conf **this task sets up Gunicorn**
          - template: https://github.com/AASHE/django-gunicorn-supervisor/blob/master/templates/supervisor.conf.j2
        4. Start supervisor service
        5. re-read the supervisor config file
          - cmd: supervisorctl reread
        6. Update Supervisor to add the app in the process group - sudo supervisorctl update
          - restart nginx
6. django-celery-rabbitmq - deploy django, rabbitmq, celery (app servers only)
   1. **main.yml** - runs **install_packages.yml** and **celery_init.yml**
   2. **install_packages.yml**
      1. sudo apt-get update
      2. sudo apt-get install rabbitmq-server
   3. **celery_init.yml** - Configuration for celery init scripts
      1. Write celery supervisor config to /etc/supervisor/conf.d/stars-celery.conf
        - template: https://github.com/AASHE/django-celery-rabbitmq/blob/master/templates/celeryd.conf.j2
        - start supervisor service (celery)
        - reload supervisor (celery)
        - restart worker
      2. Write celery beat supervisor config to /etc/supervisor/conf.d/stars-beat.conf
        - template: https://github.com/AASHE/django-celery-rabbitmq/blob/master/templates/celerybeat.conf.j2
        - reload supervisor (celery)
        - restart worker