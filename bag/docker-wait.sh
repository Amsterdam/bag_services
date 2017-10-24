#!/usr/bin/env bash

set -u
set -e

# wait for elastic
while ! nc -z ${ELASTICSEARCH_PORT_9200_TCP_ADDR} ${ELASTICSEARCH_PORT_9200_TCP_PORT}
do
	echo "Waiting for elastic..."
	sleep 2
done

# wait for postgres
while ! nc -z ${DATABASE_HOST_OVERRIDE} ${DATABASE_PORT_OVERRIDE}
do
	echo "Waiting for postgres..."
	sleep 2
done
