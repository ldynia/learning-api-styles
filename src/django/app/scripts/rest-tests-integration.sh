#!/usr/bin/env bash

set -Eeuo pipefail

if [[ "$(basename $(pwd))" != "django" ]]; then
  echo "Error: this script must be run from the 'django' directory"
  exit 1
fi

echo "Executing: $0"

function testJWTRetrieval() {
  CREDENTIALS='{"username":"admin","password":"admin"}'
  ACCESS_TOKEN=$(docker compose exec app \
    curl \
    --silent \
    --request POST \
    --header "Content-Type: application/json" \
    --data "$CREDENTIALS" \
    http://localhost:8000/api/jwt/obtain | \
    jq -r ".access")

  if [ -n "$ACCESS_TOKEN" ]; then
    echo "Test JWT retrieval PASSED"
  else
    echo "Test JWT retrieval FAILED"
    exit 1
  fi
}

function testCityCreation() {
  CREATE_CITY_PAYLOAD='{
    "name":"Copenhagen",
    "country":"Denmark",
    "region":"Europe",
    "timezone":"Europe/Copenhagen",
    "latitude":55.676100,
    "longitude":12.568300
  }'
  CITY_UUID=$(docker compose exec app bash -c \
    "curl --data '$CREATE_CITY_PAYLOAD' \
      --header 'Authorization: Bearer $ACCESS_TOKEN' \
      --header 'Content-Type: application/json' \
      --request 'POST' \
      --silent \
      'http://localhost:8000/api/cities' | \
    jq -r '.results[0].uuid'"
  )

  if [ -n "$CITY_UUID" ]; then
    echo "Test city creation PASSED"
  else
    echo "Test city creation FAILED"
    exit 1
  fi
}

function testCityRetrieval() {
  CITY_CAIRO=$(docker compose exec app bash -c \
    "curl --silent \
      'http://localhost:8000/api/cities?sort=-name&fields=name&search_region=Africa' | \
    jq '.results[0].name'")
  if [ "$CITY_CAIRO" == \"Cairo\" ]; then
    echo "Test city retrieval PASSED"
  else
    echo "Test city retrieval FAILED"
    exit 1
  fi
}

function testContentPagination() {
  PAGINATED_CONTENT_NEXT=$(docker compose exec app bash -c \
    "curl --silent 'http://localhost:8000/api/cities?page_size=1&page=2' | \
    jq '.next'"
  )
  PAGINATED_CONTENT_PREVIOUS=$(docker compose exec app bash -c \
    "curl --silent 'http://localhost:8000/api/cities?page_size=1&page=2' | \
    jq '.previous'"
  )
  if [[ -n "${PAGINATED_CONTENT_NEXT:-}" && -n "${PAGINATED_CONTENT_PREVIOUS:-}" && "$PAGINATED_CONTENT_NEXT" != "null" && "$PAGINATED_CONTENT_PREVIOUS" != "null" ]]; then
    echo "Test city pagination PASSED"
  else
    echo "Test city pagination FAILED"
    exit 1
  fi
}

function testCityDeletion() {
  CITY_UUID=$(docker compose exec app bash -c \
    "curl --silent 'http://localhost:8000/api/cities?search_name=Cairo' | \
    jq --raw-output '.results[0].uuid'"
  )
  STATUS=$(docker compose exec app bash -c \
    "curl \
    --header 'Authorization: Bearer $ACCESS_TOKEN' \
    --request 'DELETE' \
    --silent \
    'http://localhost:8000/api/cities/$CITY_UUID?soft_delete=true' | \
    jq '.results[0].deleted'"
  )
  if [ "$STATUS" == "true" ]; then
    echo "Test city deletion PASSED"
  else
    echo "Test city deletion FAILED"
    exit 1
  fi
}

function runBDDTests() {
  docker compose exec app python manage.py behave --no-input
  if [[ $? -eq 0 ]]; then
    echo "BDD tests PASSED"
  else
    echo "BDD tests FAILED"
    exit 1
  fi
}

function runIntegrationTests() {
  docker compose exec app python manage.py test --no-input
  if [[ $? -eq 0 ]]; then
    echo "Integration tests PASSED"
  else
    echo "Error: Integration tests FAILED"
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
testJWTRetrieval
testCityCreation
testCityRetrieval
testContentPagination
testCityDeletion
runBDDTests
runIntegrationTests
