#!/usr/bin/env bash

set -Eeuo pipefail

function usage() {
  echo "Usage: ./$0 http0.9|http1.0|http1.1|h2c|h2|http3|firefox|iperf|tcp|tls"
}

WORK_DIR=$(basename $(pwd))
ROOT_DIR="http"
if [[ "$WORK_DIR" != "$ROOT_DIR" ]]; then
  echo "Error: Script must be run from the $ROOT_DIR directory"
  usage
  exit 1
fi

if [[ $# -ne 1 ]]; then
  echo "Error: Client argument is required: http0.9|http1.0|http1.1|h2c|h2|http3|firefox|iperf|tcp|tls"
  usage
  exit 1
else
  CLIENT=$1
fi

if ! [[ "$CLIENT" =~ ^(http0.9|http1.0|http1.1|h2c|h2|http3|firefox|iperf|tcp|tls)$ ]]; then
  echo "Error: Incorrect client: $CLIENT. Supported values: http0.9|http1.0|http1.1|h2c|h2|http3|firefox|iperf|tcp|tls"
  usage
  exit 1
fi

echo "Executing: $0 $@"

# Start with clean SSLKEYLOGFILE
docker compose exec client bash -c "echo > tests/SSLKEYLOGFILE.client"
docker compose exec https-server bash -c "echo > /usr/src/http/tests/SSLKEYLOGFILE.server"

if [[ "$CLIENT" =~ ^(iperf)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::configurenetwork_for_iperf[]
docker compose exec client bash -c \
       "sudo tc qdisc del dev lo root || true && \
       sudo tc qdisc add dev lo root netem delay 100ms rate 100mbit loss 1% && \
       tc qdisc show dev lo && \
       sudo ip link set dev lo mtu 1500 && \
       ip a"
# end::configurenetwork_for_iperf[]
fi
if [[ "$CLIENT" =~ ^(tcp)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::configure_network_for_tcp[]
docker compose exec client bash -c \
       "sudo tc qdisc del dev lo root || true && \
       sudo tc qdisc add dev lo root handle 1: prio && \
       sudo tc qdisc add dev lo parent 1:1 netem delay 5s && \
       sudo tc filter add dev lo protocol ip parent 1:0 prio 1 handle 1 fw flowid 1:1 && \
       tc qdisc show dev lo && \
       sudo ip link set dev lo mtu 1500 && \
       ip a && \
       sudo iptables -A OUTPUT -p tcp --dport 80 \
         -m string --string DELAYME --algo bm -j MARK --set-mark 1 && \
       sudo iptables-legacy-save && sudo iptables-save"
# end::configure_network_for_tcp[]
fi

screen -ls || true
LOGFILE_SERVER=tests/client_${CLIENT}_server.log
echo > ${LOGFILE_SERVER}
function docker () {
  screen -L -Logfile ${LOGFILE_SERVER} -S server -d -m docker "$@"
}
if [[ "$CLIENT" =~ ^(iperf)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_server_iperf[]
docker compose exec client bash -c "iperf --server --port 80 --time 10"
# end::start_server_iperf[]
fi
if [[ "$CLIENT" =~ ^(tcp)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_server_tcp[]
docker compose exec client bash -c "netcat -l -p 80 && echo"
# end::start_server_tcp[]
fi
if [[ "$CLIENT" =~ ^(tls)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_server_tls[]
docker compose exec client bash -c \
       "sudo openssl s_server -accept 443 -quiet -naccept 1 \
       -cert /etc/ssl/certs/openssl.crt \
       -key /etc/ssl/private/openssl.key"
# end::start_server_tls[]
fi
unset docker
sleep 3

screen -ls || true
LOGFILE_TCPDUMP=tests/client_${CLIENT}_tcpdump.log
echo > ${LOGFILE_TCPDUMP}
docker compose exec client bash -c 'sudo kill $(pgrep --full "sudo tcpdump")' || true
# tag::client_flush_arp_cache[]
docker compose exec client bash -c "sudo ip neigh flush all"
# end::client_flush_arp_cache[]
function docker () {
  screen -L -Logfile ${LOGFILE_TCPDUMP} -S tcpdump -d -m docker "$@"
}
if [[ "$CLIENT" =~ ^(http0|http1|h2c) ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_tcpdump[]
PCAP_FILE=/tmp/client_${CLIENT}.pcap
docker compose exec client bash -c \
       "sudo rm --force ${PCAP_FILE} && \
       sudo tcpdump -w ${PCAP_FILE} 'port 80' && \
       cp ${PCAP_FILE} tests"
# end::start_client_tcpdump[]
fi
if [[ $CLIENT == firefox ]];
then
# DO NOT INDENT to keep proper include alignment
# Filter out traffic to akamai.tre.se by hard-coding its IP address.
# tag::start_client_firefox_tcpdump[
PCAP_FILE=/tmp/client_${CLIENT}.pcap
docker compose exec client bash -c \
       "sudo rm --force ${PCAP_FILE} && \
       sudo tcpdump -w ${PCAP_FILE} \
       'port 80 and not (host 95.209.205.40 or host 95.209.205.27)' && \
       cp ${PCAP_FILE} tests"
# end::start_client_firefox_tcpdump[]
fi
if [[ "$CLIENT" =~ ^(iperf|tcp)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_tcp_tcpdump[]
PCAP_FILE=/tmp/client_${CLIENT}.pcap
docker compose exec client bash -c \
       "sudo rm --force ${PCAP_FILE} && \
       sudo tcpdump --interface lo -w ${PCAP_FILE} 'port 80' && \
       cp ${PCAP_FILE} tests"
# end::start_client_tcp_tcpdump[]
fi
if [[ "$CLIENT" =~ ^(h2|http3)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_https_tcpdump[]
PCAP_FILE=/tmp/client_${CLIENT}.pcap
docker compose exec client bash -c \
       "sudo rm --force ${PCAP_FILE} && \
       sudo tcpdump -w ${PCAP_FILE} 'port 80 or port 443' && \
       cp ${PCAP_FILE} tests"
# end::start_client_https_tcpdump[]
fi
if [[ "$CLIENT" =~ ^(tls)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_tls_tcpdump[]
PCAP_FILE=/tmp/client_${CLIENT}.pcap
docker compose exec client bash -c \
       "sudo rm --force ${PCAP_FILE} && \
       sudo tcpdump --interface lo -w ${PCAP_FILE} 'port 443' && \
       cp ${PCAP_FILE} tests"
# end::start_client_tls_tcpdump[]
fi
unset docker
sleep 3

screen -ls || true
if [[ $CLIENT == http0.9 ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_http0.9[]
docker compose exec client bash -c \
       "echo -en 'GET /Hello.html\r\n\r\n' | netcat -p 8080 http-server 80"
# end::start_client_http0.9[]
fi
if [[ $CLIENT == http1.0 ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_http1.0[]
docker compose exec client bash -c \
       "echo -en 'GET /HelloValid.html HTTP/1.0\r\n\r\n' | \
       netcat -p 8080 http-server 80"
# end::start_client_http1.0[]
fi
if [[ $CLIENT == firefox ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_firefox[]
docker compose exec client bash -c \
       "rm -rf ~/.cache/mozilla/firefox/* && \
       rm -rf ~/.mozilla/firefox/*.profile && \
       firefox --headless --screenshot /tmp/website-in-firefox.png \
       http://http-server/HelloWeb.html && \
       cp /tmp/website-in-firefox.png tests"
# end::start_client_firefox[]
fi
if [[ $CLIENT == iperf ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_iperf[]
docker compose exec client bash -c \
       "iperf --client 127.0.0.1 --bind 127.0.0.1:8080 --port 80 \
       --interval 1 --time 5"
# end::start_client_iperf[]
fi
if [[ $CLIENT == tcp ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_tcp[]
docker compose exec client bash -c \
       "exec 3<>/dev/tcp/127.0.0.1/80 && \
       echo -n SEGMENT1 >&3 && \
       echo -n DELAYME >&3 && \
       echo -n SEGMENT11 >&3 && \
       sleep 1 && \
       echo -n SEGMENT111 >&3 && \
       exec 3<&- && \
       exec 3>&- && \
       sleep 5"
# end::start_client_tcp[]
fi
if [[ $CLIENT == http1.1 ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_http1.1[]
docker compose exec client bash -c \
       'GET="GET / HTTP/1.1\r\nHost:host\r\n" && echo -en \
       "${GET}Connection:keep-alive\r\n\r\n${GET}Connection:close\r\n\r\n" | \
       netcat -p 8080 http-server 80'
# end::start_client_http1.1[]
fi
if [[ $CLIENT == h2c ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_h2c[]
docker compose exec client bash -c \
       "nghttp --verbose --timeout 3 --no-dep --hexdump \
       http://https-server:80"
# end::start_client_h2c[]
fi
if [[ $CLIENT == h2 ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_h2[]
docker compose exec client bash -c \
       "SSLKEYLOGFILE=tests/SSLKEYLOGFILE.client \
       nghttp --verbose --timeout 3 --no-dep --hexdump --no-verify-peer \
       https://https-server"
# end::start_client_h2[]
fi
if [[ $CLIENT == tls ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_tls[]
docker compose exec client bash -c \
       "export SSLKEYLOGFILE=tests/SSLKEYLOGFILE.client && \
       echo -n Hello | gnutls-cli --port 443 --insecure 127.0.0.1"
# end::start_client_tls[]
fi
if [[ $CLIENT == http3 ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_client_http3[]
docker compose exec client bash -c \
       "export SSLKEYLOGFILE=tests/SSLKEYLOGFILE.client && \
       curl --http3 --insecure --verbose https://https-server"
# end::start_client_http3[]
fi
sleep 3

echo

# stop tcpdump, by sending SIGINT (ctrl+c)
docker compose exec client bash -c 'sudo kill -SIGINT $(pgrep --full "sudo tcpdump")' || true
screen -X -S "tcpdump" quit
screen -ls || true
if [[ "$CLIENT" =~ ^(h2|http3|tls)$ ]];
then
# DO NOT INDENT to keep proper include alignment
# tag::start_editcap_pcapng[]
docker compose exec client bash -c \
       "cd tests && \
       editcap --inject-secrets tls,SSLKEYLOGFILE.client \
       client_${CLIENT}.pcap client_${CLIENT}.pcapng"
# end::start_editcap_pcapng[]
fi

# cat captured screen output
echo "cat ${LOGFILE_TCPDUMP}" && cat ${LOGFILE_TCPDUMP}

# test the created pcap
if [[ $CLIENT == http0.9 ]];
then
# DO NOT INDENT to keep proper include alignment
PCAP=tests/client_${CLIENT}.pcap
echo
echo "Test pcap can be read"
# tag::tshark_read_client_http0.9[]
docker compose exec client bash -c \
       "tshark --read-file tests/client_${CLIENT}.pcap"
# end::tshark_read_client_http0.9[]
echo "Test pcap has number of packets 10"
docker compose exec client bash -c "tshark --read-file ${PCAP} | wc -l | xargs | grep --quiet 10"
echo "Test pcap has number of packets tcp 10"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | wc -l | xargs | grep --quiet 10"
echo "Test pcap has packets tcp that use only desired ports"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | grep -E '8080 → 80|80 → 8080' | grep --quiet 10"
echo "Test pcap has first packet tcp [SYN]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | head -1 | grep --quiet '\[SYN\]'"
echo "Test pcap has next to last packet tcp [FIN, ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -2 | head -1 | grep --quiet '\[FIN, ACK\]'"
# This test is flaky
# echo "Test pcap has next to next to last packet tcp [FIN, ACK]"
# docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -3 | head -1 | grep --quiet '\[FIN, ACK\]'"
echo "Test pcap has last packet tcp [ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -1 | grep --quiet '\[ACK\]'"
echo "Test pcap has last packet tcp sent by server"
docker compose exec client bash -c "CLIENT_IP=\$(timeout 5 ping -q -c 1 client | grep 'PING client' | cut -d'(' -f 2 | cut -d')' -f1) && tshark --read-file ${PCAP} -Y tcp | tail -1 | grep --quiet \"→ \${CLIENT_IP}\""
echo "Test pcap has first http packet HTTP request"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http | head -1 | grep --quiet 'GET /Hello.html'"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 4' -T fields -e tcp.payload | xxd -plain -revert | grep --quiet 'GET /Hello.html'"
echo "Test pcap has last http packet HTTP response"
# Continuation means that the packet has no HTTP headers
# https://osqa-ask.wireshark.org/questions/7268/http-continuation-vs-tcp-segment/
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http | tail -1 | grep --quiet 'Continuation'"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 6' -T fields -e tcp.payload | xxd -plain -revert | grep --quiet 'Hello'"
fi

# test the created pcap
if [[ $CLIENT == http1.0 ]];
then
# DO NOT INDENT to keep proper include alignment
PCAP=tests/client_${CLIENT}.pcap
echo
echo "Test pcap can be read"
# tag::tshark_read_client_http1.0[]
docker compose exec client bash -c \
       "tshark --read-file tests/client_${CLIENT}.pcap"
# end::tshark_read_client_http1.0[]
echo "Test pcap has number of packets 10"
docker compose exec client bash -c "tshark --read-file ${PCAP} | wc -l | xargs | grep --quiet 10"
echo "Test pcap has number of packets tcp 10"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | wc -l | xargs | grep --quiet 10"
echo "Test pcap has packets tcp that use only desired ports"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | grep -E '8080 → 80|80 → 8080' | grep --quiet 10"
echo "Test pcap has first packet tcp [SYN]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | head -1 | grep --quiet '\[SYN\]'"
echo "Test pcap has next to last packet tcp [FIN, ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -2 | head -1 | grep --quiet '\[FIN, ACK\]'"
# This test is flaky
# echo "Test pcap has next to next to last packet tcp [FIN, ACK]"
# docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -3 | head -1 | grep --quiet '\[FIN, ACK\]'"
echo "Test pcap has last packet tcp [ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -1 | grep --quiet '\[ACK\]'"
echo "Test pcap has last packet tcp sent by server"
docker compose exec client bash -c "CLIENT_IP=\$(timeout 5 ping -q -c 1 client | grep 'PING client' | cut -d'(' -f 2 | cut -d')' -f1) && tshark --read-file ${PCAP} -Y tcp | tail -1 | grep --quiet \"→ \${CLIENT_IP}\""
echo "Test pcap has first http packet HTTP request"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http | head -1 | grep --quiet 'GET /HelloValid.html HTTP/1.0'"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 4' -T fields -e tcp.payload | xxd -plain -revert | grep --quiet 'GET /HelloValid.html HTTP/1.0'"
echo "Test pcap has last http packet HTTP response"
# Continuation means that the packet has no HTTP headers
# https://osqa-ask.wireshark.org/questions/7268/http-continuation-vs-tcp-segment/
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http | tail -1 | grep --quiet 'HTTP/1.0 200 OK'"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 6' -T fields -e tcp.payload | xxd -plain -revert | grep --quiet 'Hello'"
fi

# test the created pcap
if [[ $CLIENT == firefox ]];
then
# DO NOT INDENT to keep proper include alignment
PCAP=tests/client_${CLIENT}.pcap
echo
echo "Test pcap can be read"
# tag::tshark_read_client_firefox[]
docker compose exec client bash -c \
       "tshark --read-file tests/client_${CLIENT}.pcap"
# end::tshark_read_client_firefox[]
echo "Test pcap has more than 1 tcp [SYN]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | grep '\[SYN\]' | wc -l | xargs -I {} bash -c 'if [ {} -lt 2 ]; then exit 1; else exit 0; fi'"
fi

# test the created pcap
if [[ $CLIENT == iperf ]];
then
# DO NOT INDENT to keep proper include alignment
PCAP=tests/client_${CLIENT}.pcap
echo
echo "Test pcap can be read"
# tag::tshark_read_client_iperf[]
docker compose exec client bash -c \
       "tshark --read-file tests/client_${CLIENT}.pcap"
# end::tshark_read_client_iperf[]
echo "Test pcap has more than 1 tcp [TCP Dup ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | grep '\[TCP Dup ACK' | wc -l | xargs -I {} bash -c 'if [ {} -lt 2 ]; then exit 1; else exit 0; fi'"
fi

# test the created pcap
if [[ $CLIENT == tcp ]];
then
# DO NOT INDENT to keep proper include alignment
tshark_read_tcp() {
  # Read pcap with tshark and trim away uninteresting information
  local pcap="$1"
  tshark --read-file "${pcap}" | sed -E 's/Win=[0-9]+//' | sed -E 's/MSS=[0-9]+//' | sed -E 's/SACK_PERM//' | sed -E 's/TSval=[0-9]+//' | sed -E 's/TSecr=[0-9]+//' | sed -E 's/WS=[0-9]+//'| sed -E 's/SLE=[0-9]+//' | sed -E 's/SRE=[0-9]+//' | sed -E 's/127.0.0.1 → 127.0.0.1//' | sed -E 's/TCP//' | sed -E 's/ +/ /g' | cut -d' ' -f 2,3,5- | sed -E 's/(\[[^]]+\]) ([0-9]+ → [0-9]+)/\2 \1/' | sed -E 's/ [0-9]+ → 80/ client → 80/' | sed -E 's/ 80 → [0-9]+ / 80 → client /' | sed -E 's/80 →/server →/' | sed -E 's/→ 80/→ server/'
}
declare_tshark_read_tcp=$(declare -f tshark_read_tcp)
PCAP=tests/client_${CLIENT}.pcap
echo
echo "Test pcap can be read"
# tag::tshark_read_client_tcp[]
docker compose exec client bash -c \
       "tshark --read-file tests/client_${CLIENT}.pcap"
# end::tshark_read_client_tcp[]
echo "Test pcap can be read and filtered"
# tag::tshark_read_client_tcp_filtered[]
docker compose exec client bash -c \
       "${declare_tshark_read_tcp} && \
       tshark_read_tcp tests/client_${CLIENT}.pcap"
# end::tshark_read_client_tcp_filtered[]
echo "Test pcap has number of packets 13"
docker compose exec client bash -c "${declare_tshark_read_tcp} && tshark_read_tcp ${PCAP} | wc -l | xargs | grep --quiet 13"
echo "Test pcap has number of packets tcp 13"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | wc -l | xargs | grep --quiet 13"
echo "Test pcap has packets tcp that use only desired ports"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | grep -E ' → 80|80 → ' | grep --quiet 10"
echo "Test pcap has first packet tcp [SYN]"
docker compose exec client bash -c "${declare_tshark_read_tcp} && tshark_read_tcp ${PCAP} | head -1 | grep --quiet '\[SYN\]'"
echo "Test pcap has next to last packet tcp [FIN, ACK]"
docker compose exec client bash -c "${declare_tshark_read_tcp} && tshark_read_tcp ${PCAP} | tail -2 | head -1 | grep --quiet '\[FIN, ACK\]'"
echo "Test pcap has last packet tcp [ACK]"
docker compose exec client bash -c "${declare_tshark_read_tcp} && tshark_read_tcp ${PCAP} | tail -1 | grep --quiet '\[ACK\]'"
echo "Test pcap has last packet tcp sent by client"
docker compose exec client bash -c "${declare_tshark_read_tcp} && tshark_read_tcp ${PCAP} | grep --quiet 'client → server'"
echo "Test pcap has 6th packet is [TCP Previous segment not captured]"
docker compose exec client bash -c "tshark --read-file ${PCAP} | head -6 | tail -1 | grep --quiet '\[TCP Previous segment not captured\]'"
echo "Test pcap has 6th packet that contains SEGMENT11"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 6' -T fields -e tcp.payload | xxd -plain -revert | grep --quiet 'SEGMENT11'"
echo "Test pcap has 8th packet that contains SEGMENT111"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 8' -T fields -e tcp.payload | xxd -plain -revert | grep --quiet 'SEGMENT111'"
echo "Test pcap has 10th packet is [TCP Retransmission]"
docker compose exec client bash -c "tshark --read-file ${PCAP} | head -10 | tail -1 | grep --quiet '\[TCP Retransmission\]'"
echo "Test pcap has 10th packet that contains DELAYME"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 10' -T fields -e tcp.payload | xxd -plain -revert | grep --quiet 'DELAYME'"
fi

if [[ $CLIENT == http1.1 ]];
then
# DO NOT INDENT to keep proper include alignment
PCAP=tests/client_${CLIENT}.pcap
echo
echo "Test pcap can be read"
# tag::tshark_read_client_http1.1[]
docker compose exec client bash -c \
       "tshark --read-file tests/client_${CLIENT}.pcap"
# end::tshark_read_client_http1.1[]
echo "Test pcap has number of packets 12"
docker compose exec client bash -c "tshark --read-file ${PCAP} | wc -l | xargs | grep --quiet 12"
echo "Test pcap has number of packets tcp 12"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | wc -l | xargs | grep --quiet 12"
echo "Test pcap has packets tcp that use only desired ports"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | grep -E '8080 → 80|80 → 8080' | grep --quiet 12"
echo "Test pcap has first packet tcp [SYN]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | head -1 | grep --quiet '\[SYN\]'"
echo "Test pcap has next to last packet tcp [FIN, ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -2 | head -1 | grep --quiet '\[FIN, ACK\]'"
echo "Test pcap has last packet tcp [ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -1 | grep --quiet '\[ACK\]'"
echo "Test pcap has last packet tcp sent by server"
docker compose exec client bash -c "CLIENT_IP=\$(timeout 5 ping -q -c 1 client | grep 'PING client' | cut -d'(' -f 2 | cut -d')' -f1) && tshark --read-file ${PCAP} -Y tcp | tail -1 | grep --quiet \"→ \${CLIENT_IP}\""
echo "Test pcap has first http packet two HTTP requests"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http | head -1 | grep --quiet 'GET / HTTP/1.1 GET / HTTP/1.1'"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 4' -T fields -e tcp.payload | xxd -plain -revert | grep --quiet 'GET / HTTP/1.1'"
echo "Test pcap has next to last http packet HTTP response"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http | tail -2 | head -1 | grep --quiet 'HTTP/1.1 200 OK'"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 6' -T fields -e tcp.payload | xxd -plain -revert | grep --quiet 'HTTP/1.1 200 OK'"
echo "Test pcap has last http packet HTTP response"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http | tail -1 | grep --quiet 'HTTP/1.1 200 OK'"
# This test is flaky, the second HTTP packet comes as number 7 sometimes
# docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 8' -T fields -e tcp.payload | xxd -plain -revert | grep --quiet 'HTTP/1.1 200 OK'"
fi

if [[ $CLIENT == h2c ]];
then
# DO NOT INDENT to keep proper include alignment
PCAP=tests/client_${CLIENT}.pcap
echo
echo "Test pcap can be read"
# tag::tshark_read_client_h2c[]
docker compose exec client bash -c \
       "tshark --read-file tests/client_${CLIENT}.pcap"
# end::tshark_read_client_h2c[]
echo "Test pcap has number of packets 13"
docker compose exec client bash -c "tshark --read-file ${PCAP} | wc -l | xargs | grep --quiet 13"
echo "Test pcap has number of packets tcp 13"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | wc -l | xargs | grep --quiet 13"
echo "Test pcap has packets tcp that use only desired ports"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | grep -E ' → 80 | 80 → ' | grep --quiet 13"
echo "Test pcap has first packet tcp [SYN]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | head -1 | grep --quiet '\[SYN\]'"
echo "Test pcap has next to last packet tcp [FIN, ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -2 | head -1 | grep --quiet '\[FIN, ACK\]'"
echo "Test pcap has last packet tcp [ACK]"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y tcp | tail -1 | grep --quiet '\[ACK\]'"
echo "Test pcap has last packet tcp sent by client"
docker compose exec client bash -c "CLIENT_IP=\$(timeout 5 ping -q -c 1 client | grep 'PING client' | cut -d'(' -f 2 | cut -d')' -f1) && tshark --read-file ${PCAP} -Y tcp | tail -1 | grep --quiet \"\${CLIENT_IP} → \""
echo "Test pcap has first http2 packet Magic, SETTINGS[0], HEADERS[1]: GET /"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http2 | head -1 | grep --quiet 'Magic, SETTINGS\[0\], HEADERS\[1\]: GET /'"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 4' -T fields -e tcp.payload | xxd -plain -revert | grep --quiet 'PRI \* HTTP/2.0'"
echo "Test pcap has next to last http2 packet HTTP2 response"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http2 | tail -2 | head -1 | grep --quiet 'DATA\[1\]'"
# This test is flaky, the second HTTP packet comes as number 8 sometimes
# docker compose exec client bash -c "tshark --read-file ${PCAP} -Y 'frame.number == 9' -T fields -e tcp.payload | xxd -plain -revert | grep --quiet 'Welcome to nginx!'"
echo "Test pcap has last http2 packet HTTP2 GOAWAY"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http2 | tail -1 | grep --quiet 'GOAWAY\[0\]'"
fi

if [[ $CLIENT == http3 ]];
then
# DO NOT INDENT to keep proper include alignment
PCAP=tests/client_${CLIENT}.pcapng
echo
echo "Test pcap can be read"
# tag::tshark_read_client_http3[]
docker compose exec client bash -c \
       "tshark --read-file tests/client_${CLIENT}.pcapng"
# end::tshark_read_client_http3[]
# These tests are flaky, sometimes there are 12 packets
# echo "Test pcap has number of packets 11"
# docker compose exec client bash -c "tshark --read-file ${PCAP} | wc -l | xargs | grep --quiet 11"
# echo "Test pcap has number of packets quic 11"
# docker compose exec client bash -c "tshark --read-file ${PCAP} -Y quic | wc -l | xargs | grep --quiet 11"
echo "Test pcap has first packet quic Initial"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y quic | head -1 | grep --quiet 'Initial'"
# These tests are flaky, sometimes the last quic packet is ACK sent by the server
# echo "Test pcap has last packet quic CC"
# docker compose exec client bash -c "tshark --read-file ${PCAP} -Y quic | tail -1 | grep --quiet 'CC'"
# echo "Test pcap has last packet quic sent by client"
# docker compose exec client bash -c "CLIENT_IP=\$(timeout 5 ping -q -c 1 client | grep 'PING client' | cut -d'(' -f 2 | cut -d')' -f1) && tshark --read-file ${PCAP} -Y quic | tail -1 | grep --quiet \"\${CLIENT_IP} → \""
# This test is flaky
# Sometimes : GET / is not present, and this packet comes second not first
# echo "Test pcap has first http3 packet STREAM(0), HEADERS: GET /"
# docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http3 | head -1 | grep --quiet 'STREAM(0), HEADERS: GET /'"
echo "Test pcap has last http3 packet STREAM(0), HEADERS: 200 OK, DATA"
docker compose exec client bash -c "tshark --read-file ${PCAP} -Y http3 | tail -1 | grep --quiet 'STREAM(0), HEADERS: 200 OK, DATA'"
fi
