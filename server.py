import socket
import select
import hashlib  # To encrypt passwords
import bcrypt
import sys
import re

# password reference : https://howtodoinjava.com/python/modules/python-bcrypt-hash-password/
# password check : https://stackoverflow.com/questions/41117733/validation-of-a-password-python
HEADER_LENGTH = 10
IP = "169.254.58.41"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen(5)

sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and name as data
clients = {}
all_in_one = {}

print(f'Listening for connections on {IP}:{PORT}...')

def new_connection_server(client_socket) :

    client_socket.send(('Press "l" to log in or press "r" to new registration or press "c" to close the connection: ').encode('utf-8'))
    intention =  client_socket.recv(1024).decode()

    if intention == 'r':
        client_socket.send(str.encode('Enter your new username: '))
        new_username = client_socket.recv(1024).decode()

        if new_username in all_in_one.keys():
            client_socket.send(str.encode('This username is already in use, please select another username: '))
            new_connection_server(client_socket)
        else :
            client_socket.send(str.encode('Enter your new password (Your password should contain at least 8 characters, a capital letter and a number ):   '))
            new_password_1 = client_socket.recv(1024).decode()
            if (len(new_password_1)) < 8 or (re.search('[0-9]', new_password_1) is None) or (re.search('[A-Z]', new_password_1) is None) :
                client_socket.send(str.encode('Your password should contain at least 8 characters, a capital letter and a number, start again '))
                new_connection_server(client_socket)

            client_socket.send(str.encode('Enter your new password again: '))
            new_password_2_encoded = client_socket.recv(1024)
            new_password_2_decoded = new_password_2_encoded.decode()
            if new_password_1 == new_password_2_decoded :
                passwd = new_password_2_encoded
                hashed = bcrypt.hashpw(passwd, bcrypt.gensalt())
                all_in_one[new_username] = {'password' : hashed , 'IP_address' : client_address , 'activity': False}
                client_socket.send(str.encode('Registration is successful, now you have to login'))
                new_connection_server(client_socket)

            else :
                client_socket.send(str.encode('Your passwords do not match! Start from selecting a new username '))
                new_connection_server(client_socket)
    if intention == 'l':
        client_socket.send(str.encode('Enter your username: '))  # Request Username
        username = client_socket.recv(1024).decode()

        if username in all_in_one:
            client_socket.send(str.encode('Enter your password : '))
            password_from_client_encoded = client_socket.recv(1024)
            password_from_client_decoded = password_from_client_encoded.decode()
            passwd_from_client = password_from_client_encoded
            matched = bcrypt.checkpw(passwd_from_client, all_in_one[username]['password'])
            if (matched == True) and (all_in_one[username]['activity'] != True):
                client_socket.send(str.encode('Login is successful, you can start chating :) '))
                all_in_one[username] = {'activity': 'true'}

            else :
                client_socket.send(str.encode('Your password is wrong! Start from the beginning '))
                new_connection_server(client_socket)

        else:
            client_socket.send(str.encode('Your username could not been found, you are directed to the main page... '))
            new_connection_server(client_socket)
    if intention == 'c' :
        print("Your connection is being closed, see you again :(")
    else :
        print("You have entered invalid key, try again")
        new_connection_server(client_socket)
# Handles message receiving
def receive_message(client_socket):

    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        client_socket, client_address = server_socket.accept()

        new_connection_server(client_socket)
        continue


