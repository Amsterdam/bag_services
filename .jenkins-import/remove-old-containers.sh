#!/usr/bin/env bash

set -u
set -e

echo "clean up old dockers";
for container_id in $(docker ps -aq --filter status=exited);do docker rm $container_id;done
echo "clean up completed";

echo "clean up old images";
docker 2>/dev/null 1>&2 rmi -f `docker images -aq` || true
echo "clean up images completed";

echo "clean up old volumes";
docker volume ls -qf dangling=true | xargs -r docker volume rm;
echo "clean up volumes completed";
