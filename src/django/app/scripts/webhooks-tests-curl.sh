#!/usr/bin/env bash

set -Eeuo pipefail

if [[ "$(basename $(pwd))" != "django" ]]; then
  echo "Error: this script must be run from the 'django' directory"
  exit 1
fi

echo "Executing: $0"

# https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md
# Note: while it's OK (and recommended) to minimize the JSON body when serialized for sending,
# it's important to make sure that the payload sent is the same as the payload signed.
# Cryptographic signatures are sensitive to even the smallest changes, and even a stray space can cause the signature to be invalid.
# This is a very common failure mode as many webhook consumers often accidentally parse the body as json, and then serialize it again,
# which can cause for failed verification due to minor changes in serialization of JSON (which is not necessarily the same across implementations,
# or even multiple invocations of the same implementation).

function testWebhookEchoV1() {
  ENDPOINT="webhook/v1/echo"
  PAYLOAD_TIMESTAMP=$((2**31))
  WEBHOOK_TIMESTAMP=$(date +%s)
  WEBHOOK_ID="123abc"
  WEBHOOK_PAYLOAD="{\"type\": \"dummy_event.created\",\"timestamp\": \"${PAYLOAD_TIMESTAMP}\",\"data\": {\"echo\": \"test\"}}"
  WEBHOOK_SECRET=$(docker compose exec app bash -c 'echo -n "$WEBHOOK_SECRET"')
  # Create standard webhook signature
  SIG_SCHEME="${WEBHOOK_ID}.${WEBHOOK_TIMESTAMP}.${WEBHOOK_PAYLOAD}"
  # Avoid "warning: command substitution: ignored null byte in input" by immediately base64 encoding the signature
  SIGNATURE_B64=$(docker compose exec app bash -c "echo -n '$SIG_SCHEME' | openssl dgst -sha256 -hmac '$WEBHOOK_SECRET' -binary" | base64)
  STANDARD_WEBHOOK_SIGNATURE="v1,$SIGNATURE_B64"
  EXPECTED_RESPONSE='{"type": "dummy_event.created", "data": {"echo": "test"}}'

  docker compose exec app bash -c \
    "curl \
      --data '$WEBHOOK_PAYLOAD' \
      --fail-with-body \
      --header 'Content-Type: application/json' \
      --header 'webhook-id: $WEBHOOK_ID' \
      --header 'webhook-signature: $STANDARD_WEBHOOK_SIGNATURE' \
      --header 'webhook-timestamp: $WEBHOOK_TIMESTAMP' \
      --output response.json \
      --silent \
      'http://localhost:8000/$ENDPOINT'"

  if docker compose exec app jq -e --argjson expected "$EXPECTED_RESPONSE" '.type == $expected.type and .data.echo == $expected.data.echo' response.json > /dev/null; then
    echo "Test Webhook V1 PASSED"
  else
    echo "Test Webhook V1 FAILED"
    exit 1
  fi
}

function testWebhookEchoV2() {
  ENDPOINT="webhook/v2/echo"
  PAYLOAD_TIMESTAMP=$((2**31))
  WEBHOOK_TIMESTAMP=$(date +%s)
  WEBHOOK_ID="123abc"
  WEBHOOK_PAYLOAD="{\"type\": \"dummy_event.created\",\"timestamp\": \"${PAYLOAD_TIMESTAMP}\",\"data\": {\"echo\": \"test\"}}"
  WEBHOOK_SECRET=$(docker compose exec app bash -c 'echo -n "$WEBHOOK_SECRET"')
  # Create standard webhook signature
  SIG_SCHEME="${WEBHOOK_ID}.${WEBHOOK_TIMESTAMP}.${WEBHOOK_PAYLOAD}"
  # Avoid "warning: command substitution: ignored null byte in input" by immediately base64 encoding the signature
  SIGNATURE_B64=$(docker compose exec app bash -c "echo -n '$SIG_SCHEME' | openssl dgst -sha256 -hmac '$WEBHOOK_SECRET' -binary" | base64)
  STANDARD_WEBHOOK_SIGNATURE="v1,$SIGNATURE_B64"
  EXPECTED_RESPONSE='{"type": "dummy_event.created", "data": {"echo": "test"}}'

  docker compose exec app bash -c \
    "curl \
      --data '$WEBHOOK_PAYLOAD' \
      --fail-with-body \
      --output response.json \
      --silent \
      --header 'Content-Type: application/json' \
      --header 'webhook-id: $WEBHOOK_ID' \
      --header 'webhook-signature: $STANDARD_WEBHOOK_SIGNATURE' \
      --header 'webhook-timestamp: $WEBHOOK_TIMESTAMP' \
      'http://localhost:8000/$ENDPOINT'"

  if docker compose exec app jq -e --argjson expected "$EXPECTED_RESPONSE" '.type == $expected.type and .data.echo == $expected.data.echo' response.json > /dev/null; then
    echo "Test Webhook V2 PASSED"
  else
    echo "Test Webhook V2 FAILED"
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
testWebhookEchoV1
testWebhookEchoV2
