import os
from socket import *
import threading


class StorageServer:
    def __init__(self, root_dir, host='localhost', port=8000):
        self.root_dir = root_dir
        self.host = host
        self.port = port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

    def start(self):
        self.server_socket.listen(5)
        print(f'Storage server started on {self.host}:{self.port}')

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(
                f'Accepted connection from {client_address[0]}:{client_address[1]}')
            t = threading.Thread(target=self.handle_client,
                                 args=(client_socket,))
            t.start()

    def handle_client(self, client_socket):
        request = client_socket.recv(1024).decode()
        request_type, filename, data = request.split('||')
        if request_type == 'PUT':
            self.put_file(filename, data)
            response = 'File stored successfully!'
        elif request_type == 'GET':
            file_data = self.get_file(filename)
            if file_data:
                response = file_data
            else:
                response = 'File not found'
        else:
            response = 'Invalid request'
        client_socket.send(response.encode())
        client_socket.close()

    def get_file(self, filename):
        try:
            with open(os.path.join(self.root_dir, filename), 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return None

    def put_file(self, filename, data):
        with open(os.path.join(self.root_dir, filename), 'wb') as f:
            f.write(data)
