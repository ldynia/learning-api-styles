#!/usr/bin/env bash

set -Eeuo pipefail

function usage() {
  echo "Usage: ./$0 unary|server_streaming|client_streaming|bidirectional_streaming insecure|mtls"
}

get_network_information () {
  # From the $1 container, get the interface name or IP address on the $2 network
  local mode=$1
  local service_name=$2
  local network_name=$3
  local container_id=$(docker compose ps -q "${service_name}")
  local network_info=$(docker inspect "${container_id}")
  local mac_address=$(echo "${network_info}" | jq -r ".[0].NetworkSettings.Networks.${network_name}.MacAddress")
  local ip_address=$(echo "${network_info}" | jq -r ".[0].NetworkSettings.Networks.${network_name}.IPAddress")
  local interfaces=$(docker compose exec -t "${service_name}" ip a)
  local interface_name=$(echo "${interfaces}" | grep -a1 "${mac_address}" | tail -1 | rev | cut -d' ' -f1 | rev | xargs)
  if [[ "${mode}" == "interface" ]];
  then
    echo "${interface_name}"
  fi
  if [[ "${mode}" == "ip" ]];
  then
    echo "${ip_address}"
  fi
}

WORK_DIR=$(basename $(pwd))
ROOT_DIR="grpc"
if [[ "$WORK_DIR" != "$ROOT_DIR" ]]; then
  echo "Error: Script must be run from the $ROOT_DIR directory"
  usage
  exit 1
fi

