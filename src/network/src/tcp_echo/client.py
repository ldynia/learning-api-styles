"""TCP ECHO client"""

import socket


BUFSIZE_BYTES = 8

# Create an IPv4 TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    # Bind client socket to specific port
    # Normally the client does not bind to a specific port
    # and instead selects the port at random
    client_socket.bind(("", 8080))
    # Connect to the server
    client_socket.connect(("server", 8080))
    # Send data (encoded as bytes) to the server
    client_socket.send("Hello".encode())
    # Receive the data (encoded as bytes) from the server
    data = client_socket.recv(BUFSIZE_BYTES)
    print(data.decode(), end="")
