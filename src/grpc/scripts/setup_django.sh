#!/usr/bin/env bash

set -Eeuo pipefail

WORK_DIR=$(basename $(pwd))
ROOT_DIR="django"
if [[ "$WORK_DIR" != "$ROOT_DIR" ]]; then
  echo "Error: Script must be run from the $ROOT_DIR directory"
  exit 1
fi

echo "Executing: $0"

docker compose version

export BUILDKIT_PROGRESS=plain
# tag::build_container_images[]
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
# end::build_container_images[]

# tag::start_containers[]
docker compose up --detach --wait
# end::start_containers[]

docker ps

id && pwd && ls -al
docker compose exec app bash -c "id && pwd && ls -al"
