import socket
import threading
import select
import errno
import sys

HEADER_LENGTH = 10

# check for arguments
if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

# assign arguments to host address and port number
IP, PORT = sys.argv[1], int(sys.argv[2])

# ask user for username
my_username = input("Username: ")

# create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((IP, PORT))
client_socket.setblocking(False)

# prepare username and header and send them
# encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

# function for receiving messages
def receive_messages():
    while True:

        try:

            # receive our header containing username length, size is defined and constant
            username_header = client_socket.recv(HEADER_LENGTH)

            # if we received no data, server gracefully closed a connection
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            # convert header to int value
            username_length = int(username_header.decode('utf-8').strip())

            # receive and decode username
            username = client_socket.recv(username_length).decode('utf-8')

            # do the same for message (as username was being received, so was the whole message, so no need to check its length)
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            # print message
            print("")
            print("\x1b[1A\x1b[2K", end="")
            print(f'{username} > {message}')
            
        except IOError as e:
            # on nonblocking connections, when there is no incoming data, an error will be raised
            # check for both - if its the first one - thats expected, means no incoming data, continue
            # if its a different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

            # nothing was received
            continue

        except Exception as e:
            # any other exception - something happened, exit
            print('Reading error: '.format(str(e)))
            sys.exit()

# receive messages on seperate thread to prevent input nonblocking
receive_thread = threading.Thread(target = receive_messages, daemon = True)
receive_thread.start()

# send messages on main thread
while True:

    try:

        # wait for user to input a message
        message = input(f'{my_username} > ')

        # if message is not empty - send it
        if message:

            # encode message to bytes, prepare header and convert to bytes, then send
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message) 
 
    except Exception as e:
        # print any caught error
        print('Reading error: '.format(str(e)))
        sys.exit()
