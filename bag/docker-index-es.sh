#!/bin/bash
# Usage:
# ./es-indexing.sh <dataset> <nr of parts>
# es-indexing.sh gebieden 1
set -e

dataset=$1
parts=$2
retries=3
re='^[0-9]+$'
n=0

# loop over netcat to see open psql & eslastic established connection(s)
# source docker-wait.sh

function usage() {
    echo "ERROR: Missing or invalid arguments!"
    echo "Usage: $0 [dataset] [parts]"
    exit 0
}

function rm_index() {
    echo "Deleting elastic indexes!"
    python manage.py elastic_indices --delete
    exit 0
}


function run_index() {
  for num in $(seq 1 $parts); do
    until [ "$n" -ge "$retries" ]; do
      echo attempt: $((n+1))
      python manage.py elastic_indices $dataset --partial=$num/$parts --build && echo "Succes" && break || echo "failed"
      n=$((n+1))
      sleep 1s
    done
  done
}


# Check if the right number of arguments were passed
if [[ $1 == "delete" ]]; then
    rm_index
elif [[ "$#" -eq 2 ]]; then
  if [[ $2 == ?(-)+([0-9]) ]]; then
    run_index
  else
    usage
  fi
else
  usage
fi
