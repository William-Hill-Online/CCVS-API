#!/bin/bash
set -e

# Collectstatic
pipenv run python /app/src/manage.py collectstatic --noinput --settings=ccvs.settings.production

# Migrate
pipenv run python /app/src/manage.py migrate --settings ccvs.settings.production

# Webserver
pipenv run uwsgi --ini /app/src/ccvs/uwsgi.ini --env DJANGO_SETTINGS_MODULE=ccvs.settings.production
