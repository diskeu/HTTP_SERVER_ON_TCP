import socket
from Content_types import basic_content_types

class HTTP_Server():
    def __init__(self, host:str, port:int, bufsize: int = 1024, backlog: int = 5, response_Body_If_404:str | None = None) -> None:
        self.host = host
        self.port = port
        self.bufsize = bufsize
        self.backlog = backlog
        self.Routes = {}
        self.Methods = ["GET", "POST", "PUT", "DELETE"]
        self.existingRoute = False
        self.basic_content_types = basic_content_types
        self.response_Body_If_404 = response_Body_If_404

        # if no set 404 Response Body
        if not self.response_Body_If_404:
            self.response_Body_If_404 = "<h1>404<br>Page not Found</h1>"

        # Defining Page not Found response
        self.page_Not_Found_Response =(
            f"HTTP/1.1 404 not Found\r\n"
            f"Content-Type: text/html\r\n"
            "\r\n"
            f"{self.response_Body_If_404}"
        )
        return None
    
    def add_Route(self, path:str, handler:callable, response_Body:str, response_Content_Type: str ="text/html", body_Needed: bool = False) -> None:
        # checking if valid response Content Type
        if response_Content_Type in self.basic_content_types:
            pass
        else:
            response_Content_Type = "text/html"
        
        # updating dict
        self.Routes[path] = [handler, response_Body, response_Content_Type, body_Needed]
        self.existingRoute = True
        print(self.Routes)
        return None
    
    def call_Route(self, request:bytes) -> bytes:
        lines: list = request.decode().split("\r\n")
        print(lines)

        # get only header from list
        header = []
        for x in lines:
            if x != "":
                header.append(x)
            else:
                break

        # get only body from list
        seperation: int = lines.index("")
        body: str | None = lines[seperation+1]

        # defining
        requestLine: list = header[0].split(" ")
        method: str = requestLine[0]
        rout: str = requestLine[1]
        print("Request Line: "+str(requestLine))
        print("Method: "+method)
        print("Request rout: "+rout)

        # calling Route and defining variables
        if (rout in self.Routes) and (method in self.Methods):
            handler, response_Body, response_Content_Type, body_Needed = self.Routes[rout]
        else:
            print("Page Not found")
            return self.page_Not_Found_Response.encode()
        
        # calling Function if Bofy is needed with body parameter
        handler(body) if body_Needed and body else handler()
        
        # making full HTTP response
        HTTP_Response_str: str = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: {response_Content_Type}\r\n"
            "\r\n"
            f"{response_Body}"
        )
        HTTP_Response_binary: bytes = HTTP_Response_str.encode()
        return HTTP_Response_binary
    
    def boot_Server(self):
        # checking if a route exists
        if not self.existingRoute:
            raise "No Definied Route Error"
        
        # binding Server
        server_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_Socket.bind((self.host, self.port))
        server_Socket.listen(self.backlog)

        while True:
            client_Conn, client_Addr = server_Socket.accept()
            print(f"Connected with {client_Addr}")

            # checking for request
            request: bytes = client_Conn.recv(self.bufsize)
            
            # send response when rout is called
            if request:
                HTTP_Response_binary: bytes = self.call_Route(request)
                client_Conn.send(HTTP_Response_binary)
            else:
                client_Conn.close()

# Making Server Object
myServer = HTTP_Server("127.0.0.1", 8000)
print(myServer)

def myHandler(body):
    print("Handler...")
    print(f"Body: {body}")

with open("index.html", "r") as f:
    html = f.read()

# Defining my Routes
myServer.add_Route("/", myHandler, html, body_Needed=True)

# Booting Server
myServer.boot_Server()


    
    
            
        




# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def home():
#     return {"message": "Welcome to the Randomizer API"}
