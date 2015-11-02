#!/usr/bin/env bash

set -e
set -u

PYTHON=$(which python3 || which python)

echo Performing system check
${PYTHON} manage.py check

echo Performing migrations
yes yes | ${PYTHON} manage.py migrate

echo Starting server
uwsgi --ini uwsgi.ini
