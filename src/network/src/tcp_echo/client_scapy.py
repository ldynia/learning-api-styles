"""TCP echo client"""

# tag::tcp_3_way_handshake[]
from scapy.all import IP, RandInt, TCP, send, sr

F = {  # <1>
    "ACK": "A",
    "FIN-ACK": "FA",
    "PSH-ACK": "PA",
    "SYN": "S",
    "SYN-ACK": "SA",
}

ip = IP(src="client", dst="server")  # <2>

sport = dport = 8080  # <3>
c0 = int(RandInt()) # <4>

tcp = TCP(sport=sport, dport=dport, flags=F["SYN"], seq=c0)  # <5>
packet = ip / tcp  # <6>
ans, unans = sr(packet, verbose=0)  # <7>

s0 = ans[0][1][TCP].fields["seq"]  # <8>

tcp = TCP(sport=sport, dport=dport, flags=F["ACK"], seq=c0 + 1, ack=s0 + 1)  # <9>
packet = ip / tcp
send(packet, verbose=0)  # <10>
# end::tcp_3_way_handshake[]

# tag::tcp_3_way_handshake_explanation[]
# <1> This dictionary holds verbose names of TCP flags as keys, to make them more understandable compared to their corresponding short names used by _scapy_.
#
# <2> The scapy's IP layer defines the source (client) and the destination (server) addresses.
# Note that the +client+ and the +server+ names are internally resolved to their IP addresses.
#
# <3> The client's (+sport+) and the server's (+dport+) TCP port numbers are defined.
# Both the client and the server use the same port number, each on its own machine.
#
# <4> The TCP initial sequence number for the client (c0) is set to a random integer value.
# The value of c0 is set, so it can be used for manual calculations of the client's sequence numbers.
# Note however, that a secure selection of the initial sequence number is more complex.footnote:[See https://datatracker.ietf.org/doc/html/rfc1948[RFC 1948].]
#
# <5> The scapy's TCP layer defines the SYN TCP segment, to be sent by the client to the server.
#
# <6> This line defines the IP packet, composed of IP and TCP scapy layers.
# The +/+ operator in scapy denotes a composition between two layers.
#
# <7> The TCP three-way handshake starts.
# The scapy's +sr()+ function is used to send and receive packets.
# The function returns a couple (tuple composed of two elements) of two lists.
# The first element, +ans+, is a list of couples +(packet sent, response)+, and the second element, +unans+, is a list of packets for which no response was received.
# Verbose printing of packet exchange progress is disabled, by setting +verbose=0+.
#
# <8> This line extracts the server's initial sequence number (s0) from the server response.
# Our code controls the client's initial sequence number (c0), but the server controls its own.
#
# <9> This line defines the TCP layer for the ACK TCP segment, to be sent by the client to the server.
#
# <10> The TCP three-way handshake finishes, by the client sending the ACK segment to the server.
# tag::tcp_3_way_handshake_explanation[]

# tag::tcp_send_receive_data[]
# Send "Hello" message to the server as TCP data with PSH-ACK flag
# The PSH flag is used to indicate that the message is complete
message = "Hello"
tcp = TCP(
    sport=sport, dport=dport, flags=F["PSH-ACK"], seq=c0 + 1, ack=s0 + 1
)
packet = ip / tcp / message
if message.encode() != packet[TCP].load:
    raise RuntimeError("Incorrect data sent")

# Wait for an ACK followed by PSH-ACK
# The multi parameter is set to True to indicate that multiple packets may be received
# The timeout parameter is set to 0.1 seconds to wait for an answer
ans, unans = sr(packet, multi=True, timeout=0.1, verbose=0)
answer = ans[1][1][TCP].payload.load
if answer.decode() != message:
    raise RuntimeError("Incorrect data received")
print(answer.decode(), end="")

# ACK the reception of "Hello" answer
tcp = TCP(
    sport=sport,
    dport=dport,
    flags=F["ACK"],
    seq=c0 + 1 + len(message),
    ack=s0 + 1 + len(answer),
)
packet = ip / tcp
send(packet, verbose=0)
# tag::tcp_send_receive_data[]

# tag::tcp_terminate_connection[]
# Send FIN to terminate the connection. The FIN is combined with ACK here,
# which a common practice to reduce the number of exchanged packets
tcp = TCP(
    sport=sport,
    dport=dport,
    flags=F["FIN-ACK"],
    seq=c0 + 1 + len(message),
    ack=s0 + 1 + len(answer),
)
packet = ip / tcp
ans, unans = sr(packet, verbose=0)

# Confirm termination of the connection by sending ACK
tcp = TCP(
    sport=sport,
    dport=dport,
    flags=F["ACK"],
    seq=c0 + 1 + len(message) + 1,
    ack=s0 + 1 + len(answer) + 1,
)
packet = ip / tcp
send(packet, verbose=0)
# end::tcp_terminate_connection[]
