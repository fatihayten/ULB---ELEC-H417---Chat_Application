import pip
import pwinput as pwinput
import pwinput
import socket
import select
import errno
import sys

HEADER_LENGTH = 10

IP = "169.254.58.41"
PORT = 1234


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


client_socket.connect((IP, PORT))


def new_connection_client() :
    intention = input(client_socket.recv(1024).decode())
    client_socket.send(intention.encode('utf-8'))

    if intention == 'r' :
        new_username = input(client_socket.recv(1024).decode())
        client_socket.send(new_username.encode('utf-8'))
        username_response_decoded = client_socket.recv(1024).decode()
        if username_response_decoded == 'This username is already in use, please select another username: ' :
            print ('This username is already in use, please start from beginning and  select another username : ')
            new_connection_client()
        if username_response_decoded == 'Enter your new password (Your password should contain at least 8 characters, a capital letter and a number ):   ' :
            password1 = pwinput.pwinput(username_response_decoded)
            client_socket.send(password1.encode('utf-8'))
            first_password_response = client_socket.recv(1024).decode()
            if first_password_response == 'Your password should contain at least 8 characters, a capital letter and a number, start again ' :
                print('Your password should contain at least 8 characters, a capital letter and a number, start again ')
                new_connection_client()
            if first_password_response == 'Enter your new password again: ' :
                password2 = pwinput.pwinput(first_password_response)
                client_socket.send(password2.encode('utf-8'))

            password_response = client_socket.recv(1024)
            password_response = password_response.decode()
            if password_response == 'Registration is successful, now you have to login' :
                print(f'You have successfully registered with username {new_username}')
                new_connection_client()

            if password_response == 'Your passwords do not match! Start from selecting a new username ':
                print('Your passwords do not match! Start from selecting a new username ')
                new_connection_client()

    if intention == 'l':
        username = client_socket.recv(1024)
        username = input(username.decode())
        client_socket.send(username.encode('utf-8'))

        username_response = (client_socket.recv(1024)).decode()

        if username_response == 'Enter your password : ' :
            password = pwinput.pwinput(username_response)
            client_socket.send(password.encode('utf-8'))
            password_response = (client_socket.recv(1024)).decode()
            if password_response == 'Login is successful, you can start chating :) ' :
                print(password_response)

            if password_response == 'Your password is wrong! Start from the beginning ' :
                print(password_response)
                new_connection_client()
        if username_response == 'Your username could not been found, you are directed to the main page... ' :
            print('Your username could not been found, you are directed to the main page... ')
            new_connection_client()
    if intention == 'c':
        print("Your connection is being closed, see you again :(")
        # sys.exit()
    else :
        print("You have entered invalid key, try again")
        new_connection_client()
while True:

    new_connection_client()
    new_connection_client()

    input('STOP HIER')

    # If message is not empty - send it
    if message:

        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)

    try:
        # Now we want to loop over received messages (there might be more than one) and print them
        while True:

            # Receive our "header" containing username length, it's size is defined and constant
            username_header = client_socket.recv(HEADER_LENGTH)

            # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            # Convert header to int value
            username_length = int(username_header.decode('utf-8').strip())

            # Receive and decode username
            username = client_socket.recv(username_length).decode('utf-8')

            # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            # Print message
            print(f'{username} > {message}')

    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: '.format(str(e)))
        sys.exit()

