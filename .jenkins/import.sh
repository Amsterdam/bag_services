#!/bin/sh

set -e
set -u

DIR="$(dirname $0)"

dc() {
	docker-compose -f ${DIR}/docker-compose.yml $*;
}

# wait_for_containers checks every 15 seconds whether a given container is done
# running, and if so, whether it has finished with an exit code other than 0. If
# it has, then it will return with the exit code. Note that if one container
# exits non-zero, other containers may still be running.
wait_for_containers() {
  containers="$@"
  echo "Monitoring containers: ${containers}"
  still_running=""
  while [ 0 -ne "${#containers}" ]; do
    for container in ${containers}; do
      if [ "false" = "$( docker inspect -f {{.State.Running}} $container )" ]; then
        exit_code="$( docker inspect -f {{.State.ExitCode}} $container )"
        if [ "0" != "${exit_code}" ]; then
          echo "$container failed with ${exit_code}"
          return $exit_code
        fi
        echo "${container} has finished"
      else
        still_running="${still_running} ${container}"
      fi
    done
    containers=$still_running
    still_running=""
    if [ 0 -ne "${#containers}" ]; then
      sleep 15
    fi
  done
  return 0
}

trap 'dc kill ; dc rm -f' EXIT

rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc build
# import new diva files in database
dc run --rm importer
# create the new elastic indexes
dc up importer_el1 importer_el2 importer_el3
# wait until all building is done
wait_for_containers jenkins_importer_el1_1 jenkins_importer_el2_1 jenkins_importer_el3_1 || \
  dc down && exit 1

# run backups
dc run --rm db-backup
dc run --rm el-backup

# You are awesome and done! <3
