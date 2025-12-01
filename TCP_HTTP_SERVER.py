import socket

def root():
    with open("index.html", "r") as f:
        file = f.read()
    return file

class HTTP_Server():
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.routes = {}

    def Http_response(
        self, 
            response_Content_Type: str, 
            response_Body: str, 
            client_socket=None, 
            response_Status_Code=200, 
            response_Message="OK", 
            send=False
        ) -> bytes:

        response = (

            f"HTTP/1.1 {response_Status_Code} {response_Message}\r\n"
            f"Content-Type: {response_Content_Type}\r\n"
            "\r\n"
            f"{response_Body}"

        )

        response = response.encode()

        if client_socket and send:
            self.client_socket.send(response)
        else:
            pass
        return response
    
    def add_Route(self, 
        path:str,
        handler:callable,
        response,
        method:str) -> dict:
        
        self.routes[path] = handler
        return self.routes

    def call_Endpoint(self, http_GET_request:str):
        lines = http_GET_request.split("\r\n")
        requestline = lines[0].split(" ")
                
        method = requestline[0]
        endpoint = requestline[1]
        

    def Boot_Server(self):
        server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)

        response = self.Http_response("text/html", File, self.client_socket,200, "OK", send=True)
        self.add_Route("/", root, response)
        print("Response:"+response.decode())
        while True:

            self.client_socket, self.client_address = server_socket.accept()
            
            self.request = self.client_socket.recv(1024).decode()
            print("Request: "+self.request)

            File = self.call_Endpoint(self.request)


            self.client_socket.close()


    def run(self):
        self.Boot_Server()

http_Server = HTTP_Server("127.0.0.1", 8000)

http_Server.run()