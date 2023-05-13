import socket
import threading
from lib import simple_hash


class FileServer:
    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', port))
        self.socket.listen(5)
        self.log = None  # to be used for logs
        self.storageNodes = [('127.0.0.1', 5001)]
        print(f"Server listening on port {port}")

    def start(self):

        try:
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
            conn.sendall(f'Thank you for loggin in user {userId}'.encode())
            while True:
                data = conn.recv(1024).decode()
                if not data or data == 'exit':
                    print('exiting from ', addr)
                    break
                # Handle the client request
                response = self.handle_request(data, userId)
                conn.sendall(response.encode())
            conn.close()
        except ConnectionResetError:
            print('Connection disrupted')

    def handle_request(self, data, userId):
        # Parse the client request and return the response
        splittedRequest = data.split()
        command = splittedRequest[0]
        match command:
            case 'create':
                pass
            case 'ls':
                pass
            case 'create':
    def request_storage_node(self, userId, message):
        storageNodeIp, storageNodePort = self.storageNodes(simple_hash(userId))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((storageNodeIp, storageNodePort))
            s.sendall(message.encode())
            response = s.recv(2048).decode()
        return response


if __name__ == '__main__':
    server = FileServer(8080)
    server.start()
