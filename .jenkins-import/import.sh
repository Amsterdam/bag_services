#!/bin/bash

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -p bag -f ${DIR}/docker-compose.yml $*;
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
dc exec -T database backup-db.sh bag
dc exec -T elasticsearch backup-indices.sh bag bag*,brk*,nummeraanduiding

echo "Done"
