#!/usr/bin/env bash

set -Eeuo pipefail

function usage() {
  echo "Usage: ./$0 warmup|newsboat|django"
}

get_network_information () {
  # From the $1 container, get the interface name or IP address on the $2 network
  local mode=$1
  local service_name=$2
  local network_name=$3
  local container_id=$(docker compose ps -q "${service_name}")
  local network_info=$(docker inspect "${container_id}")
  local mac_address=$(echo "${network_info}" | jq -r ".[0].NetworkSettings.Networks.${network_name}.MacAddress")
  local ip_address=$(echo "${network_info}" | jq -r ".[0].NetworkSettings.Networks.${network_name}.IPAddress")
  local interfaces=$(docker compose exec -t "${service_name}" ip a)
  local interface_name=$(echo "${interfaces}" | grep -a1 "${mac_address}" | tail -1 | rev | cut -d' ' -f1 | rev | xargs)
  if [[ "${mode}" == "interface" ]];
  then
    echo "${interface_name}"
  fi
  if [[ "${mode}" == "ip" ]];
  then
    echo "${ip_address}"
  fi
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

# Start with clean SSLKEYLOGFILE
docker compose exec client bash -c "echo > tests/SSLKEYLOGFILE.client"

screen -ls || true
LOGFILE_SERVER=tests/atom_client_${CLIENT}_server.log
echo > ${LOGFILE_SERVER}
docker compose exec server bash -c 'kill $(pgrep --full "python src/enricher/enricher/server.py")' || true
function docker () {
  screen -L -Logfile ${LOGFILE_SERVER} -S server -d -m docker "$@"
}
# tag::start_server[]
docker compose exec server bash -ci \
       "PYTHONPATH=./src/enricher python src/enricher/enricher/server.py"
# end::start_server[]
unset docker
sleep 3

screen -ls || true
LOGFILE_TCPDUMP=tests/atom_client_${CLIENT}_tcpdump.log
echo > ${LOGFILE_TCPDUMP}
docker compose exec client bash -c 'sudo kill $(pgrep --full "sudo tcpdump")' || true
# tag::client_flush_arp_cache[]
docker compose exec client bash -c "sudo ip neigh flush all"
# end::client_flush_arp_cache[]
# Determine the network interface to be used by tcpdump
if [[ "$CLIENT" =~ ^(warmup)$ ]];
then
NETWORK_NAME=grpc_internal
fi
if [[ "$CLIENT" =~ ^(newsboat|django)$ ]];
then
NETWORK_NAME=django_shared
fi
CLIENT_INTERFACE_NAME=$(get_network_information interface "client" "${NETWORK_NAME}")
SERVER_IP_ADDRESS=$(get_network_information ip "server" "${NETWORK_NAME}")
echo "client will access server '${SERVER_IP_ADDRESS}' on network '${NETWORK_NAME}' using interface '${CLIENT_INTERFACE_NAME}'"
function docker () {
  screen -L -Logfile ${LOGFILE_TCPDUMP} -S tcpdump -d -m docker "$@"
}
if [[ "$CLIENT" =~ ^(warmup)$ ]];
then
# tag::start_client_warmup_tcpdump[]
docker compose exec client bash -c \
       "sudo tcpdump --interface ${CLIENT_INTERFACE_NAME} -w /tmp/atom_client_${CLIENT}.pcap 'port 50051' && \
       cp /tmp/atom_client_${CLIENT}.pcap tests"
# end::start_client_warmup_tcpdump[]
fi
if [[ "$CLIENT" =~ ^(newsboat|django)$ ]];
then
# tag::start_client_newsboat_tcpdump[]
docker compose exec client bash -c \
       "sudo tcpdump --interface ${CLIENT_INTERFACE_NAME} -w /tmp/atom_client_${CLIENT}.pcap 'port 8000' && \
       cp /tmp/atom_client_${CLIENT}.pcap tests"
# end::start_client_newsboat_tcpdump[]
fi
unset docker
sleep 3

screen -ls || true
if [[ "$CLIENT" =~ ^(warmup)$ ]];
then
# Warm-up run downloads the model
TEMP_STDERR_FILE=$(mktemp)
WARMUP_START=$(date +%s)
docker compose exec client grpcurl -plaintext \
       -d '{"weather_forecast": {"city": {"name": "warmup"}}}' \
       ${SERVER_IP_ADDRESS}:50051 enricher.v1.EnricherService/Enrich > "$TEMP_STDERR_FILE" 2>&1 || true
WARMUP_END=$(date +%s)
WARMUP_STDERR=$(<"$TEMP_STDERR_FILE")
echo "${WARMUP_STDERR}"
WARMUP_ELAPSED=$((WARMUP_END - WARMUP_START))
echo "WARMUP took ${WARMUP_ELAPSED} seconds"
fi
if [[ "$CLIENT" =~ ^(newsboat)$ ]];
then
# tag::start_client_newsboat_configure[]
docker compose exec client bash -c \
       "mkdir --parents ~/.newsboat && \
       echo 'download-timeout 600' > ~/.newsboat/config && \
       echo http://app:8000/forecast/feed_enriched > ~/.newsboat/urls"
# end::start_client_newsboat_configure[]
TEMP_STDERR_FILE=$(mktemp)
# tag::start_client_newsboat_run[]
docker compose exec client bash -c \
       "newsboat --refresh-on-start --execute='reload' --execute='print-unread'" > \
       "$TEMP_STDERR_FILE" 2>&1 || true
# end::start_client_newsboat_run[]
NEWSBOAT_CLIENT_STDERR=$(<"$TEMP_STDERR_FILE")
echo "${NEWSBOAT_CLIENT_STDERR}"
# end::start_client_newsboat[]
fi
if [[ "$CLIENT" =~ ^(django)$ ]];
then
pushd ../django
# tag::start_client_newsboat_django_configure[]
docker compose exec app bash -c \
       "mkdir --parents ~/.newsboat && \
       echo 'download-timeout 600' > ~/.newsboat/config && \
       echo http://app:8000/forecast/feed_enriched > ~/.newsboat/urls"
# end::start_client_newsboat_django_configure[]
TEMP_STDERR_FILE=$(mktemp)
# tag::start_client_newsboat_django_run[]
docker compose exec app bash -c \
       "newsboat --refresh-on-start --execute='reload' --execute='print-unread'" > \
       "$TEMP_STDERR_FILE" 2>&1 || true
# end::start_client_newsboat_django_run[]
NEWSBOAT_DJANGO_STDERR=$(<"$TEMP_STDERR_FILE")
echo "${NEWSBOAT_DJANGO_STDERR}"
popd
# end::start_client_newsboat_django[]
fi
sleep 3

echo

# stop tcpdump, by sending SIGINT (ctrl+c)
docker compose exec client bash -c 'sudo kill -SIGINT $(pgrep --full "sudo tcpdump")' || true
screen -X -S "tcpdump" quit
screen -ls || true

# stop server
screen -X -S "server" quit
screen -ls || true

# cat captured screen output
echo "cat ${LOGFILE_SERVER}" && cat ${LOGFILE_SERVER}
echo "cat ${LOGFILE_TCPDUMP}" && cat ${LOGFILE_TCPDUMP}

# test the created pcap
echo "Test pcap can be read"
PCAP="tests/atom_client_${CLIENT}.pcap"
if [[ ! "$CLIENT" =~ ^(django)$ ]];
then
# tag::tshark_read_atom_client[]
docker compose exec client bash -c "tshark --read-file tests/atom_client_${CLIENT}.pcap"
# end::tshark_read_atom_client[]
fi
echo
if [[ "$CLIENT" =~ ^(warmup)$ ]];
then
  echo "Warmup succeeds"
  echo "${WARMUP_STDERR}" | grep --quiet "Language Model says"
fi
if [[ "$CLIENT" =~ ^(newsboat)$ ]];
then
  echo "Newsboat client reads articles"
  echo "${NEWSBOAT_CLIENT_STDERR}" | grep --quiet "6 unread articles"
fi
if [[ "$CLIENT" =~ ^(django)$ ]];
then
  echo "Newsboat django reads articles"
  echo "${NEWSBOAT_DJANGO_STDERR}" | grep --quiet "6 unread articles"
fi
