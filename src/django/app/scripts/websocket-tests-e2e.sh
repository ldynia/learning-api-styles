#!/usr/bin/env bash

set -Eeuo pipefail

if [[ "$(basename $(pwd))" != "django" ]]; then
  echo "Error: this script must be run from the 'django' directory"
  exit 1
fi

echo "Executing: $0"

function testWebsocketConnection() {
  ACCESS_TOKEN=$(docker compose exec app bash -c "curl -s -X 'POST' 'http://localhost:8000/api/jwt/obtain' -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin\"}' | jq \".access\" | base64 -w 0")
  CITY_UUID=$(docker compose exec app python manage.py app_cities | head -n 1 | cut -d' ' -f 2)
  docker compose exec app bash -c "wscat --no-check --host 'localhost:8001' --connect 'ws://127.0.0.1:8001/ws/v1/alert?city_uuid=$CITY_UUID&access_token=$ACCESS_TOKEN' &"

  # This command is optional, and is to be run in the second terminal
  # docker compose exec app bash -c "python manage.py app_alert --city-uuid $CITY_UUID"

  EXIT=$?

  if [[ $EXIT -eq 0 ]]; then
    echo "Test Websocket Connection PASSED"
  else
    echo "Test Websocket Connection FAILED"
    exit 1
  fi
}

# Setup
docker compose version
docker compose down --volumes

export BUILDKIT_PROGRESS=plain
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait

# Run tests
testWebsocketConnection
