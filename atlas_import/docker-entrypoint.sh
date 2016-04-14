#!/usr/bin/env bash

set -e
set -u

PYTHON=$(which python3 || which python)

echo Performing system check
${PYTHON} manage.py check

${PYTHON} manage.py remove_materialize_views

echo Performing migrations
yes yes | ${PYTHON} manage.py migrate

${PYTHON} manage.py create_geo_tables

echo Starting server
uwsgi --ini uwsgi.ini
