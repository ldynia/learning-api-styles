#!/usr/bin/env bash

set -Eeuo pipefail

function usage() {
  echo "Usage: ./$0 netcat|scapy|python|openssl"
}

WORK_DIR=$(basename $(pwd))
ROOT_DIR="network"
if [[ "$WORK_DIR" != "$ROOT_DIR" ]]; then
  echo "Error: Script must be run from the $ROOT_DIR directory"
  usage
  exit 1
fi

if [[ $# -ne 1 ]]; then
  echo "Error: Client type argument is required: netcat|scapy|python|openssl"
  usage
  exit 1
else
  CLIENT=$1
fi

if ! [[ "$CLIENT" =~ ^(netcat|scapy|python|openssl)$ ]]; then
  echo "Error: Incorrect client type: $CLIENT. Supported values: netcat|scapy|python|openssl"
  usage
  exit 1
fi

echo "Executing: $0 $@"

# Start with clean SSLKEYLOGFILE
docker compose exec client bash -c "echo > tests/SSLKEYLOGFILE.client"

# tag::print_tcp_echo_client_pcap[]
docker compose exec client bash -c \
       "tshark --read-file tests/tcp_echo_client_${CLIENT}_reference.pcap | \
       bash scripts/trim_client_pcap.sh"
# end::print_tcp_echo_client_pcap[]

screen -ls || true
LOGFILE_SERVER=tests/tcp_echo_client_${CLIENT}_server.log
echo > ${LOGFILE_SERVER}
docker compose exec server bash -c 'sudo kill $(pgrep --full "sudo python src/tcp_echo/server.py")' || true
function docker () {
  screen -L -Logfile ${LOGFILE_SERVER} -S server -d -m docker "$@"
}
# DO NOT INDENT to keep proper include alignment
# tag::start_tcp_echo_server[]
docker compose exec server bash -c "sudo python src/tcp_echo/server.py"
# end::start_tcp_echo_server[]
unset docker
sleep 3

screen -ls || true
LOGFILE_TCPDUMP=tests/tcp_echo_client_${CLIENT}_tcpdump.log
echo > ${LOGFILE_TCPDUMP}
docker compose exec client bash -c 'sudo kill $(pgrep --full "sudo tcpdump")' || true
# tag::tcp_echo_client_flush_arp_cache[]
docker compose exec client bash -c "sudo ip neigh flush all"
# end::tcp_echo_client_flush_arp_cache[]
function docker () {
  screen -L -Logfile ${LOGFILE_TCPDUMP} -S tcpdump -d -m docker "$@"
}
if [[ ! "$CLIENT" =~ ^(openssl)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_tcp_echo_client_tcpdump_tcp[]
PCAP_FILE=/tmp/tcp_echo_client_${CLIENT}.pcap
docker compose exec client bash -c \
       "sudo rm --force ${PCAP_FILE} && \
       sudo tcpdump -c 12 -w ${PCAP_FILE} 'not icmp and not icmp6' && \
       cp ${PCAP_FILE} tests"
# end::start_tcp_echo_client_tcpdump_tcp[]
fi
if [[ "$CLIENT" =~ ^(openssl)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_tcp_echo_client_tcpdump_tls[]
PCAP_FILE=/tmp/tcp_echo_client_${CLIENT}.pcap
docker compose exec client bash -c \
       "sudo rm --force ${PCAP_FILE} && \
       sudo tcpdump -c 18 -w ${PCAP_FILE} 'port 443' && \
       cp ${PCAP_FILE} tests"
# end::start_tcp_echo_client_tcpdump_tls[]
fi
unset docker
sleep 3

screen -ls || true
if [[ $CLIENT == netcat ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_tcp_echo_client_netcat[]
docker compose exec client bash -c \
       "(echo -n Hello | netcat -p 8080 -i 1 -q 1 server 8080) && echo"
# end::start_tcp_echo_client_netcat[]
fi
if [[ $CLIENT == scapy ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_tcp_echo_client_scapy[]
docker compose exec client bash -c \
       "sudo python src/tcp_echo/client_scapy.py && echo"
# end::start_tcp_echo_client_scapy[]
fi
if [[ $CLIENT == python ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_tcp_echo_client_python[]
docker compose exec client bash -c \
       "sudo python src/tcp_echo/client.py && echo"
# end::start_tcp_echo_client_python[]
fi
if [[ $CLIENT == openssl ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_tcp_echo_client_openssl[]
docker compose exec client bash -c \
       'export SSLKEYLOGFILE=tests/SSLKEYLOGFILE.client && \
       (echo -n Hello && sleep 1 && echo -n) | \
       openssl s_client -brief -connect server:443 \
       -CAfile ca.crt -verify_return_error \
       -keylogfile ${SSLKEYLOGFILE} -servername server -tls1_3'
# end::start_tcp_echo_client_openssl[]
fi
sleep 3

echo

# stop server
screen -X -S "server" quit
screen -ls || true

if [[ "$CLIENT" =~ ^(openssl)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_editcap_pcapng[]
docker compose exec client bash -c \
       "cd tests && \
       editcap --inject-secrets tls,SSLKEYLOGFILE.client \
       tcp_echo_client_${CLIENT}.pcap tcp_echo_client_${CLIENT}.pcapng"
# end::start_editcap_pcapng[]
fi

# cat captured screen output
echo "cat ${LOGFILE_SERVER}" && cat ${LOGFILE_SERVER}
echo "cat ${LOGFILE_TCPDUMP}" && cat ${LOGFILE_TCPDUMP}

if [[ ! "$CLIENT" =~ ^(openssl)$ ]];
then
# test the created pcap
PCAP=tests/tcp_echo_client_${CLIENT}.pcap
echo
echo "Test pcap can be read"
docker compose exec client bash -c "tshark --read-file ${PCAP}"
echo "Test pcap has number of packets 12"
docker compose exec client bash -c "tshark --read-file ${PCAP} | wc -l | xargs | grep --quiet 12"
echo "Test pcap has number of packets arp 2"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y arp | wc -l | xargs | grep --quiet 2"
echo "Test pcap has number of packets tcp 10"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | wc -l | xargs | grep --quiet 10"
echo "Test pcap has packets tcp that use only desired ports"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | grep '8080 → 8080' | grep --quiet 10"
echo "Test pcap has first packet arp Broadcast"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y arp | head -1 | grep --quiet Broadcast"
echo "Test pcap has first packet tcp [SYN]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | head -1 | grep --quiet '\[SYN\]'"
echo "Test pcap has next to last packet tcp [FIN, ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -2 | head -1 | grep --quiet '\[FIN, ACK\]'"
echo "Test pcap has next to next to last packet tcp [FIN, ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -3 | head -1 | grep --quiet '\[FIN, ACK\]'"
echo "Test pcap has last packet tcp [ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -1 | grep --quiet '\[ACK\]'"
docker compose exec client bash -c "tshark --read-file ${PCAP} | bash scripts/trim_client_pcap.sh"
fi

if [[ "$CLIENT" =~ ^(openssl)$ ]];
then
# test the created pcap
PCAP=tests/tcp_echo_client_${CLIENT}.pcapng
echo
echo "Test pcap can be read"
docker compose exec client bash -c "tshark --read-file ${PCAP}"
echo "Test pcap has number of packets 18"
docker compose exec client bash -c "tshark --read-file ${PCAP} | wc -l | xargs | grep --quiet 18"
echo "Test pcap has number of packets arp 0"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y arp | wc -l | xargs | grep --quiet 0"
echo "Test pcap has number of packets tcp 18"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | wc -l | xargs | grep --quiet 18"
echo "Test pcap has packets tcp that use only desired ports"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | grep -E ' → 443|443 → ' | grep --quiet 11"
echo "Test pcap has first packet tcp [SYN]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | head -1 | grep --quiet '\[SYN\]'"
echo "Test pcap has next to last packet tcp [FIN, ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -2 | head -1 | grep --quiet '\[FIN, ACK\]'"
echo "Test pcap has last packet tcp [ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -1 | grep --quiet '\[ACK\]'"
echo "Test pcap has first packet tls Client Hello"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tls | head -1 | grep --quiet 'Client Hello'"
echo "Test pcap has second packet tls Server Hello"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tls | head -2 | tail -1 | grep --quiet 'Server Hello'"
echo "Test pcap has next to last packet tls Alert"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tls | tail -2 | head -1 | grep --quiet 'Alert'"
echo "Test pcap has last packet tls Alert"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tls | tail -1 | grep --quiet 'Alert'"
echo "Test pcap has first packet tls application data Hello"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 9' -T fields -e tls.segment.data | xxd -plain -revert | grep --quiet 'Hello'"
echo "Test pcap has second packet tls application data Hello"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 11' -T fields -e tls.segment.data | xxd -plain -revert | grep --quiet 'Hello'"
docker compose exec client bash -c "tshark --read-file ${PCAP} | bash scripts/trim_client_pcap.sh"
fi
