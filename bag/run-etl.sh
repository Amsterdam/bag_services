#!/usr/bin/env bash

# Script for running the complete ETL process using data from the reference database.
# The data resulting from this process is served through the REST API
# included in this repository.  
#
# The process entails:
#   - loading data from the reference database into a separate schema (e.g. bag_v11)
#   - using the loaded data to create/update the indices in Elasticsearch
#
# TODO: Note that currently this will incur downtime since we are truncating and writing
# directly to the target databases.

FILENAME=$(realpath $0) 
CURDIR=${FILENAME%/*} 

dboptions="--host $DATABASE_HOST_OVERRIDE --user $DATABASE_USER --password $(cat $DATABASE_PW_LOCATION) --database $DATABASE_NAME"

echo 'Truncating legacy schema tables'
$CURDIR/ref-db/cli.py --delete $dboptions
echo 'Running data transfer from refdb to legacy schema'
$CURDIR/ref-db/cli.py --execute $dboptions

echo 'Running denormalization task'
$CURDIR/manage.py run_import --task-filter denormalize_vbo_standplaats_ligplaats

echo 'Deleting Elasticsearch indices'
$CURDIR/manage.py elastic_indices --delete
echo 'Starting Elasticsearch indexing'
$CURDIR/manage.py elastic_indices --build

echo 'ETL process successful'