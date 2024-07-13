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

  # Read the beginning of the file
  expected_start='{"data": {"cities": [{"name": "Tokyo", "country": "Japan", "region": "Asia"}]}'
  file_start=$(docker compose exec app head -c ${#expected_start} response.json)

  # Check if the file starts with the expected string
  if [ "$file_start" == "$expected_start" ]; then
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

  EXPECTED_RESPONSE='{
    "name": "Warsaw",
    "country": "Poland",
    "region": "Europe",
    "timezone": "Europe/Warsaw",
    "latitude": 52.249782,
    "longitude": 21.012176
  }'

  # Use jq to compare the actual response with the expected response
  if docker compose exec app jq -e --argjson expected "$EXPECTED_RESPONSE" '.data.createCity | .name == $expected.name and .country == $expected.country and .region == $expected.region and .timezone == $expected.timezone and .latitude == $expected.latitude and .longitude == $expected.longitude' response.json > /dev/null; then
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

  EXPECTED_RESPONSE='{
    "uuid": "'$CITY_UUID'",
    "name": "'$NEW_NAME'"
  }'

  # Use jq to compare the actual response with the expected response
  if docker compose exec app jq -e --argjson expected "$EXPECTED_RESPONSE" '.data.updateCity | .name == $expected.name and .country == $expected.country and .region == $expected.region and .timezone == $expected.timezone and .latitude == $expected.latitude and .longitude == $expected.longitude' response.json > /dev/null; then
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

  EXPECTED_RESPONSE='{"uuid": "'$CITY_UUID'"}'

  # Use jq to compare the actual response with the expected response
  if docker compose exec app jq -e --argjson expected "$EXPECTED_RESPONSE" '.data.deleteCity | .uuid == $expected.uuid' response.json > /dev/null; then
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
