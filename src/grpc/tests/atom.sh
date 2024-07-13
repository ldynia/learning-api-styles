#!/usr/bin/env bash

set -Eeuo pipefail

function usage() {
  echo "Usage: ./$0 warmup|newsboat|django"
}

WORK_DIR=$(basename $(pwd))
ROOT_DIR="grpc"
if [[ "$WORK_DIR" != "$ROOT_DIR" ]]; then
  echo "Error: Script must be run from the $ROOT_DIR directory"
  usage
  exit 1
fi

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

if [[ $# -eq 1 ]]; then
  CLIENT=$1
fi

if ! [[ "$CLIENT" =~ ^(warmup|newsboat|django)$ ]]; then
  echo "Error: Incorrect CLIENT type: $CLIENT. Supported values: warmup|newsboat|django"
  usage
  exit 1
fi

echo "Executing: $0 $@"

# tag::teardown_containers[]
bash scripts/teardown_containers.sh
# end::teardown_containers[]
if [[ "$CLIENT" =~ ^(newsboat|django)$ ]];
then
# tag::teardown_django[]
(cd ../django && bash ../grpc/scripts/teardown_django.sh)
# end::teardown_django[]
fi

# tag::setup_containers[]
bash scripts/setup_containers.sh
# end::setup_containers[]
if [[ "$CLIENT" =~ ^(newsboat|django)$ ]];
then
# tag::setup_django[]
(cd ../django && bash ../grpc/scripts/setup_django.sh)
# end::setup_django[]
fi

# tag::test[]
bash tests/atom_client.sh $CLIENT
# end::test[]
