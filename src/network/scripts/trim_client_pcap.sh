#!/usr/bin/env bash

set -Eeuo pipefail

echo

# tag::get-ip-addresses[]
CLIENT_IP=$(timeout 5 ping -q -c 1 client | grep 'PING client' | cut -d'(' -f 2 | cut -d')' -f1)
echo "client: $CLIENT_IP"
CLIENT_ROUTER_IP=$(timeout 5 ping -q -c 1 router | grep 'PING router' | cut -d'(' -f 2 | cut -d')' -f1)
echo "client router: $CLIENT_ROUTER_IP"
SERVER_IP=$(timeout 5 ping -q -c 1 server | grep 'PING server' | cut -d'(' -f 2 | cut -d')' -f1)
echo "server: $SERVER_IP"
# end::get-ip-addresses[]

# tag::get-mac-addresses[]
CLIENT_MAC=$(ip -f inet -br link show | grep -v UNKNOWN | tr -s ' ' | cut -d' ' -f3)
echo "clientMAC: $CLIENT_MAC"
CLIENT_ROUTER_MAC=$(sudo arping -i eth0 -c 1 network_router | grep index=0 | cut -d' ' -f4)
echo "client routerMAC: $CLIENT_ROUTER_MAC"
# end::get-mac-addresses[]

echo

# tag::trim-pcap-output[]
cat - | \
  sed "s/$CLIENT_IP/client/g" | \
  sed "s/$SERVER_IP/server/g" | \
  sed "s/$CLIENT_ROUTER_IP/router/g" | \
  sed "s/$CLIENT_MAC/clientMAC/g" | \
  sed "s/$CLIENT_ROUTER_MAC/routerMAC/g" | \
  tr -s ' ' | \
  cut -d ' ' -f2,4,5,6,7,9- | \
  sed -E "s/MSS=[0-9]+//" | \
  sed -E "s/Win=[0-9]+//" | \
  sed -E "s/ SACK_PERM //" | \
  sed -E "s/TSval=[0-9]+//" | \
  sed -E "s/TSecr=[0-9]+//" | \
  sed -E "s/WS=[0-9]+//"
# end::trim-pcap-output[]
