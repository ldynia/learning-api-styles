#!/usr/bin/env bash

set -Eeuo pipefail

if [[ "$(basename $(pwd))" != "6.RequestResponse" ]];
then
    echo "Error: this script must be run from the '6.RequestResponse' directory"
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
LOGFILE_SERVER=src/scripts/e2e-tests-server.log
echo > $LOGFILE_SERVER
docker compose exec server bash -c 'kill $(pgrep --full "python3 /usr/src/server.py")' || true
function docker () {
    screen -L -Logfile $LOGFILE_SERVER -S server -d -m docker "$@"
}
# tag::start_server[]
docker compose exec server python3 /usr/src/server.py
# end::start_server[]
unset docker
sleep 1

screen -ls || true
LOGFILE_CLIENT=src/scripts/e2e-tests-client.log
echo > $LOGFILE_CLIENT
docker compose exec client bash -c 'kill $(pgrep --full "python3 /usr/src/client.py")' || true
function docker () {
    screen -L -Logfile $LOGFILE_CLIENT -S client -d -m docker "$@"
}
# tag::start_client[]
for i in {1..6}; do docker compose exec client python3 /usr/src/client.py; done
# end::start_client[]
unset docker

# Wait for consumers to read messages
sleep 3

# stop remaining screen sessions
echo "quit server" && screen -X -S "server" quit
screen -ls || true

# cat and test captured screen output
echo "cat $LOGFILE_CLIENT" && cat $LOGFILE_CLIENT && echo
echo "cat $LOGFILE_SERVER" && cat $LOGFILE_SERVER && echo

# Test $MESSAGES_PRODUCER, $LOGFILE_SERVER and $LOGFILE_CONSUMER_B contains 6 messages
MESSAGES_CLIENT=$((grep 'Calling' $LOGFILE_CLIENT || true) | wc -l | xargs)
MESSAGES_SERVER=$((grep 'Computing .* queue' $LOGFILE_SERVER || true) | wc -l | xargs)
if [ $(($MESSAGES_CLIENT + $MESSAGES_SERVER)) -eq 12 ]; then
  echo "Test PASSED"; echo
  exit 0
else
  echo "Test FAILED"; echo
  exit 1
fi

# docker compose down --volumes && docker network rm -f rabbitmq

# rm $LOGFILE_CLIENT $LOGFILE_SERVER
