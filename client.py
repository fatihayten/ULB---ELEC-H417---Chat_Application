import pwinput # To hide the passwords while entering to the system in stars (like ∗∗∗∗∗)
import socket
import random # To select random public key

# Enter the IP and Port numbers of the server that you want to connect
IP = "169.254.58.41"
PORT = 1234

# list of prime numbers, we wanted to use it in encryption
prime_list=[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
our_own_key = random.choice(prime_list)

# Following 2 functions are taken from: https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/?completed=/server-chatroom-sockets-tutorial-python-3/
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Setup the socket
client_socket.connect((IP, PORT))  # Connect to server

# This function is explained in server.py code in more detail
def new_connection_client() :
    intention = input(client_socket.recv(1024).decode())
    client_socket.send(intention.encode('utf-8'))

    if intention == 'r' :
        new_username = input(client_socket.recv(1024).decode())
        client_socket.send(new_username.encode('utf-8'))
        username_response_decoded = client_socket.recv(1024).decode()
        if username_response_decoded == 'This username is being used, please select another... ':
            print ('This username is being used, please select another... ')
            new_connection_client()
        elif username_response_decoded == 'Enter your password (Your password should contain at least 8 characters, a capital letter and a number ):   ' :
            password1 = pwinput.pwinput(username_response_decoded)
            client_socket.send(password1.encode('utf-8'))
            first_password_response = client_socket.recv(1024).decode()
            if first_password_response == 'Your password should contain at least 8 characters, a capital letter and a number... ' :
                print('Your password should contain at least 8 characters, a capital letter and a number... ')
                new_connection_client()
            elif first_password_response == 'Enter your password again:  ':
                password2 = pwinput.pwinput(first_password_response)
                client_socket.send(password2.encode('utf-8'))

            password_response = client_socket.recv(1024)
            password_response = password_response.decode()
            if password_response == 'Registration is successful, now you have to login' :
                print(f'You have successfully registered with username {new_username}')
                new_connection_client()

            elif password_response == 'Your passwords do not match!':
                print('Your passwords do not match!')
                new_connection_client()

    if intention == 'l':
        username = client_socket.recv(1024)
        username = input(username.decode())
        client_socket.send(username.encode('utf-8'))

        username_response = (client_socket.recv(1024)).decode()

        if username_response == 'Enter your password :  ' :
            password = pwinput.pwinput(username_response)
            client_socket.send(password.encode('utf-8'))
            password_response = (client_socket.recv(1024)).decode()
            if password_response == 'Login is successful, you can start chating:)  ' :
                print(password_response)
            elif password_response == 'Your password is wrong!' :
                print(password_response)
                new_connection_client()
        elif username_response == 'Your username could not been found... ':
            print('Your username could not been found... ')
            new_connection_client()

#  Message sending and receiving function
def chating():
     while True:
        print("Write the username of the person that you want to chat")
        receiver=input()
        message = receiver+" "+str(our_own_key) # create a str containing the receiver and our public key


        if receiver == "":
            length=0
            received_public_key = (client_socket.recv(1024)).decode()
            received_public_key = received_public_key.replace(" ", "") # remove the white spaces
            key_product= int(received_public_key) * our_own_key    # Creating a new key using the client's own key and the received key (of the other client)
            write_read_check = input("press 1 to send message, 0 to listen")
            if write_read_check == "1":
                client_socket.send(("handle message").encode('utf-8')) # Warn the server, a message is coming
                message_will_be_encrypted = input("Write your message: ")
                encrypted_message = ""

                # Encoding the message using multiplication of two clients' keys
                # (https://medium.com/@sadatnazrul/diffie-hellman-key-exchange-explained-python-8d67c378701c)
                for c in message_will_be_encrypted:
                    encrypted_message += chr(ord(c) + key_product)
                client_socket.send(encrypted_message.encode('utf-8'))
            if write_read_check == "0": # Warn the server, we are waiting for a message
                client_socket.send(("send message").encode('utf-8'))
                received_encrypted_message = (client_socket.recv(1024)).decode()
                decrypted_message = ""

                # Decoding the message using multiplication of two clients' keys
                # (https://medium.com/@sadatnazrul/diffie-hellman-key-exchange-explained-python-8d67c378701c)
                for c in received_encrypted_message:
                    decrypted_message += chr(ord(c) - key_product)
                print(decrypted_message)

        else:
            length=len(message)
        # send a str containing the length of the message, receiver's username and our public key
        client_socket.send((str(length) +" " + receiver +" " + str(our_own_key)).encode('utf-8'))

def message_check():
    message_recv = client_socket.recv(1024).decode()
    return message_recv

#  Getting the online clients list from the server
def online_clients():
    print("Online clients that you can send message are :   \n")
    print((client_socket.recv(1024)).decode())

while True:
    new_connection_client()
    online_clients()
    chating()









