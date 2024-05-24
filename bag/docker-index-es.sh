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

function usage() {
    echo "ERROR: Missing or invalid arguments!"
    echo "Usage: $0 [dataset] [parts]"
    exit 0
}

function run_index() {
  for num in $(seq 1 $parts); do
    until [ "$n" -ge "$retries" ]; do
      echo attempt: $n
      python manage.py elastic_indices $dataset --partial=$num/$parts --build && echo "Succes" && break || echo "failed"
      n=$((n+1))
      sleep 1s
    done
  done
}


# Check if the right number of arguments were passed
if [[ "$#" -eq 2 ]]; then
  if [[ $2 == ?(-)+([0-9]) ]]; then
    run_index
  else
    usage
  fi
else
  usage
fi

exit 0
