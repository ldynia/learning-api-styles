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

# Start with clean SSLKEYLOGFILE
docker compose exec client bash -c "echo > tests/SSLKEYLOGFILE.client"

screen -ls || true
LOGFILE_SERVER=tests/enricher_behavior_${BEHAVIOR}_server.log
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
LOGFILE_TCPDUMP=tests/enricher_behavior_${BEHAVIOR}_tcpdump.log
echo > ${LOGFILE_TCPDUMP}
docker compose exec client bash -c 'sudo kill $(pgrep --full "sudo tcpdump")' || true
# tag::client_flush_arp_cache[]
docker compose exec client bash -c "sudo ip neigh flush all"
# end::client_flush_arp_cache[]
function docker () {
  screen -L -Logfile ${LOGFILE_TCPDUMP} -S tcpdump -d -m docker "$@"
}
# tag::start_client_tcpdump[]
docker compose exec client bash -c \
       "sudo tcpdump -w /tmp/enricher_behavior_${BEHAVIOR}.pcap 'port 50051' && \
       cp /tmp/enricher_behavior_${BEHAVIOR}.pcap tests"
# end::start_client_tcpdump[]
unset docker
sleep 3

screen -ls || true
if [[ "$BEHAVIOR" =~ ^(caching)$ ]];
then
# Warm-up run downloads the model
WARMUP_RUN1_START=$(date +%s)
docker compose exec client grpcurl -plaintext \
       -d '{"weather_forecast": {"city": {"name": "warmup"}}}' \
       server:50051 enricher.v1.EnricherService/Enrich
WARMUP_RUN1_END=$(date +%s)
WARMUP_RUN1_ELAPSED=$((WARMUP_RUN1_END - WARMUP_RUN1_START))
echo "WARMUP_RUN1 took ${WARMUP_RUN1_ELAPSED} seconds"
echo
# tag::start_client_caching[]
CACHING_RUN1_START=$(date +%s)
docker compose exec client grpcurl -plaintext \
       -d '{"weather_forecast": {"city": {"name": "caching"}}}' \
       server:50051 enricher.v1.EnricherService/Enrich
CACHING_RUN1_END=$(date +%s)
CACHING_RUN1_ELAPSED=$((CACHING_RUN1_END - CACHING_RUN1_START))
echo "CACHING_RUN1 took ${CACHING_RUN1_ELAPSED} seconds"
echo
CACHING_RUN2_START=$(date +%s)
docker compose exec client grpcurl -plaintext \
       -d '{"weather_forecast": {"city": {"name": "caching"}}}' \
       server:50051 enricher.v1.EnricherService/Enrich
CACHING_RUN2_END=$(date +%s)
CACHING_RUN2_ELAPSED=$((CACHING_RUN2_END - CACHING_RUN2_START))
echo "CACHING_RUN2 took ${CACHING_RUN2_ELAPSED} seconds"
# end::start_client_caching[]
fi
if [[ "$BEHAVIOR" =~ ^(basic_error_status)$ ]];
then
# tag::start_client_basic_error_status[]
TEMP_STDERR_FILE=$(mktemp)
docker compose exec client grpcurl -plaintext \
       -d '{"weather_forecast": {"temperature_max_celsius": 100.0}}' \
       server:50051 enricher.v1.EnricherService/Enrich > "$TEMP_STDERR_FILE" 2>&1 || true
BASIC_ERROR_STATUS_STDERR=$(<"$TEMP_STDERR_FILE")
echo "${BASIC_ERROR_STATUS_STDERR}"
# end::start_client_basic_error_status[]
fi
if [[ "$BEHAVIOR" =~ ^(rich_error_status)$ ]];
then
# tag::start_client_rich_error_status[]
TEMP_STDERR_FILE=$(mktemp)
docker compose exec client grpcurl -plaintext \
       -d '{"weather_forecast": {"temperature_min_celsius": 100.0}}' \
       server:50051 enricher.v1.EnricherService/Enrich > "$TEMP_STDERR_FILE" 2>&1 || true
RICH_ERROR_STATUS_STDERR=$(<"$TEMP_STDERR_FILE")
echo "${RICH_ERROR_STATUS_STDERR}"
# end::start_client_rich_error_status[]
fi
if [[ "$BEHAVIOR" =~ ^(deadline)$ ]];
then
# tag::start_client_deadline[]
TEMP_STDERR_FILE=$(mktemp)
docker compose exec client grpcurl -plaintext \
       -d '{"weather_forecast": {"city": {"name": "deadline"}}}' --max-time 1 \
       server:50051 enricher.v1.EnricherService/Enrich > "$TEMP_STDERR_FILE" 2>&1 || true
DEADLINE_STDERR=$(<"$TEMP_STDERR_FILE")
echo "${DEADLINE_STDERR}"
# end::start_client_deadline[]
fi
if [[ "$BEHAVIOR" =~ ^(reflection)$ ]];
then
# tag::start_client_reflection_list_services[]
docker compose exec client grpcurl -plaintext server:50051 list
# end::start_client_reflection_list_services[]
# tag::start_client_reflection_describe_service[]
docker compose exec client grpcurl -plaintext \
       server:50051 describe enricher.v1.EnricherService
# end::start_client_reflection_describe_service[]
# tag::start_client_reflection_describe_message[]
docker compose exec client grpcurl -plaintext \
       -msg-template server:50051 describe enricher.v1.EnrichRequest
# end::start_client_reflection_describe_message[]
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
PCAP="tests/enricher_behavior_${BEHAVIOR}.pcap"
# tag::tshark_read_enricher_behavior[]
docker compose exec client bash -c "tshark --read-file tests/enricher_behavior_${BEHAVIOR}.pcap"
# end::tshark_read_enricher_behavior[]
echo
if [[ "$BEHAVIOR" =~ ^(caching)$ ]];
then
  echo "Second request is cached"
  DIFFERENCE=$((CACHING_RUN1_ELAPSED - CACHING_RUN2_ELAPSED))
  if (( DIFFERENCE < 0 )); then
    DIFFERENCE=$(( -DIFFERENCE ))
  fi
  if (( DIFFERENCE < 5 )); then
    echo "Error: two runs are within ${DIFFERENCE} seconds"
    exit 1
  fi
fi
if [[ "$BEHAVIOR" =~ ^(basic_error_status)$ ]];
then
  echo "basic_error_status is returned"
  echo "${BASIC_ERROR_STATUS_STDERR}" | grep --quiet "Message: Allowed temperature_max_celsius range"
fi
if [[ "$BEHAVIOR" =~ ^(rich_error_status)$ ]];
then
  echo "rich_error_status is returned"
  echo "${RICH_ERROR_STATUS_STDERR}" | grep  --quiet "Message: Field validation error"
fi
if [[ "$BEHAVIOR" =~ ^(deadline)$ ]];
then
  echo "deadline is returned"
  echo "${DEADLINE_STDERR}" | grep --quiet "Code: DeadlineExceeded"
fi
