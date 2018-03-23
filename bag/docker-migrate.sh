#!/usr/bin/env bash

set -u   # crash on missing environment variables
set -e   # stop on any error
set -x

yes yes | python manage.py migrate --verbosity 3
