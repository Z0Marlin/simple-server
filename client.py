import socket as sk 
import sys

BUFFER_SIZE = 1024

def client(connection: sk.socket):
    while True:
        try:
            send_data = input('Enter message : ')
        except EOFError:
            print()
            break
        connection.send(send_data.encode('utf-8'))
        recieved_data = connection.recv(BUFFER_SIZE)
        if not recieved_data:
            break
        print('Server respond :',recieved_data.decode())
    print('Connection terminated')

if __name__ == "__main__":
    ip = input('Enter IP : ')
    port = int(input('Enter PORT : '))
    client_socket = sk.socket()
    try:
        client_socket.connect((ip, port))
    except ConnectionError:
        print('An error occured while connectiong')
        sys.exit()
    client(client_socket)


