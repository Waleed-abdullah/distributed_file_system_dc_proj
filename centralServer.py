import socket
import threading
import time
from lib import simple_hash, logger, berkeley, compute_formatted_time


class FileServer:
    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', port))
        self.socket.listen(5)
        self.log = "centralServerLog.txt"
        self.storageNodes = [('127.0.0.1', 8000)]
        self.synchronizedClockOffset = None
        print(f"Server listening on port {port}")

    def start(self):
        try:
            self.synchronize_storage_nodes()
            while True:
                conn, addr = self.socket.accept()
                print(f"Connected by {addr}")
                t = threading.Thread(
                    target=self.handle_client, args=(conn, addr))
                t.start()
        except KeyboardInterrupt:
            print("Server stopped by user")
            self.socket.close()
            exit()

    def handle_client(self, conn, addr):
        try:
            conn.sendall('Enter userId: '.encode())
            userId = conn.recv(1024).decode()
            userStorageNode = simple_hash(userId, len(self.storageNodes))
            conn.sendall(f'Thank you for logging in user {userId}'.encode())
            while True:
                data = conn.recv(1024).decode()
                if not data or data == 'exit':
                    print('exiting from ', addr)
                    break
                # Handle the client request
                response = self.handle_request(data, userId, userStorageNode)
                conn.sendall(response.encode())
            conn.close()
        except ConnectionResetError:
            print('Connection disrupted')

    def handle_request(self, data, userId, userStorageNode):
        # Parse the client request and return the response
        splittedRequest = data.split()
        command = splittedRequest[0]

        # log request to the server
        logMessage = f"\n{userId} : {compute_formatted_time(self.synchronizedClockOffset)} : {command}"
        logger(self.log, logMessage)

        match command:
            case 'ls':
                if len(splittedRequest) != 1:
                    return 'command Usage(lists the entire storage area for user): ls'
                return self.request_storage_node(f'{userId}:ls', userStorageNode)
            case 'create':
                if len(splittedRequest) != 3:
                    return 'command Usage: create type<dir,file> path'
                type, path = splittedRequest[1], splittedRequest[2]
                return self.request_storage_node(f'{userId}:create:{type}:{path}', userStorageNode)
            case 'write':
                if len(splittedRequest) < 3:
                    return 'command Usage: write path\\to\\file data'
                filePath = splittedRequest[1]
                fileData = ' '.join(splittedRequest[2:])
                return self.request_storage_node(f'{userId}:write:{filePath}:{fileData}', userStorageNode)
            case 'read':
                if len(splittedRequest) != 2:
                    return 'command Usage: read path\\to\\file'
                filePath = splittedRequest[1]
                return self.request_storage_node(f'{userId}:read:{filePath}', userStorageNode)
            case 'delete':
                if len(splittedRequest) != 2:
                    return 'command Usage: delete path\\to\\file_or_dir'
                path = splittedRequest[1]
                return self.request_storage_node(f'{userId}:delete:{path}', userStorageNode)
            case 'rename':
                if len(splittedRequest) != 3:
                    return 'command Usage: rename path\\to\\file_or_dir new_name'
                path = splittedRequest[1]
                newName = splittedRequest[2]
                return self.request_storage_node(f'{userId}:rename:{path}:{newName}')
            case other:
                return 'invalid request'

    def request_storage_node(self, message, userStorageNode):
        storageNodeIp, storageNodePort = self.storageNodes[userStorageNode]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((storageNodeIp, storageNodePort))
            s.sendall(message.encode())
            response = s.recv(2048).decode()
        return response

    def synchronize_storage_nodes(self):
        storageNodeClocks = []
        for storageNode in self.storageNodes:
            storageNodeIp, storageNodePort = storageNode
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((storageNodeIp, storageNodePort))
                s.sendall("synchronize".encode())
                nodeClock = s.recv(2048).decode()
                storageNodeClocks.append(float(nodeClock))
                s.close()

        synchronizedTime = berkeley(storageNodeClocks)

        for index, storageNode in enumerate(self.storageNodes):
            storageNodeIp, storageNodePort = storageNode
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((storageNodeIp, storageNodePort))
                synchronizedTimeOffset = synchronizedTime - \
                    storageNodeClocks[index]
                s.sendall(str(synchronizedTimeOffset).encode())
                s.close()

        self.synchronizedClockOffset = synchronizedTimeOffset


if __name__ == '__main__':
    server = FileServer(8080)
    server.start()
