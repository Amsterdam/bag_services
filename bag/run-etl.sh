#!/usr/bin/env bash
# This script is used on Azure to recreate the legacy databases.

# Script for running the complete ETL process using data from the reference database.
# The data resulting from this process is served through the REST API
# included in this repository.  
#
# The process entails:
#   - loading data from the reference database into a separate schema (e.g. bag_v11)
#   - running a subset of tasks from the GOB import logic to complete the dataset
#   - using the loaded data to create/update the indices in Elasticsearch
#
# TODO: Note that currently this will incur downtime since we are truncating and writing
# directly to the target databases.

set -e

FILENAME=$(realpath $0) 
CURDIR=${FILENAME%/*} 

dboptions="$DATABASE_SCHEMA\
 --host $DATABASE_HOST_OVERRIDE\
 --user $DATABASE_USER\
 --password $(cat $DATABASE_PW_LOCATION)\
 --database $DATABASE_NAME\
 --source-schema $1\
 --target-schema $2"

echo 'Truncating legacy schema tables'
$CURDIR/ref-db/cli.py --delete $dboptions
echo 'Running data transfer from refdb to legacy schema'
$CURDIR/ref-db/cli.py --execute $dboptions

echo 'Running eigendommen creation task'
$CURDIR/manage.py run_import --task-filter create_eigendommen_tables

echo 'Running denormalization task'
$CURDIR/manage.py run_import --task-filter denormalize_vbo_standplaats_ligplaats

echo 'Deleting Elasticsearch indices'
$CURDIR/manage.py elastic_indices --delete
echo 'Starting Elasticsearch indexing'
$CURDIR/manage.py elastic_indices --build

echo 'ETL process successful'