if [[ $# -ne 2 ]]; then
  usage
  exit 1
fi

if [[ $# -eq 2 ]]; then
  RPC=$1
  SECURITY=$2
fi

if ! [[ "$RPC" =~ ^(unary|server_streaming|client_streaming|bidirectional_streaming)$ ]]; then
  echo "Error: Incorrect RPC type: $RPC. Supported values: unary|server_streaming|client_streaming|bidirectional_streaming"
  usage
  exit 1
fi

if ! [[ "$SECURITY" =~ ^(insecure|mtls)$ ]]; then
  echo "Error: Incorrect $SECURITY setting. Supported values: insecure|mtls"
  usage
  exit 1
fi

echo "Executing: $0 $@"

# Start with clean SSLKEYLOGFILE
docker compose exec client bash -c "echo > tests/SSLKEYLOGFILE.client"

screen -ls || true
LOGFILE_SERVER=tests/echo_rpc_${RPC}_${SECURITY}_server.log
echo > ${LOGFILE_SERVER}
docker compose exec server bash -c 'kill $(pgrep --full "python src/echo/echo/server.py")' || true
function docker () {
  screen -L -Logfile ${LOGFILE_SERVER} -S server -d -m docker "$@"
}
# tag::start_server[]
docker compose exec server bash -ci \
       "PYTHONPATH=./src/echo python src/echo/echo/server.py ${SECURITY}"
# end::start_server[]
unset docker
sleep 3

screen -ls || true
LOGFILE_TCPDUMP=tests/echo_rpc_${RPC}_${SECURITY}_tcpdump.log
echo > ${LOGFILE_TCPDUMP}
docker compose exec client bash -c 'sudo kill $(pgrep --full "sudo tcpdump")' || true
# tag::client_flush_arp_cache[]
docker compose exec client bash -c "sudo ip neigh flush all"
# end::client_flush_arp_cache[]
NETWORK_NAME=grpc_internal
CLIENT_INTERFACE_NAME=$(get_network_information interface "client" "${NETWORK_NAME}")
SERVER_IP_ADDRESS=$(get_network_information ip "server" "${NETWORK_NAME}")
echo "client will access server '${SERVER_IP_ADDRESS}' on network '${NETWORK_NAME}' using interface '${CLIENT_INTERFACE_NAME}'"
function docker () {
  screen -L -Logfile ${LOGFILE_TCPDUMP} -S tcpdump -d -m docker "$@"
}
# tag::start_client_tcpdump[]
PCAP_FILE=/tmp/echo_rpc_${RPC}_${SECURITY}.pcap
docker compose exec client bash -c \
       "sudo rm -f ${PCAP_FILE} && \
       sudo tcpdump -w ${PCAP_FILE} 'port 50051' && \
       cp ${PCAP_FILE} tests"
# end::start_client_tcpdump[]
unset docker
sleep 3

screen -ls || true
# tag::start_client[]
docker compose exec client bash -ci \
       "PYTHONPATH=./src/echo python src/echo/echo/client.py ${RPC} ${SECURITY}"
# end::start_client[]
sleep 3

echo

# stop tcpdump, by sending SIGINT (ctrl+c)
docker compose exec client bash -c 'sudo kill -SIGINT $(pgrep --full "sudo tcpdump")' || true
screen -X -S "tcpdump" quit
screen -ls || true

# stop server
screen -X -S "server" quit
screen -ls || true

# cat captured screen output
echo "cat ${LOGFILE_SERVER}" && cat ${LOGFILE_SERVER}
echo "cat ${LOGFILE_TCPDUMP}" && cat ${LOGFILE_TCPDUMP}

if [[ "$SECURITY" =~ ^(mtls)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_editcap_pcapng[]
docker compose exec client bash -c \
       "cd tests && \
       editcap --inject-secrets tls,SSLKEYLOGFILE.client \
       echo_rpc_${RPC}_${SECURITY}.pcap echo_rpc_${RPC}_${SECURITY}.pcapng"
# end::start_editcap_pcapng[]
fi

# test the created pcap
echo "Test pcap can be read"
if [[ "$SECURITY" =~ ^(insecure)$ ]];
then
# DO NOT INDENT to keep proper include alignment
PCAP="tests/echo_rpc_${RPC}_${SECURITY}.pcap"
# tag::tshark_read_echo_rpc_insecure[]
docker compose exec client bash -c "tshark --read-file tests/echo_rpc_${RPC}_${SECURITY}.pcap"
# end::tshark_read_echo_rpc_insecure[]
fi
if [[ "$SECURITY" =~ ^(mtls)$ ]];
then
# DO NOT INDENT to keep proper include alignment
PCAP="tests/echo_rpc_${RPC}_${SECURITY}.pcapng"
# tag::tshark_read_echo_rpc_mtls[]
docker compose exec client bash -c "tshark --read-file tests/echo_rpc_${RPC}_${SECURITY}.pcapng"
# end::tshark_read_echo_rpc_mtls[]
fi
echo
if [[ "$RPC" =~ ^(unary)$ ]] && [[ "$SECURITY" =~ ^(insecure)$ ]];
then
NUMBER_OF_PACKETS=$(docker compose exec client bash -c "tshark --read-file ${PCAP} | wc -l")
if [[ "${NUMBER_OF_PACKETS}" == "0" ]];
then
  echo "Test pcap is empty. This is an error, which may happen sometimes, but not always."
  echo "This is due to the traffic going through incorrect interface, since 'server' name instead of IP address is used."
else
echo "Test pcap has number of packets 16|17|18|19|20"
docker compose exec client bash -c "tshark --read-file ${PCAP} | wc -l | xargs | grep -E --quiet '16|17|18|19|20'"
echo "Test pcap has number of packets tcp 16|17|18|19|20"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | wc -l | xargs | grep -E --quiet '16|17|18|19|20'"
echo "Test pcap has packets tcp that use only desired ports"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | grep -E '50051' | grep -E --quiet '16|17|18|19|20'"
echo "Test pcap has first packet tcp [SYN]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | head -1 | grep --quiet '\[SYN\]'"
echo "Test pcap has next to last packet tcp [FIN, ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -2 | head -1 | grep --quiet '\[FIN, ACK\]'"
# This test is flaky
# echo "Test pcap has next to next to last packet tcp [FIN, ACK]"
# docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -3 | head -1 | grep --quiet '\[FIN, ACK\]'"
# This should be the case, but instead last packet tcp is most often [RST, ACK] from the client. See https://github.com/marcindulak/grpc-client-tcp-rst
# echo "Test pcap has last packet tcp [ACK]"
# docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -1 | grep --quiet '\[ACK\]'"
# echo "Test pcap has last packet tcp sent by server"
# docker compose exec client bash -c "CLIENT_IP=\$(timeout 5 ping -q -c 1 client | grep 'PING client' | cut -d'(' -f 2 | cut -d')' -f1) && tshark --read-file ${PCAP} -Y tcp | tail -1 | grep --quiet \"→ \${CLIENT_IP}\""
echo "Test pcap has last packet tcp [RST, ACK] or [ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -1 | grep -E --quiet '\[RST, ACK\]|\[ACK\]'"
echo "Test pcap has first packet http2 Magic"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http2 | head -1 | grep --quiet 'Magic'"
echo "Test pcap has first packet grpc HTTP2 POST"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y grpc | head -1 | grep --quiet 'HEADERS\[1\]: POST /echo.v1.EchoService/DemoUnary'"
echo "Test pcap has last packet grpc HTTP2 DATA"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y grpc | tail -1 | grep --quiet 'HEADERS\[1\]: 200 OK, DATA\[1\]'"
echo "Test pcap has first packet grpc HTTP2 protobuf Hello"
docker compose exec client bash -c "LINE_NUMBER=\$(tshark --read-file ${PCAP} -Y grpc | grep 'HEADERS\[1\]: POST /echo.v1.EchoService/DemoUnary' | tr -s ' ' | xargs | cut -d ' ' -f 1) && tshark --read-file ${PCAP} -Y \"frame.number == \${LINE_NUMBER}\" -T fields -e http2.data.data | xxd -plain -revert | grep --quiet 'Hello'"
# The last packet http2 should be GOAWAY, but it's [RST, ACK] from the client. See https://github.com/marcindulak/grpc-client-tcp-rst
# echo "Test pcap has last http2 packet HTTP2 GOAWAY"
# docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http2 | tail -1 | grep --quiet 'GOAWAY\[0\]'"
fi
fi
