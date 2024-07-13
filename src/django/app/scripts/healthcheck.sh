#!/usr/bin/env bash

set -Eeuo pipefail

if [[ "$TLS_ENABLE" -eq 0 ]]; then
  curl --fail "http://localhost:$APP_PORT_HTTP"
else
  curl --insecure --fail "https://localhost:$APP_PORT_HTTP"
fi
