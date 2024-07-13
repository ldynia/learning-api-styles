#!/usr/bin/env bash

set -Eeuo pipefail

WORK_DIR=$(basename $(pwd))
ROOT_DIR="grpc"
if [[ "$WORK_DIR" != "$ROOT_DIR" ]]; then
  echo "Error: Script must be run from the $ROOT_DIR directory"
  exit 1
fi

echo "Executing: $0"

# tag::teardown_containers[]
BUILDKIT_PROGRESS=plain docker compose down --volumes
# end::teardown_containers[]
