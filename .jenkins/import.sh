#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -f ${DIR}/docker-compose.yml $*;
}

trap 'dc kill ; dc rm -f' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

#dc build
#dc run --rm importer_pg
#dc up importer_bag1 importer_bag2 importer_bag3
#dc up importer_brk1 importer_brk2 importer_brk3
#dc run --rm db-backup
#dc run --rm el-backup


dc build
# import new diva files in database
dc run --rm importer
# create the new elastic indexes
dc up importer_el1 importer_el2 importer_el3
# waint until all building is done
docker wait jenkins_importer_el1_1 jenkins_importer_el2_1 jenkins_importer_el3_1

# run the backup shizzle
dc run --rm db-backup
dc run --rm el-backup

# Youare awsome and done! <3
