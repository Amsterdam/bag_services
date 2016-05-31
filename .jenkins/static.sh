#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -f ${DIR}/docker-compose.yml $*
}

trap 'dc kill ; dc rm -f' EXIT

dc build web-static
dc run --rm web-static

