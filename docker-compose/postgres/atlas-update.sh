#!/usr/bin/env bash

cd /tmp
rm -f atlas_latest.gz
wget https://admin:atlas123@admin.datapunt.amsterdam.nl/postgres/atlas_latest.gz /tmp/atlas_latest.gz
createuser -U postgres atlas
dropdb -U postgres atlas
pg_restore -C -d postgres -U postgres /tmp/atlas_latest.gz