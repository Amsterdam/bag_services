#!/usr/bin/env bash

set -u   # crash on missing environment variables
set -e   # stop on any error
set -x   # log every command.


while getopts "g" arg; do
  case $arg in
    g)
      GOB_PARAMETER="-g"
      ;;
    \?)
      echo "WRONG" >&2
      ;;
  esac
done

GOB_PARAMETER=${GOB_PARAMETER:-""}

source docker-wait.sh

# download csv
python objectstore/objectstore.py ${GOB_PARAMETER}

# load data in database
python manage.py migrate
python manage.py flush --noinput
python manage.py run_import ${GOB_PARAMETER}
python manage.py run_import --validate ${GOB_PARAMETER}
