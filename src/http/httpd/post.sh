#!/bin/bash

send_status_400() {
  echo "Status: 400 Bad Request"
  echo "Content-type: text/plain"
  echo ""
  echo "Error: $1"
  exit 1
}

send_status_405() {
  echo "Status: 405 Method Not Allowed"
  echo "Content-type: text/plain"
  echo "Allow: POST"
  echo ""
  echo "Error: This script only handles POST requests."
  exit 1
}

send_status_415() {
  echo "Status: 415 Unsupported Media Type"
  echo "Content-type: text/plain"
  echo ""
  echo "Error: Unsupported Content-Type: $1"
  exit 1
}

if [ "$REQUEST_METHOD" = "POST" ]; then
  if [ -z "$CONTENT_LENGTH" ]; then
      send_status_400 "Missing Content-Length header."
  fi
  if [ "$CONTENT_TYPE" != "text/plain" ]; then
    send_status_415 "$CONTENT_TYPE"
  fi
  read -n "$CONTENT_LENGTH" -r POST_DATA
  echo "Content-type: text/plain"
  echo ""
  echo "Received POST data: $POST_DATA"
else
  send_status_405
fi
