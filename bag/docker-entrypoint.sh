#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

cd /app

source docker-wait.sh

echo Performing system check
python manage.py check

echo Performing migrations
yes yes | python manage.py migrate

echo Collecting static files
yes yes | python manage.py collectstatic

# run uwsgi
exec uwsgi --ini /app/uwsgi.ini
