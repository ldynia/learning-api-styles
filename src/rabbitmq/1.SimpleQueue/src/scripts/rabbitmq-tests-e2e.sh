#!/usr/bin/env bash

set -Eeuo pipefail

if [[ "$(basename $(pwd))" != "1.SimpleQueue" ]];
then
    echo "Error: this script must be run from the '1.SimpleQueue' directory"
    exit 1
fi

echo "Executing: $0"

docker compose version

# tag::teardown_containers[]
docker compose down --volumes && docker network rm -f rabbitmq
# end::teardown_containers[]

export BUILDKIT_PROGRESS=plain
# tag::start_containers[]
docker compose up --detach --wait
# end::start_containers[]

screen -ls || true
LOGFILE_CONSUMER=src/scripts/e2e-tests-consumer.log
echo > $LOGFILE_CONSUMER
docker compose exec consumer bash -c 'kill $(pgrep --full "python3 /usr/src/consumer.py")' || true
function docker () {
    screen -L -Logfile $LOGFILE_CONSUMER -S consumer -d -m docker "$@"
}
# tag::start_consumer[]
docker compose exec consumer python3 /usr/src/consumer.py
# end::start_consumer[]
unset docker
sleep 1

screen -ls || true
LOGFILE_PRODUCER=src/scripts/e2e-tests-producer.log
echo > $LOGFILE_PRODUCER
docker compose exec producer bash -c 'kill $(pgrep --full "python3 /usr/src/producer.py")' || true
function docker () {
    screen -L -Logfile $LOGFILE_PRODUCER -S producer -d -m docker "$@"
}
# tag::start_producer[]
for i in {1..6}; do docker compose exec producer python3 /usr/src/producer.py; done
# end::start_producer[]
unset docker

# Wait for consumers to read messages
sleep 3

# stop remaining screen sessions
echo "quit consumer" && screen -X -S "consumer" quit
screen -ls || true

# cat and test captured screen output
echo "cat $LOGFILE_PRODUCER" && cat $LOGFILE_PRODUCER && echo
echo "cat $LOGFILE_CONSUMER" && cat $LOGFILE_CONSUMER && echo

# Test $LOGFILE_PRODUCER and $LOGFILE_CONSUMER contains 6 messages (12 messages total)
MESSAGES_PRODUCER=$((grep 'Sent.*message' $LOGFILE_PRODUCER || true) | wc -l | xargs)
MESSAGES_CONSUMER=$((grep 'Received.*message' $LOGFILE_CONSUMER || true) | wc -l | xargs)
if [ $(($MESSAGES_PRODUCER + $MESSAGES_CONSUMER)) -eq 12 ]; then
  echo "Test PASSED"; echo
  exit 0
else
  echo "Test FAILED"; echo
  exit 1
fi

# docker compose down --volumes && docker network rm -f rabbitmq

# rm $LOGFILE_PRODUCER $LOGFILE_CONSUMER
