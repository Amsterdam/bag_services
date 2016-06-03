#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -f ${DIR}/docker-compose.yml $*;
}

#trap 'dc kill ; dc rm -f' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

#dc build
#dc run --rm importer_pg
#dc run --rm importer_el1
#sleep 10
#dc run --rm importer_el2
#dc run --rm importer_el3
#dc run --rm db-backup
#dc run --rm el-backup

dc build
#dc run importer_pg
dc up -d importer_el1 importer_el2 importer_el3
docker wait jenkins_importer_el1_1 jenkins_importer_el2_1 jenkins_importer_el3_1

dc run db-backup
dc run el-backup

