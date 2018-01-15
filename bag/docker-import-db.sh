#!/usr/bin/env bash

set -u   # crash on missing environment variables
set -e   # stop on any error
set -x   # log every command.

source docker-wait.sh

# download csv
python objectstore/objectstore.py

# load data in database
python manage.py migrate
python manage.py flush --noinput
python manage.py run_import
python manage.py run_import --validate
