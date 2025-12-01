import socket

class HTTP_Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.bufsize = 1024
        self.backlog = 5
        self.Routes = {}
        self.Methods = ["GET", "POST", "PUT", "DELETE"]
        self.page_Not_Found_Response = ""
        self.existingRoute = False
    
    def add_Route(self, path, handler, response_Body):
        self.Routes[path] = [handler, response_Body]
        self.existingRoute = True
        print(self.Routes)
    
    def call_Route(self, request):
        lines = request.decode().split("\r\n")

        # get only header from list
        header = []
        for x in lines:
            if x != "":
                header.append(x)
            else:
                break

        # get only body from list
        seperation = lines.index("")
        body = lines[seperation+1:]

        # defining
        requestLine = header[0].split(" ")
        method = requestLine[0]
        rout = requestLine[1]
        print("Request Line: "+str(requestLine))
        print("Method: "+method)
        print("Request rout: "+rout)

        # calling Route
        if (rout in self.Routes) and (method in self.Methods):
            handler, response_Body = self.Routes[rout]
        else:
            print("Page Not found")
            return self.page_Not_Found_Response.encode()
        
        # calling Function
        handler()
        
        # making full HTTP response
        HTTP_Response_str = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: text/html\r\n"
            "\r\n"
            f"{response_Body}"
        )
        HTTP_Response_binary = HTTP_Response_str.encode()
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
            request = client_Conn.recv(self.bufsize)
            
            # send response when rout is called
            if request:
                HTTP_Response_binary = self.call_Route(request)
                client_Conn.send(HTTP_Response_binary)
            else:
                client_Conn.close()

myServer = HTTP_Server("127.0.0.1", 8000)

def myHandler():
    print("Handler...")

myServer.add_Route("/", myHandler, "<h1>You Recieved this from a Raw Tcp server</h1>")
myServer.boot_Server()
            
        




# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def home():
#     return {"message": "Welcome to the Randomizer API"}
