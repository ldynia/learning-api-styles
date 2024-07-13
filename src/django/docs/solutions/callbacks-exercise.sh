#!/usr/bin/env bash

# https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md
# Note: while it's OK (and recommended) to minimize the JSON body when serialized for sending,
# it's important to make sure that the payload sent is the same as the payload signed.
# Cryptographic signatures are sensitive to even the smallest changes, and even a stray space can cause the signature to be invalid.
# This is a very common failure mode as many webhook consumers often accidentally parse the body as json, and then serialize it again,
# which can cause for failed verification due to minor changes in serialization of JSON (which is not necessarily the same across implementations,
# or even multiple invocations of the same implementation).

set -Eeuo pipefail

# Set the variables
ENDPOINT_V1="webhook/v1/echo"
ENDPOINT_V2="webhook/v2/echo"
WEBHOOK_ID="123abc"
PAYLOAD_TIMESTAMP=$((2**31))
WEBHOOK_TIMESTAMP=$(date +%s)
WEBHOOK_PAYLOAD="{\"type\": \"dummy_event.created\", \"timestamp\": ${PAYLOAD_TIMESTAMP}, \"data\": {\"echo\": \"test\"}}"
WEBHOOK_SECRET=$WEBHOOK_SECRET

# Create standard webhook signature scheme
SIG_SCHEME="${WEBHOOK_ID}.${WEBHOOK_TIMESTAMP}.${WEBHOOK_PAYLOAD}"

# Create the HMAC using SHA256
SIGNATURE=$(echo -n $SIG_SCHEME | openssl dgst -sha256 -hmac $WEBHOOK_SECRET -binary)

# Encode the signature in base64. For long signature in Linux use base64 -w0
SIGNATURE_B64=$(echo -n $SIGNATURE | base64)

# Create the standard webhook signature
STANDARD_WEBHOOK_SIGNATURE="v1,$SIGNATURE_B64"

echo "Sent POST request to $ENDPOINT_V1 Received below response"
curl -X POST "http://localhost:8000/$ENDPOINT_V1" \
  -H "Content-Type: application/json" \
  -H "webhook-id: $WEBHOOK_ID" \
  -H "webhook-timestamp: $WEBHOOK_TIMESTAMP" \
  -H "webhook-signature: $STANDARD_WEBHOOK_SIGNATURE" \
  -d "$WEBHOOK_PAYLOAD"
echo
echo

echo "Sent POST request to $ENDPOINT_V2 Received below response"
curl -X POST "http://localhost:8000/$ENDPOINT_V2" \
  -H "Content-Type: application/json" \
  -H "webhook-id: $WEBHOOK_ID" \
  -H "webhook-timestamp: $WEBHOOK_TIMESTAMP" \
  -H "webhook-signature: $STANDARD_WEBHOOK_SIGNATURE" \
  -d "$WEBHOOK_PAYLOAD"
echo
