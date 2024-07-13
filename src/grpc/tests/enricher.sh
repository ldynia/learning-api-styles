#!/usr/bin/env bash

set -Eeuo pipefail

function usage() {
  echo "Usage: ./$0 caching|basic_error_status|rich_error_status|deadline|reflection"
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
  BEHAVIOR=$1
fi

if ! [[ "$BEHAVIOR" =~ ^(caching|basic_error_status|rich_error_status|deadline|reflection)$ ]]; then
  echo "Error: Incorrect BEHAVIOR type: $BEHAVIOR. Supported values: caching|basic_error_status|rich_error_status|deadline|reflection"
  usage
  exit 1
fi

echo "Executing: $0 $@"

# tag::teardown_containers[]
bash scripts/teardown_containers.sh
# end::teardown_containers[]
# tag::setup_containers[]
bash scripts/setup_containers.sh  # <2>
# end::setup_containers[]
# tag::test[]
bash tests/enricher_behavior.sh $BEHAVIOR
# end::test[]
