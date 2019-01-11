import socket
import threading
import select
import logging

BUFFER_SIZE = 2048

logging.basicConfig(filename = 'server.log', filemode = 'a',format = "%(levelname)s:%(asctime)s:%(name)s:%(message)s")
logger_serv = logging.getLogger("server")
logger_cli = logging.getLogger("client")
logger_serv.setLevel(logging.INFO)
logger_cli.setLevel(logging.INFO)

class TCPServer(object):

    def __init__(self, server_address, request_handler):
        self.server_address = server_address
        self.request_handler = request_handler
        self._listening_socket = None
        self._active_connections = {}
        self.server_active = False
        self._aux_write_sock = None
        self._aux_read_sock = None
        self._listenet_thread = None
        
    def start_server(self):
        logger_serv.info("Starting Server")
        self._listening_socket = socket.socket()
        self._listening_socket.setblocking(0)
        self._listening_socket.bind(self.server_address)
        self._listening_socket.listen()
        self.server_active = True
        self._aux_write_sock, self._aux_read_sock = socket.socketpair()
        self._listenet_thread = threading.Thread(target=self._listen_for_clients)
        self._listenet_thread.start()
        logger_serv.info("Server Started at "+str(self.server_address))

    def _listen_for_clients(self):
        while self.server_active:
            readable_sockets, _, _ = select.select([self._listening_socket, self._aux_read_sock],[],[])
            if self._aux_read_sock in readable_sockets:
                break
            client_socket, addr = self._listening_socket.accept()
            self._start_connection(client_socket, addr)
            
    def _start_connection(self, client_socket: socket.socket, address: tuple):
        logger_serv.info("Establishing new connection with "+str(address))
        aux_write_sock, aux_read_sock = socket.socketpair()
        t = threading.Thread(target=self._handle_client, args=(client_socket, aux_read_sock, address))
        self._active_connections[t] = aux_write_sock
        t.start()
        logger_serv.info("New connection with "+str(address))
            

    def _handle_client(self, client_socket: socket.socket, aux_read_sock: socket.socket, address: tuple):
        while self.server_active:
            readable_sockets, _, _ = select.select([client_socket, aux_read_sock],[],[])
            if aux_read_sock not in readable_sockets:
                try:
                    recieved_data = client_socket.recv(BUFFER_SIZE)
                except ConnectionResetError:
                    logger_serv.warn("Connection Reset Error occured while trying to recieve from a closed connection.")
                if not recieved_data:
                    logger_serv.debug("Client closed network. Recieved 0 bytes")
                    break
                logger_serv.info("Message recieved from "+str(address))
                send_data, close_conn = self.request_handler(recieved_data)
                if send_data:
                    client_socket.sendall(send_data)
                    logger_serv.info("Message sent to "+str(address))
                if close_conn:
                    break
            else:
                client_socket.close()
                aux_read_sock.close()
                return
        client_socket.close()
        aux_read_sock.close()
        self._active_connections.pop(threading.current_thread()).close()
        logger_serv.info("Connection closed with "+str(address))

    def _end_connection(self, connection_thread: threading.Thread):
        aux_write_sock = self._active_connections[connection_thread]
        aux_write_sock.close()
        if connection_thread.is_alive():
            connection_thread.join()
        

    def stop_server(self):
        logger_serv.info("Stopping server")
        self.server_active = False
        for thread in self._active_connections:
            self._end_connection(thread)
        logger_serv.info("All connections stopped")
        self._active_connections.clear()
        self._aux_write_sock.close()
        if self._listenet_thread.is_alive():
            self._listenet_thread.join()
        self._listening_socket.close()
        self._aux_read_sock.close()
        logger_serv.info("Server stopped")

class Client(object):

    def __init__(self):
        self.socket = None
        self.target_address = None

    def connect(self, address, timeout = 60):
        self.socket = socket.socket()
        self.target_address = address
        self.socket.settimeout(timeout)
        self.socket.connect(address)
        logger_cli.info("Connected to "+str(address))
    
    def talk_to_sever(self):
        while True:
            try:
                send_data = input("Enter message for server : ")
            except EOFError:
                break
            self.socket.send(send_data.encode("utf-8"))
            logger_cli.info("Message sent to "+str(self.target_address))
            try:
                recieved_data = self.socket.recv(BUFFER_SIZE)
                assert recieved_data
            except socket.timeout:
                logger_cli.info("Connection timed out")
                self.disconnect()
                return
            except AssertionError:
                logger_cli.info("Server closed the connection")
                self.disconnect()
                return
            logger_cli.info("Message recieved from "+str(self.target_address))
            print("Message from "+str(self.target_address)+" : "+recieved_data.decode())
        self.disconnect()
    
    def disconnect(self):
        self.socket.close()
        logger_cli.info("Disconnected from "+str(self.target_address))
        self.target_address = None


        


    

    



        
            

            
