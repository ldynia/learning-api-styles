#!/usr/bin/env bash

set -Eeuo pipefail

if [[ "$(basename $(pwd))" != "django" ]]; then
  echo "Error: this script must be run from the 'django' directory"
  exit 1
fi

echo "Executing: $0"

function testUnreadFeeds() {
  # Configure the newsboat feed reader to point to our feed URL
  docker compose exec app bash -c \
        "mkdir -p ~/.newsboat && \
        echo http://localhost:8000/forecast/feed > ~/.newsboat/urls"

  docker compose exec app bash -c \
        "newsboat --refresh-on-start --execute='reload' --execute='print-unread' | \
        ack --passthru '6 unread articles'"

  if [[ "$?" -eq 0 ]]; then
    echo "Test unread feeds PASSED"
  else
    echo "Test unread feeds FAILED"
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
testUnreadFeeds
