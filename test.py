import socket, ssl

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secure_sock = ssl.create_default_context().wrap_socket(client_socket, server_hostname="www.savewalterwhite.com")
secure_sock.connect(("www.savewalterwhite.com", 443))

request = b"GET / HTTP/1.1\r\nHost: www.savewalterwhite.com\r\n\r\n"
secure_sock.send(request)

response = secure_sock.recv(4096)
print(response.decode())

secure_sock.close()

