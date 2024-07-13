#!/usr/bin/env bash

set -Eeuo pipefail

if [[ "$(basename $(pwd))" != "django" ]]; then
  echo "Error: this script must be run from the 'django' directory"
  exit 1
fi

echo "Executing: $0"

function testWebhookEchoV1Endpoint() {
  EPOCH=$(date +%s)
  LOGFILE_WEBHOOK_V1="app/scripts/webhooks-tests-e2e-v1.log"
  docker compose exec app python manage.py app_event \
    --callback-url webhook/v1/echo \
    --payload '{"type": "dummy.event", "timestamp": '$EPOCH', "data": {"echo": "test"}}' \
    > $LOGFILE_WEBHOOK_V1

  RESPONSE_WEBHOOK_V1=$(grep '{"type"' $LOGFILE_WEBHOOK_V1 || true)
  if [[ -n "$RESPONSE_WEBHOOK_V1" ]]; then
    echo -e "Test Webhook Echo V1 PASSED"
  else
    echo -e "Test Webhook Echo V1 Failed"
    exit 1
  fi
}

function testWebhookEchoV2Endpoint() {
  EPOCH=$(date +%s)
  LOGFILE_WEBHOOK_V2=app/scripts/webhooks-tests-e2e-v2.log
  docker compose exec app python manage.py app_event \
    --callback-url webhook/v2/echo \
    --payload '{"type": "dummy.event", "timestamp": '$EPOCH', "data": {"echo": "test"}}' \
    > $LOGFILE_WEBHOOK_V2

  RESPONSE_WEBHOOK_V2=$(grep '{"type"' $LOGFILE_WEBHOOK_V2 || true)
  if [[ -n "$RESPONSE_WEBHOOK_V2" ]]; then
    echo -e "Test Webhook Echo V2 PASSED"
  else
    echo -e "Test Webhook Echo V2 FAILED"
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
testWebhookEchoV1Endpoint
testWebhookEchoV2Endpoint
