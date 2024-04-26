#!/usr/bin/env bash

set -u   # crash on missing environment variables
set -e   # stop on any error
set -x   # log every command.

# clear elasticindices and creates empty ones
# It seems that this step is essential to get the correct mapping
# for the indexes!
python manage.py elastic_indices --delete

python manage.py elastic_indices gebieden pand --build

python manage.py elastic_indices bag --partial=1/3 --build 
python manage.py elastic_indices bag --partial=2/3 --build 
python manage.py elastic_indices bag --partial=3/3 --build 
python manage.py elastic_indices brk --partial=1/3 --build 
python manage.py elastic_indices brk --partial=2/3 --build 
python manage.py elastic_indices brk --partial=3/3 --build 
