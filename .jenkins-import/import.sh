#!/bin/bash

set -e  # crash on all errors
set -u  # crash on missing environment variables
set -x  # print all commands

DIR="$(dirname $0)"

dc() {
	docker-compose -p bag_v11 -f ${DIR}/docker-compose.yml $*;
}

trap 'dc kill ; dc rm -f' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

echo "Building dockers"
dc down
dc pull
dc build

dc up -d database
dc up -d elasticsearch
dc run importer ./docker-wait.sh

echo "import new diva files into database"
dc run --rm importer

echo "Starting Elastic importer"
dc run --rm importer ./docker-index-es.sh

echo "Running backups"
dc exec -T database backup-db.sh bag_v11
dc exec -T elasticsearch backup-indices.sh bag_v11 bag_v11*,brk_v11*,v11_nummeraanduiding

echo "Done"
