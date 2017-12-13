#!/usr/bin/env bash

set -u
set -e
set -x

echo 0.0.0.0:5432:bag:bag:insecure > ~/.pgpass
chmod 600 ~/.pgpass

pg_dump   --clean \
	  -Fc \
	  -t bag* \
	  -t brk* \
	  -t wkpb* \
	  -t geo*  \
	  -t django_*  \
	  -U bag \
	  -h 0.0.0.0 -p 5432 \
	  bag > /tmp/backups/database.dump


