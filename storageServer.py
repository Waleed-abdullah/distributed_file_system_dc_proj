import os
from socket import *
import threading
import sys
import time
from lib import logger, compute_formatted_time


class StorageServer:
    def __init__(self, root_dir, host='localhost', port=8000):
        self.root_dir = root_dir
        self.host = host
        self.port = port
        self.synchronizedClockOffset = None
        self.log = "storageServerLog.txt"
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

    def create_root_dir(self):
        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)

    def synchronize_clock(self):
        socket, _ = self.server_socket.accept()
        request = socket.recv(1024).decode()
        if request == "synchronize":
            current_time = time.time()
            socket.send(str(current_time).encode())
            socket.close()

            # we accept a new connection here as previous
            # socket gets closed on the server
            socket, _ = self.server_socket.accept()
            clockOffset = socket.recv(1024).decode()
            self.synchronizedClockOffset = float(clockOffset)
            socket.close()

    def start(self):
        self.create_root_dir()
        self.server_socket.listen(5)
        print(f'Storage server started on {self.host}:{self.port}')

        self.synchronize_clock()

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(
                f'Accepted connection from {client_address[0]}:{client_address[1]}')
            t = threading.Thread(target=self.handle_client,
                                 args=(client_socket,))
            t.start()

    def handle_client(self, client_socket):
        request = client_socket.recv(1024).decode()
        splittedRequest = request.split(':')
        userId, command = splittedRequest[0], splittedRequest[1]
        userBasePath = self.get_user_base_path(userId)

        # log request to the server
        logMessage = f"\n{userId} : {compute_formatted_time(self.synchronizedClockOffset)} : {command} : {userBasePath}"
        logger(self.log, logMessage)

        match command:
            case 'ls':
                response = self.list_directory_structure(userBasePath)
            case 'create':
                pass
            case 'write':
                pass
            case 'read':
                pass
            case 'delete':
                pass
            case 'rename':
                pass
            case other:
                response = 'invalid Request'
        client_socket.send(response.encode())
        client_socket.close()

    def get_user_base_path(self, userId):
        userBasePath = f'{self.root_dir}\\{userId}_DIR'
        if not os.path.exists(userBasePath):
            os.mkdir(userBasePath)
        return userBasePath

    def get_file(self, userBasePath, pathToFile):
        try:
            with open(os.path.join(userBasePath, pathToFile), 'rb') as f:
                return f.read().decode()
        except FileNotFoundError:
            return None

    def put_file(self, userBasePath, pathToFile,  data):
        with open(os.path.join(userBasePath, pathToFile), 'wb') as f:
            f.write(data.encode())

    def list_directory_structure(self, path):
        outputString = ''
        for root, dirs, files in os.walk(path):
            for name in files:
                outputString += os.path.join(root, name) + '\n'
            for name in dirs:
                outputString += os.path.join(root, name) + '\n'
        return outputString


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Enter rootDirForServer and portNo.')
        exit()
    rootDir, portNo = sys.argv[1], int(sys.argv[2])
    storageServer = StorageServer(rootDir, port=portNo)
    storageServer.start()
