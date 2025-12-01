import socket
import asyncio
import random

async def main():
    print("start event loop")
    await asyncio.sleep(2)
    print("end of funtion")

async def second():
    print("start second")
    await asyncio.sleep(2)
    print("end of second")

async def start():
    await asyncio.gather(main(), second())

asyncio.run(start())


class httpServer():
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def root(self):
        with open("index.html", "r") as f:
            file = f.read()
        self.client_socket.send(b"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"""+file.encode())

    def comment(self):
        with open("yourPost.html", "r") as f:
            Postfile = f.read()
        self.client_socket.send(b"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"""+Postfile.encode())

    def get_response(
        self, 
            response_Content_Type: str, 
            response_Body, 
            client_socket=None, 
            response_Status_Code=200, 
            response_Message="OK", 
            send=False
        ):

        if not client_socket:
            client_socket = self.client_socket
        
        response = (f"""
                    
            HTTP/1.1 {response_Status_Code} 
            {response_Message}
            \r\nContent-Type: {response_Content_Type}
            \r\n\r\n{response_Body}

        """)
        response = response.encode()

        if send:
            self.client_socket.send(response)
        else:
            pass
        return type(response)

    def endpoint(self):
        ...


    def main(self):
        server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)

        while True:

            self.client_socket, self.client_address = server_socket.accept()
            
            self.data = self.client_socket.recv(1024).decode()

            if self.data:

                self.lines = self.data.split("\r\n")
                self.requestline = self.lines[0].split(" ")
                
                self.method = self.requestline[0]
                self.endpoint = self.requestline[1]
                print(self.method)

                # GET /
                if self.method == "GET" and self.endpoint == "/":
                    self.root()
                
                # POST /comment
                elif self.method == "POST" and self.endpoint == "/Comment":
                    self.comment()
                    
            else:
                self.client_socket.close()

    def run(self):
        self.main()
        
        # self.handleClient(client_socket, client_address)

http_Server = httpServer("127.0.0.1", 8000)

http_Server.run()

print(http_Server.get_response("text/html", "<h1>Recieved</h1>", http_Server.client_socket, 200, "OK", send=False))

    
    

        



# import socket

# # Socket erstellen (TCP)
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # IP und Port binden
# server_socket.bind(('127.0.0.1', 12345))  # localhost:12345

# # Auf Verbindungen warten
# server_socket.listen(1)
# print("Warte auf Verbindung...")

# conn, addr = server_socket.accept()  # Verbindung akzeptieren
# print(f"Verbunden mit {addr}")

# # Daten empfangen
# data = conn.recv(1024)  # bis zu 1024 Bytes
# print(f"Empfangen: {data.decode()}")

# # Antwort senden
# conn.send(b"Hallo vom Server!")

# # Verbindung schließen
# conn.close()
# server_socket.close()


    # def blackjack(self):
    #     with open("blackjack.html", "r") as f:
    #         blackjackfile = f.read()
    #         number = random.randint(1, 6)
    #     if number != 6:
    #         status = "<h3>Still in the Game</h3>"
    #         blackjackfile = blackjackfile.replace("{{ number }}",f"<h2>{str(number)}</h2>")
    #         blackjackfile = blackjackfile.replace("{{ status }}",str(status))
    #     else:
    #         status = "<h3>You lost</h3>"
    #         blackjackfile = blackjackfile.replace("{{ number }}",f"<h2>{str(number)}</h2>")
    #         blackjackfile = blackjackfile.replace("{{ status }}",str(status)) 
    #     self.client_socket.sendall(b"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"""+blackjackfile.encode())