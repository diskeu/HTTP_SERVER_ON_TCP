import socket
import time

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(("127.0.0.1", 8888))

for _ in range(1000):
    client_socket.send(b"test client 1")
    time.sleep(1)
    client_socket.settimeout(3)
    try:
        data = client_socket.recv(1024)
        print(data.decode())
    except socket.timeout:
        continue
client_socket.close()