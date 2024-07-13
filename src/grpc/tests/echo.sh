#!/usr/bin/env bash

set -Eeuo pipefail

function usage() {
  echo "Usage: ./$0 unary|server_streaming|client_streaming|bidirectional_streaming insecure|mtls"
}

WORK_DIR=$(basename $(pwd))
ROOT_DIR="grpc"
if [[ "$WORK_DIR" != "$ROOT_DIR" ]]; then
  echo "Error: Script must be run from the $ROOT_DIR directory"
  usage
  exit 1
fi

if [[ $# -ne 2 ]]; then
  usage
  exit 1
fi

if [[ $# -eq 2 ]]; then
  RPC=$1
  SECURITY=$2
fi

if ! [[ "$RPC" =~ ^(unary|server_streaming|client_streaming|bidirectional_streaming)$ ]]; then
  echo "Error: Incorrect RPC type: $RPC. Supported values: unary|server_streaming|client_streaming|bidirectional_streaming"
  usage
  exit 1
fi

if ! [[ "$SECURITY" =~ ^(insecure|mtls)$ ]]; then
  echo "Error: Incorrect $SECURITY setting. Supported values: insecure|mtls"
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
bash tests/echo_rpc.sh $RPC $SECURITY
# end::test[]
