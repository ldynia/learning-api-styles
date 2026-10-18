#!/usr/bin/env bash

set -Eeuo pipefail

if [[ "$(basename $(pwd))" != "django" ]]; then
  echo "Error: this script must be run from the 'django' directory"
  exit 1
fi

echo "Executing: $0"

getJWTAccessToken() {
  CSRF_TOKEN=$1

  # Perform the GraphQL query
  # Warning: the credentails are hardcoded only for demonstration, avoid this behavior in production!
  docker compose exec app curl -s -o response.json http://localhost:8000/graphql \
    -X POST \
    -H "content-type: application/json" \
    -H "x-csrftoken: $CSRF_TOKEN" \
    -H "Cookie: csrftoken=$CSRF_TOKEN" \
    --data-raw "{\"query\":\"mutation ObtainJWTToken {\\n  obtainJwt(password: \\\"admin\\\", username: \\\"admin\\\") {\\n    token {\\n      token\\n    }\\n  }\\n}\"}"

  # Extract the token using jq
  ACCESS_TOKEN=$(docker compose exec app jq -r '.data.obtainJwt.token.token' response.json)

  echo "$ACCESS_TOKEN"
}

findCityUUID() {
  CSRF_TOKEN=$1
  CITY=$2

  # Perform the GraphQL query
  docker compose exec app curl -s -o response.json http://localhost:8000/graphql \
    -X POST \
    -H "content-type: application/json" \
    -H "x-csrftoken: $CSRF_TOKEN" \
    -H "Cookie: csrftoken=$CSRF_TOKEN" \
    --data-raw '{"query":"query FindCityUUID($cityName: String = \"'$CITY'\") {\n  cities(filters: {name: {iExact: $cityName}}) {\n    uuid\n  }\n}"}'

  # Extract the token using jq
  UUID=$(docker compose exec app jq -r '.data.cities[].uuid' response.json)

  echo "$UUID"
}

function testFindCity() {
  CSRF_TOKEN=$1
  CITY=$2

  # Perform the GraphQL query
  docker compose exec app curl -s -o response.json http://localhost:8000/graphql \
    -X POST \
    -H "content-type: application/json" \
    -H "x-csrftoken: $CSRF_TOKEN" \
    -H "Cookie: csrftoken=$CSRF_TOKEN" \
    --data-raw '{"query":"query FindCity($cityName: String = \"'$CITY'\") {\n  cities(order: {name: ASC}, filters: {name: {iExact: $cityName}}) {\n    name\n    country\n    region\n  }\n}"}'

  if docker compose exec app jq -e --arg city "$CITY" '
    (.data.cities | length) == 1 and
    (.data.cities[0].name == $city) and
    (.data.cities[0].country == "Japan") and
    (.data.cities[0].region == "Asia")
  ' response.json > /dev/null; then
    echo "Test FindCity PASSED"
  else
    echo "Test FindCity FAILED"
    exit 1
  fi
}

function testCreateCity() {
  CSRF_TOKEN=$1
  ACCESS_TOKEN=$2

  docker compose exec app curl -s -o response.json http://localhost:8000/graphql \
    -X POST \
    -H "content-type: application/json" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "x-csrftoken: $CSRF_TOKEN" \
    -H "Cookie: csrftoken=$CSRF_TOKEN" \
    --data-raw '{"query":"mutation CreateCity {\n  createCity(\n    data: {name: \"Warsaw\", country: \"Poland\", region: \"Europe\", timezone: \"Europe/Warsaw\", latitude: 52.249782, longitude: 21.012176}\n  ) {\n    uuid\n    name\n    country\n    region\n    timezone\n    latitude\n    longitude\n  }\n}"}'

  if docker compose exec app jq -e '
    (.data.createCity.name == "Warsaw") and
    (.data.createCity.country == "Poland") and
    (.data.createCity.region == "Europe") and
    (.data.createCity.timezone == "Europe/Warsaw") and
    (.data.createCity.latitude == 52.249782) and
    (.data.createCity.longitude == 21.012176)
  ' response.json > /dev/null; then
    echo "Test CreateCity PASSED"
  else
    echo "Test CreateCity FAILED"
    exit 1
  fi
}

function testUpdateCity() {
  CSRF_TOKEN=$1
  TOKEN=$2
  CITY_UUID=$3
  NEW_NAME=$4

  docker compose exec app curl -s -o response.json http://localhost:8000/graphql \
    -X POST \
    -H "content-type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "x-csrftoken: $CSRF_TOKEN" \
    -H "Cookie: csrftoken=$CSRF_TOKEN" \
    --data-raw '{"query":"mutation UpdateCity($city: UUID = \"'$CITY_UUID'\") {\n  updateCity(data: {uuid: $city, name: \"'$NEW_NAME'\"}) {\n    uuid\n    name\n  }\n}"}'

  if docker compose exec app jq -e --arg uuid "$CITY_UUID" --arg name "$NEW_NAME" '
    (.data.updateCity.uuid == $uuid) and
    (.data.updateCity.name == $name)
  ' response.json > /dev/null; then
    echo "Test UpdateCity PASSED"
  else
    echo "Test UpdateCity FAILED"
    exit 1
  fi
}

function testDeleteCity() {
  CSRF_TOKEN=$1
  ACCESS_TOKEN=$2
  CITY_UUID=$3

  docker compose exec app curl -s -o response.json http://localhost:8000/graphql \
    -X POST \
    -H 'content-type: application/json' \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "x-csrftoken: $CSRF_TOKEN" \
    -H "Cookie: csrftoken=$CSRF_TOKEN" \
    --data-raw '{"query":"mutation DeleteCity {\n  deleteCity(data: {uuid: \"'$CITY_UUID'\"}) {\n    uuid\n  }\n}"}'

  if docker compose exec app jq -e --arg uuid "$CITY_UUID" '.data.deleteCity.uuid == $uuid' response.json > /dev/null; then
    echo "Test DeleteCity PASSED"
  else
    echo "Test DeleteCity FAILED"
    exit 1
  fi
}

# Setup
docker compose version
docker compose down --volumes

export BUILDKIT_PROGRESS=plain
docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)
docker compose up --detach --wait

CSRF_TOKEN=$(openssl rand -hex 16)
ACCESS_TOKEN=$(getJWTAccessToken "$CSRF_TOKEN")
CITY_UUID=$(findCityUUID "$CSRF_TOKEN" "Tokyo")

# Run tests
testFindCity $CSRF_TOKEN "Tokyo"
testCreateCity $CSRF_TOKEN $ACCESS_TOKEN
testUpdateCity $CSRF_TOKEN $ACCESS_TOKEN $CITY_UUID "Tokio"
testDeleteCity $CSRF_TOKEN $ACCESS_TOKEN $CITY_UUID
