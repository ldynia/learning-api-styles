"""TCP ECHO server"""

# tag::tcp_echo_server[]
import socket


BUFSIZE_BYTES = 8  # <1>
CLOSE_WAIT = 8  # <1>

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:  # <2>
    server_socket.bind(("", 8080))  # <3>
    server_socket.listen()  # <4>
    while True:  # <5>
        print("Waiting for a new connection from client ...")
        conn_socket, client_address = server_socket.accept()  # <6>
        while True:  # <7>
            data = conn_socket.recv(BUFSIZE_BYTES)  # <8>
            if data:
                data_decoded = data.decode()  # <9>
                print(f"Received {data_decoded} from client {client_address}")
                conn_socket.send(data)  # <10>
                print(f"Sent {data_decoded} to client {client_address}")
            conn_state = conn_socket.getsockopt(socket.SOL_TCP, socket.TCP_INFO)
            if conn_state == CLOSE_WAIT:  # <11>
                print(f"Client {client_address} closed connection")
                conn_socket.close()
                break
# end::tcp_echo_server[]
# tag::tcp_echo_server_explanation[]
# <1> This block defines parameters used by the socket API.
#
# <2> The program creates a server's TCP socket for the IP protocol version 4 (+AF_INET+).
# The +server_socket+ is created using the +with+ context manager.
# The purpose of the context manager is to close the socket when the code within the +with+ block is finished, even if errors occur.
#
# <3> The +bind+ method (system call) binds the server socket to any network interface on the server host, and 8080 port.
#
# <4> The server starts listening on the socket for a new client connection.
#
# <5> The infinite outer loop is used to await for a new client connection.
#
# <6> When a client connection appears, it is accepted by the +accept+ method (system calls).
# This method creates, and returns the server connection socket for the connected client, along with the connected client tuple (IP address, port).
#
# <7> This infinite inner loop waits for the client to send data or to close the connection.
#
# <8> The server's connection socket receives data (encoded as bytes) from the client.
# The buffer is of +BUFSIZE_BYTES+ size, and this size must be a power of two.
#
# <9> The +decode+ method converts the data from bytes to string, in order for the data to be printed.
#
# <10> The server sends the encoded data back to the client, on the existing connection socket.
#
# <11> This condition monitors the state of the TCP connection established with the client.
# If the connection is in +CLOSE_WAIT+ state, the connection socket is closed, and the server's TCP socket returns to waiting for a new client connection.
#If the connection is in +CLOSE_WAIT+ state, the connection socket is closed, and the server's TCP socket returns to waiting for a new client connection.
# end::tcp_echo_server_explanation[]
