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
dc pull
dc build

echo "import new diva files into database"
dc run --rm importer

echo "Starting Elastic importers"
dc run --rm importer docker-index-es.sh

echo "Running backups"
dc run --rm db-backup
dc exec elasticsearch backup-indices.sh bag,brk,nummeraanduiding

echo "Done"
