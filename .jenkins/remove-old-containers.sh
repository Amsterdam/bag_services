#!/usr/bin/env bash

##
echo "clean up old dockers";
docker rm $(docker ps -qa);
echo "clean up completed";

echo "clean up old images";
docker rmi $(docker images -q);
echo "clean up images completed";

echo "clean up old volumes";
docker volume ls -qf dangling=true | xargs -r docker volume rm;
echo "clean up volumes completed";
