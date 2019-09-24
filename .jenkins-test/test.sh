#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
	docker-compose -p bag-v11-test -f ${DIR}/docker-compose.yml $*
}

dc stop
dc rm --force
dc down
dc pull
dc build

dc up -d database
dc up -d elasticsearch

dc run --rm tests

dc stop
dc rm --force
dc down
