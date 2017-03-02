#!/usr/bin/env bash

set -u   # crash on missing environment variables
set -e   # stop on any error

yes yes | python manage.py create_geo_tables
yes yes | python manage.py migrate --verbosity 3