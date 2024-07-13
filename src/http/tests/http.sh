#!/usr/bin/env bash

set -Eeuo pipefail

function usage() {
  echo "Usage: ./$0 http0.9|http1.0|http1.1|h2c|h2|http3|firefox|iperf|tcp|tls"
}

WORK_DIR=$(basename $(pwd))
ROOT_DIR="http"
if [[ "$WORK_DIR" != "$ROOT_DIR" ]]; then
  echo "Error: Script must be run from the $ROOT_DIR directory"
  usage
  exit 1
fi

if [[ $# -ne 1 ]]; then
  echo "Error: Client argument is required: http0.9|http1.0|http1.1|h2c|h2|http3|firefox|iperf|tcp|tls"
  usage
  exit 1
else
  CLIENT=$1
fi

if ! [[ "$CLIENT" =~ ^(http0.9|http1.0|http1.1|h2c|h2|http3|firefox|iperf|tcp|tls)$ ]]; then
  echo "Error: Incorrect client: $CLIENT. Supported values: http0.9|http1.0|http1.1|h2c|h2|http3|firefox|iperf|tcp|tls"
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
# tag::test_client[]
bash tests/client.sh $CLIENT
# end::test_client[]
