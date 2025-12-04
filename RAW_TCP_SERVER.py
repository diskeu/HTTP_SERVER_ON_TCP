import socket
from Content_types import basic_content_types

class HTTP_Server():
    def __init__(self, host:str, port:int,status_Code: int=200, status_Msg: str= "Ok", bufsize: int = 1024, backlog: int = 5, response_Body_If_404:str | None = None) -> None:
        self.host = host
        self.port = port
        self.status_Code = status_Code
        self.status_Msg = status_Msg
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
    
    def add_Route(self, path:str, handler:callable, method_defined:str, response_Body:str, response_Content_Type: str ="text/html", body_Needed: bool = False, easy_Form_Handler: bool = False) -> None:
        # checking if valid response Content Type
        if response_Content_Type in self.basic_content_types:
            pass
        else:
            response_Content_Type = "text/html"
        
        # defining easy_Form_Handler
        self.easy_Form_Handler = easy_Form_Handler

        # updating dict | method route gets called with
        self.Routes[path] = [handler, response_Body, method_defined, response_Content_Type, body_Needed]
        self.existingRoute = True
        print(self.Routes)
        return None
    
    # splits Form body like name=Tim&comment=AHH into dict
    def Form_Handler(self, form_Body:str) -> dict:
        # splited_Form_Elements: dict = {key: val for x in form_Body.split("&") for key, val in x.split("=")}

        splited_Form_Elements: dict = {}
        splitedBody: list = form_Body.split("&")
        for x in splitedBody:
            key, val = x.split("=")
            splited_Form_Elements[key] = val
        
        return splited_Form_Elements
            
        
    
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
        print(f"--body--{body}--")

        # defining
        requestLine: list = header[0].split(" ")
        method: str = requestLine[0]
        rout: str = requestLine[1]
        print("Request Line: "+str(requestLine))
        print("Method: "+method)
        print("Request rout: "+rout)

        # calling Route and defining variables
        if (rout in self.Routes) and (method in self.Methods):
            handler, response_Body, method_defined, response_Content_Type, body_Needed = self.Routes[rout]

            # checking if the request method is the same as the defiened method
            if method_defined == method_defined:
                pass
            
        else:
            print("Page Not found")
            return self.page_Not_Found_Response.encode()
        
        # calling Function if Bod.y is needed with body parameter
        if body_Needed:
            
            # if easy form Handler
            if self.easy_Form_Handler:
                handler(self.Form_Handler(body))

            else:
                handler(body)
        else:
            handler()
        
        # making full HTTP response
        HTTP_Response_str: str = (
            f"HTTP/1.1 {self.status_Code} {self.status_Msg}\r\n"
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

def myHandler():
    print("Handler...")

def myHandler2(body):
    print("Handler2...")
    print(f"Body: {body}")

with open("index.html", "r") as f:
    html = f.read()

with open("yourPost.html", "r") as f:
    htmlPost = f.read()

# Defining my Routes
myServer.add_Route(path="/", handler=myHandler, method_defined="GET", response_Body=html, body_Needed=False)
myServer.add_Route(path="/Comment", handler=myHandler2, method_defined="POST", response_Body=htmlPost, body_Needed=True, easy_Form_Handler=True)

# Booting Server
myServer.boot_Server()


    
    
            
        




# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def home():
#     return {"message": "Welcome to the Randomizer API"}


