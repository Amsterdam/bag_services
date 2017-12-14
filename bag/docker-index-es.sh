#!/usr/bin/env bash

set -u   # crash on missing environment variables
set -e   # stop on any error
set -x   # log every command.

source docker-wait.sh

# clear elasticindices
python manage.py elastic_indices --delete

python manage.py elastic_indices gebieden wkpb --build

python manage.py elastic_indices bag brk --partial=1/4 --build &
python manage.py elastic_indices bag brk --partial=2/4 --build &
python manage.py elastic_indices bag brk --partial=3/4 --build &
python manage.py elastic_indices bag brk --partial=4/4 --build


FAIL=0

for job in `jobs -p`
do
	echo $job
	wait $job || let "FAIL+=1"
done

echo $FAIL

if [ "$FAIL" == "0" ];
then
    echo "YAY!"
else
    echo "FAIL! ($FAIL)"
    echo 'Elastic Import Error. 1 or more workers failed'
    exit 1
fi
