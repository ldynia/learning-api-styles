#!/usr/bin/env bash

set -Eeuo pipefail

WORK_DIR=$(basename $(pwd))
ROOT_DIR="network"
if [[ "$WORK_DIR" != "$ROOT_DIR" ]]; then
  echo "Error: Script must be run from the $ROOT_DIR directory"
  exit 1
fi

echo "Executing: $0"

# tag::get_client_ip_and_network[]
CLIENT_IP_AND_CIDR=$(docker compose exec client ip -f inet -br addr show | grep -v lo | tr -s ' ' | cut -d' ' -f3)
CLIENT_IP=$(echo $CLIENT_IP_AND_CIDR | sed -E 's|/.*||')
CLIENT_NETWORK=$(echo $CLIENT_IP_AND_CIDR | sed -E 's|.[0-9]+/|.0/|')
# end::get_client_ip_and_network[]

# tag::get_server_ip_and_network[]
SERVER_IP_AND_CIDR=$(docker compose exec server ip -f inet -br addr show | grep -v lo | tr -s ' ' | cut -d' ' -f3)
SERVER_IP=$(echo $SERVER_IP_AND_CIDR | sed -E 's|/.*||')
SERVER_NETWORK=$(echo $SERVER_IP_AND_CIDR | sed -E 's|.[0-9]+/|.0/|')
# end::get_server_ip_and_network[]

# tag::setup_routing[]
docker compose exec client bash -c "sudo ip route add $SERVER_NETWORK via \$(dig +short router | cut -d' ' -f4)"
docker compose exec client bash -c "sudo bash -c 'echo $SERVER_IP server >> /etc/hosts'"
docker compose exec server bash -c "sudo ip route add $CLIENT_NETWORK via \$(dig +short router | cut -d' ' -f4)"
docker compose exec server bash -c "sudo bash -c 'echo $CLIENT_IP client >> /etc/hosts'"
# end::setup_routing[]

# Test /etc/hosts name resolution, "dig +short server" may fail so use ping instead
echo -n "client: " && docker compose exec server bash -c "timeout 5 ping -q -c 1 client | grep 'PING client' | cut -d'(' -f 2 | cut -d')' -f1 | grep $CLIENT_IP"
echo -n "client router: " && docker compose exec client bash -c "timeout 5 ping -q -c 1 router | grep 'PING router' | cut -d'(' -f 2 | cut -d')' -f1"
echo -n "server: " && docker compose exec client bash -c "timeout 5 ping -q -c 1 server | grep 'PING server' | cut -d'(' -f 2 | cut -d')' -f1 | grep $SERVER_IP"
echo -n "server router: " && docker compose exec server bash -c "timeout 5 ping -q -c 1 router | grep 'PING router' | cut -d'(' -f 2 | cut -d')' -f1"

# Scapy may operate outside of the network kernel stack,
# kernel see some of the packets as unexpected, and issue resets (RST).
# The easiest workaround is to drop RST.
# tag::drop_kernel_rst_on_client[]
docker compose exec client bash -c "sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST --dport 8080 -j DROP"
docker compose exec client bash -c "sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST --dport 8443 -j DROP"
docker compose exec client bash -c "sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST --dport 443 -j DROP"
# end::drop_kernel_rst_on_client[]
