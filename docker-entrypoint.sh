#!/bin/bash
set -e

# Migrate
pipenv run python /srv/src/manage.py migrate --settings ccvs.settings.production
# Collectstatic
pipenv run python /srv/src/manage.py collectstatic --noinput --settings=ccvs.settings.production

touch /srv/logs/gunicorn.log
touch /srv/logs/access.log
touch /var/log/nginx/error.log
ln -s /var/log/nginx/error.log /srv/logs/nginx.log
tail -n 0 -f /srv/logs/*.log &

# Start Gunicorn processes
echo Starting Gunicorn.
echo Starting nginx
exec pipenv run gunicorn \
    --env DJANGO_SETTINGS_MODULE=ccvs.settings.production \
    --name ccvs \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout=600 \
    --log-level=info \
    --log-file=/srv/logs/gunicorn.log \
    --access-logfile=/srv/logs/access.log \
    ccvs.wsgi:application &
exec service nginx start
