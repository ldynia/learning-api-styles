#!/usr/bin/env bash

set -Eeuo pipefail

if [[ "$(basename $(pwd))" != "3.PubSub" ]];
then
    echo "Error: this script must be run from the '3.PubSub' directory"
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
LOGFILE_CONSUMER_A=src/scripts/e2e-tests-consumer-a.log
echo > $LOGFILE_CONSUMER_A
docker compose exec consumer-a bash -c 'kill $(pgrep --full "python3 /usr/src/consumer.py")' || true
function docker () {
    screen -L -Logfile $LOGFILE_CONSUMER_A -S consumer-a -d -m docker "$@"
}
# tag::start_consumer-a[]
docker compose exec consumer-a python3 /usr/src/consumer.py
# end::start_consumer-a[]
unset docker
sleep 1

screen -ls || true
LOGFILE_CONSUMER_B=src/scripts/e2e-tests-consumer-b.log
echo > $LOGFILE_CONSUMER_B
docker compose exec consumer-b bash -c 'kill $(pgrep --full "python3 /usr/src/consumer.py")' || true
function docker () {
    screen -L -Logfile $LOGFILE_CONSUMER_B -S consumer-b -d -m docker "$@"
}
# tag::start_consumer-b[]
docker compose exec consumer-b python3 /usr/src/consumer.py
# end::start_consumer-b[]
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
echo "quit consumer-a" && screen -X -S "consumer-a" quit
screen -ls || true
echo "quit consumer-b" && screen -X -S "consumer-b" quit
screen -ls || true

# cat and test captured screen output
echo "cat $LOGFILE_PRODUCER" && cat $LOGFILE_PRODUCER && echo
echo "cat $LOGFILE_CONSUMER_A" && cat $LOGFILE_CONSUMER_A && echo
echo "cat $LOGFILE_CONSUMER_B" && cat $LOGFILE_CONSUMER_B && echo

# Test $MESSAGES_PRODUCER, $LOGFILE_CONSUMER_A and $LOGFILE_CONSUMER_B contains more than 6 messages (18 messages in total)
MESSAGES_PRODUCER=$((grep 'Sent .* message' $LOGFILE_PRODUCER || true) | wc -l | xargs)
MESSAGES_CONSUMER_A=$((grep 'Received .* message' $LOGFILE_CONSUMER_A || true) | wc -l | xargs)
MESSAGES_CONSUMER_B=$((grep 'Received .* message' $LOGFILE_CONSUMER_B || true) | wc -l | xargs)
if [ $(($MESSAGES_PRODUCER + $MESSAGES_CONSUMER_A + $MESSAGES_CONSUMER_B)) -eq 18 ]; then
  echo "Test PASSED"; echo
  exit 0
else
  echo "Test FAILED"; echo
  exit 1
fi

# docker compose down --volumes && docker network rm -f rabbitmq

# rm $LOGFILE_PRODUCER $LOGFILE_CONSUMER_A $LOGFILE_CONSUMER_B
