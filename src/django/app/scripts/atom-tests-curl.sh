#!/usr/bin/env bash

set -Eeuo pipefail

if [[ "$(basename $(pwd))" != "django" ]]; then
  echo "Error: this script must be run from the 'django' directory"
  exit 1
fi

echo "Executing: $0"

function testAtomFeed() {
  ATOM_FEED_ENDPOINT="forecast/feed"
  LOGFILE=scripts/atom-tests-curl.log

  # Get the Atom feed
  STATUSCODE=$(docker compose exec app curl -s -w "%{http_code}" -o $LOGFILE "http://localhost:8000/$ATOM_FEED_ENDPOINT")
  if [[ ! $STATUSCODE -eq 200 ]]; then
    echo "Status code: $STATUSCODE Failed to get data from '$ATOM_FEED_ENDPOINT' endpoint."
    exit 1
  fi

  # Get the weather forecast for the city UUID
  CITY_UUID=$(grep -oE 'forecast/[a-f0-9\-]+' app/$LOGFILE | cut -d'/' -f2 | tail -n 1)
  WEATHER_FORECAST_ENDPOINT="forecast/$CITY_UUID"

  STATUSCODE=$(docker compose exec app curl -s -w "%{http_code}" -X GET "http://localhost:8000/$WEATHER_FORECAST_ENDPOINT" -o /dev/null)
  if [[ $STATUSCODE -eq 200 ]]; then
    echo -e "Test ATOM feed PASSED"
  else
    echo -e "Test ATOM feed FAILED"
    exit 1
  fi
}

docker compose version
docker compose down --volumes

export BUILDKIT_PROGRESS=plain
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait

testAtomFeed