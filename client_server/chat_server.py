import socket
import select
import sys

HEADER_LENGTH = 10

# checks for arguments
if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

# assign arguments to host address and port number
IP, PORT = sys.argv[1], int(sys.argv[2])

# create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()

# list of sockets for select.select()
sockets_list = [server_socket]

# list of connected clients - socket used as key, user header and name as data
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

# handles message receiving on server side
def receive_msg_info(client_socket):
    try:

        # receive "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # if no data was received, client gracefully closed the connection
        if not len(message_header):
            return False

        # convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # return an object with message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False

while True:
    try:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        # iterate over notified sockets
        for notified_socket in read_sockets:

            # if notified socket is a server socket - new connection, accept it
            if notified_socket == server_socket:

                # accept new connection
                client_socket, client_address = server_socket.accept()
                user = receive_msg_info(client_socket)

                # if False - client disconnected before he sent his name
                if user is False:
                    continue

                # Add accepted socket to select.select() list
                sockets_list.append(client_socket)

                # also save username and username header
                clients[client_socket] = user

                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

            # else existing socket is sending a message
            else:

                # receive message
                message = receive_msg_info(notified_socket)

                # if False, client disconnected, cleanup
                if message is False:
                    print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                    # remove from list for socket.socket()
                    sockets_list.remove(notified_socket)

                    # remove from our list of users
                    del clients[notified_socket]

                    continue

                # get user by notified socket
                user = clients[notified_socket]

                print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

                # iterate over connected clients and broadcast message
                for client_socket in clients:

                    # exclude sent it to sender
                    if client_socket != notified_socket:

                        # send user and message (both with their headers)
                        # we are reusing here message header sent by sender, and saved username header send by user when he connected
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

        # handle socket exceptions
        for notified_socket in exception_sockets:

            # Remove from list for socket.socket()
            sockets_list.remove(notified_socket)

            # Remove from our list of users
            del clients[notified_socket]

    # close program on keyboard interrupt
    except KeyboardInterrupt:
        print("Server closed")
        sys.exit()

    # print any other errors and close program
    except Exception as e:
        print(f"Error in server: {str(e)}")
        sys.exit()
