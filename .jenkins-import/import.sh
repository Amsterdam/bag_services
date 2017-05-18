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
dc build

echo "import new diva files into database"
dc run --rm importer

echo "Starting Elastic importers"
dc up -d importer_el1 importer_el2 importer_el3

echo "Waiting for importers to complete"
import_status=$(docker wait jenkinsimport_importer_el1_1 jenkinsimport_importer_el2_1 jenkinsimport_importer_el3_1)
[[ "$import_status" == *"1"* ]] && echo "Elastic Import Error. 1 or more workers failed" && exit 1

echo "Running backups"
dc run --rm db-backup
dc run --rm el-backup

echo "Done"

