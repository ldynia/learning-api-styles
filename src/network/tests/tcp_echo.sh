#!/usr/bin/env bash

set -Eeuo pipefail

function usage() {
  echo "Usage: ./$0 netcat|scapy|python|openssl"
}

WORK_DIR=$(basename $(pwd))
ROOT_DIR="network"
if [[ "$WORK_DIR" != "$ROOT_DIR" ]]; then
  echo "Error: Script must be run from the $ROOT_DIR directory"
  usage
  exit 1
fi

if [[ $# -ne 1 ]]; then
  echo "Error: Client type argument is required: netcat|scapy|python|openssl"
  usage
  exit 1
else
  CLIENT=$1
fi

if ! [[ "$CLIENT" =~ ^(netcat|scapy|python|openssl)$ ]]; then
  echo "Error: Incorrect client type: $CLIENT. Supported values: netcat|scapy|python|openssl"
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
# tag::setup_network[]
bash scripts/setup_network.sh   # <3>
# end::setup_network[]
# tag::test_client[]
bash tests/tcp_echo_client.sh $CLIENT
# end::test_client[]
