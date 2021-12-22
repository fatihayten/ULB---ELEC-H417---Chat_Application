import socket
import bcrypt # To encrypt the passwords
import re
import threading # To run some functions for different clients simultaneously

# password reference : https://howtodoinjava.com/python/modules/python-bcrypt-hash-password/
# password check : https://stackoverflow.com/questions/41117733/validation-of-a-password-python
# server code : https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/
IP = "169.254.58.41" # You should write your own IPv4 address
PORT = 1234          # Port is defined randomly, if an error arises, just change it

# Following 4 functions are taken from: https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Setup the socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # To overcome the "Address already in use" issue
server_socket.bind((IP, PORT)) # Binding
server_socket.listen() # Listening new connections

clients = {}
all_in_one = {}

print(f'Listening for connections on {IP}:{PORT}...')

def new_connection_server(client_socket):
    client_socket.send(('Press "l" to log in, Press "r" to register:    ').encode('utf-8'))
    intention = client_socket.recv(1024).decode()

    if intention == 'r':
        client_socket.send(str.encode('Select your username: '))
        new_username = client_socket.recv(1024).decode()

        if new_username in all_in_one.keys():
            client_socket.send(str.encode('This username is being used, please select another... '))
            new_connection_server(client_socket)
        else:
            client_socket.send(str.encode(
                'Enter your password (Your password should contain at least 8 characters, a capital letter and a number ):   '))
            new_password_1 = client_socket.recv(1024).decode()

            # To check password requirements (https://stackoverflow.com/questions/41117733/validation-of-a-password-python)
            if (len(new_password_1)) < 8 or (re.search('[0-9]', new_password_1) is None) or (re.search('[A-Z]', new_password_1) is None):
                client_socket.send(str.encode(
                    'Your password should contain at least 8 characters, a capital letter and a number... '))
                new_connection_server(client_socket)

            client_socket.send(str.encode('Enter your password again:  '))
            new_password_2_encoded = client_socket.recv(1024)
            new_password_2_decoded = new_password_2_encoded.decode()
            if new_password_1 == new_password_2_decoded:  # To check whether two passwords are the same or not
                passwd = new_password_2_encoded
                hashed = bcrypt.hashpw(passwd, bcrypt.gensalt()) # Encryption of the password (https://howtodoinjava.com/python/modules/python-bcrypt-hash-password/)
                all_in_one[new_username] = {'password': hashed}
                clients[new_username] = client_socket
                client_socket.send(str.encode('Registration is successful, now you have to login'))
                new_connection_server(client_socket)
            else:
                client_socket.send(str.encode('Your passwords do not match!'))
                new_connection_server(client_socket)
    elif intention == 'l':
        client_socket.send(str.encode('Enter your username:  '))  # Request Username
        username = client_socket.recv(1024).decode()

        if username in all_in_one:
            client_socket.send(str.encode('Enter your password :  '))
            password_from_client_encoded = client_socket.recv(1024)
            password_from_client_decoded = password_from_client_encoded.decode()
            passwd_from_client = password_from_client_encoded
            matched = bcrypt.checkpw(passwd_from_client, all_in_one[username]['password'])
            if (matched == True): # To check whether the password is correct or not
                client_socket.send(str.encode('Login is successful, you can start chating:)  '))
            else:
                client_socket.send(str.encode('Your password is wrong!'))
                new_connection_server(client_socket)

        else:
            client_socket.send(str.encode('Your username could not been found... '))
            new_connection_server(client_socket)


#  A function to converting a list to string (https://www.geeksforgeeks.org/python-program-to-convert-a-list-to-string/)
def listToString(s):
    str1 = " "
    return (str1.join(s))


#  Message sending and receiving function
def chating(client_socket):
    connected = True
    while connected:
        message = message_check()
        print(message)

        if message != 0:
            receiver_username = (message.split(' ', 3))[1]
            if receiver_username in clients.keys():
                receiver_address = clients[receiver_username]
                public_key = (message.split(' ', 3))[2]
                receiver_address.send(str.encode(listToString(public_key)))
                write_read_check = client_socket.recv(1024).decode()
                m1 = client_socket.recv(1024).decode()
                print("The message :   ") #  The message between clients are printed to validate that the message is encrypted
                print(m1)
                receiver_address.send(str.encode(m1))
            else:
                continue

def message_check():
    message_recv = client_socket.recv(1024).decode()
    message_length = (message_recv.split(' ', 3))[0]

    if message_length == "0":
        return 0
    else:
        return message_recv

#  Converting the keys of a dictionary to a string (https://www.geeksforgeeks.org/python-get-dictionary-keys-as-a-list/)
def getList(dict):
    return list(dict.keys())

#  Sending the online clients list to a client
def online_clients(client_socket):
    client_socket.send(str.encode('Usernames of online clients right now are as follows: \n'))
    client_socket.send(str.encode(listToString(getList(clients))))

while True:

    client_socket, client_address = server_socket.accept()
    new_connection_server(client_socket)
    online_clients(client_socket)
    # Using "threading" to run chating() function for different clients simultaneously (https: // www.techwithtim.net / tutorials / socket - programming /)
    thread = threading.Thread(target=chating, args=(client_socket,))
    thread.start()



