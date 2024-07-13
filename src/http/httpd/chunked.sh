#!/bin/bash

send_chunk() {
  local chunk="$1"
  local chunk_size=$(printf "%x" ${#chunk})
  echo -en "${chunk_size}\r\n${chunk}\r\n"
}

echo -en "Content-Type: text/plain\r\nTransfer-Encoding: chunked\r\n\r\n"

send_chunk "Hello! "
sleep 1
send_chunk "The chunked "
sleep 1
send_chunk "transfer coding."
send_chunk ""
