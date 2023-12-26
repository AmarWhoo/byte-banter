import sys
import socket
import threading
import select
import errno

HEADER_LENGTH = 10

# create a socket for the server
def create_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen()

    print(f'Server listening on port {PORT}...')
    
    return server_socket

# connect to an existing server
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    
    return client_socket

# check for arguments
if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

# assign arguments to host address and port number
IP, PORT = sys.argv[1], int(sys.argv[2])

my_username = input("Username: ")

try:

    # Try connecting to an existing server
    client_socket = connect_to_server()
    print(f"Connected to server at {IP}:{PORT}")

except ConnectionRefusedError:
    
    # If connection fails, create a server and connect to it
    print("No existing server found. Creating a new server...")
    server_socket = create_server()
    client_socket = connect_to_server()

client_socket.setblocking(False)

# prepare username and header and send them
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)


