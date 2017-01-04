#!/usr/bin/env bash

set -u
set -e

echo "clean up old dockers";
for container_id in $(docker ps -a --filter status=exited -q);do docker rm $container_id;done
echo "clean up completed";

echo "clean up old images";
docker rmi $(docker images -q);
echo "clean up images completed";

echo "clean up old volumes";
docker volume ls -qf dangling=true | xargs -r docker volume rm;
echo "clean up volumes completed";
