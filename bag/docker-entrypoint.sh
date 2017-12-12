#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

echo Performing system check
python manage.py check

echo Collecting static files
yes yes | python manage.py collectstatic

ls -al /static/

chmod -R 777 /static

# run uwsgi
exec uwsgi

