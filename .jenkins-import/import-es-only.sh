#!/bin/bash

set -e  # crash on all errors
set -u  # crash on missing environment variables
set -x  # print all commands

DIR="$(dirname $0)"

dc() {
	docker-compose -p bag -f ${DIR}/docker-compose.yml $*;
}

trap 'dc kill ; dc rm -f' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

echo "Building dockers"
#dc down
#dc pull
#dc build

dc up -d database
dc up -d elasticsearch
dc run importer ./docker-wait.sh

# restore database bag backup.
#docker-compose -p bag exec -T database update-db.sh bag_v11 spreeker
dc exec -T database update-db.sh bag_v11

echo "Starting Elastic importer"
dc run --rm importer ./docker-index-es.sh

echo "Make es backup"
dc exec -T elasticsearch backup-indices.sh bag bag*,brk*,nummeraanduiding

echo "Done"
