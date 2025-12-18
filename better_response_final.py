import socket
import asyncio
import threading
import time
import datetime
import queue
import inspect
import csv
import os
import mimetypes
from Content_types import basic_content_types
from encoding_needed import mimetype_encoding_needed
from concurrent.futures import Future

class HTTP_Server():
    def __init__(self, host:str, port:int,status_Code: int=200, status_Msg: str= "OK",bufsize: int = 1024, response_Body_If_404:str | None = None, response_Body_If_Timeout: str | None = None, timeout:float | int = 200) -> None:
        self.host = host
        self.port = port
        self.status_Code = status_Code
        self.status_Msg = status_Msg
        self.bufsize = bufsize
        self.Routes = {}
        self.Methods = ["GET", "POST", "PUT", "DELETE"]
        self.existingRoute = False
        self.basic_content_types = basic_content_types
        self.encoding_needed = mimetype_encoding_needed
        self.response_Body_If_404 = response_Body_If_404
        self.timeout = timeout

        # if no set 404 Response Body
        if not self.response_Body_If_404:
            self.response_Body_If_404 = "<h1>404<br>Page not Found</h1>"

        # Defining Page not Found response
        self.page_Not_Found_Response =(
            f"HTTP/1.1 404 not Found\r\n"
            f"Content-Type: text/html\r\n"
            "\r\n\r\n"
            f"{self.response_Body_If_404}"
        )

        # if no set 404 Response Body
        if not response_Body_If_Timeout:
            self.response_Body_If_Timeout = "<h1>Timeout</h1>"
        # Defining Timeout response
        self.timeout_Response =(
            f"HTTP/1.1 408 Request Timeout\r\n"
            f"Content-Type: text/html\r\n"
            "\r\n\r\n"
            f"{self.response_Body_If_Timeout}"
        )
        
        return None
    
    def add_Route(self, path:str, handler:callable, method_defined:str, response_Content_Type: str ="text/html", body_Needed: bool = False, easy_Form_Handler: bool = False) -> None:
        # checking if valid response Content Type
        if response_Content_Type in self.basic_content_types:
            pass
        else:
            response_Content_Type = "text/html"

        # updating dict | method route gets called with
        self.Routes[path] = [handler, method_defined, response_Content_Type, body_Needed, easy_Form_Handler]
        self.existingRoute = True
        return None        
    
    # splits Form body like name=Tim&comment=AHH into dict
    def Form_Handler(self, form_Body:str) -> dict:
        # splited_Form_Elements: dict = {key: val for x in form_Body.split("&") for key, val in x.split("=")}

        splited_Form_Elements: dict = {}
        splitedBody: list = form_Body.split("&")
        for x in splitedBody:
            key, val = x.split("=")
            splited_Form_Elements[key] = val
        print(splited_Form_Elements)
        
        return splited_Form_Elements
    
    def log_request(self, Time, status_Code: int, Method: str, Route: str, IP: str) -> None:
        line = [Time, status_Code, Method, Route, IP]
        with open("log.csv", "a", newline="") as f:
            csv_Writer = csv.writer(f)
            csv_Writer.writerow(line)
    
    def mount_static(self, rout: str, path: str) -> None:
        # adds a route for every file in the directory
        for x in os.listdir(path):
            file_Type, _ = mimetypes.guess_file_type(path+x)
            with open(path+x, "rb") as f:
                content = f.read()
            self.add_Route(path=rout+"/"+x, handler=lambda content=content: content, method_defined="GET", response_Content_Type=file_Type)        
        
    # gets items from request makes response, gives back future
    def call_Route(self, request:bytes, response_Future, client_ip) -> Future[any]:
        # spliting lines from request
        lines: list = request.decode().split("\r\n")

        # get only header from list
        header:list = []
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
        
        # Function that returns Response_Container with page_Not_Found_Response
        def page_Not_Found_Action():
            print("Page Not found")

            # defining datetime
            now = datetime.datetime.now()
            request_Time = now.strftime("%Y:%m:%d - %X")

            # calling function that writes in log
            self.log_request(request_Time, 404, method, rout, client_ip)

            # seting future
            response_Future.set_result(self.page_Not_Found_Response.encode())
            return # leaving function

        # calling Route and defining variables and checking if the request method is the same as the defiened method
        if (rout in self.Routes) and (method in self.Methods):
            handler, method_defined, response_Content_Type, body_Needed, easy_Form_Handler = self.Routes[rout]

            if method != method_defined:
                print(f"Definied Method = {method_defined}")
                print(f"Used Method = {method}")
                page_Not_Found_Action()
                return  # leaving thread
        
        else:
            page_Not_Found_Action()
            return # leaving thread
            
        # checking the type of Function and getting response Body from it
        # calling Function if Body is needed with body parameter
        if inspect.iscoroutinefunction(handler):
            if body_Needed:
                
                # if easy form Handler
                if easy_Form_Handler:
                    response_Body =  asyncio.run(self.Form_Handler(body))

                else:
                    response_Body = asyncio.run(handler(body))
            else:
                response_Body = asyncio.run(handler())
        else:
            if body_Needed:
                
                # if easy form Handler
                if easy_Form_Handler:
                    response_Body = handler(self.Form_Handler(body))

                else:
                    response_Body = handler(body)
            else:
                response_Body = handler()

        # defining Response Body and Length
        if type(response_Body) == str:
            response_Body = response_Body.encode()
        content_Length = len(response_Body) if response_Body else 0
        HTTP_Response_Body_bytes: bytes = response_Body

        # making HTTP response Header
        HTTP_Response_Header_str: str = (
            f"HTTP/1.1 {self.status_Code} {self.status_Msg}\r\n"
            f"Content-Type: {response_Content_Type}\r\n"
            f"Content-Length: {content_Length}"
            "\r\n\r\n"
        )

        HTTP_Response_Header_bytes: bytes = HTTP_Response_Header_str.encode()

        HTTP_Response_binary: bytes = HTTP_Response_Header_bytes + HTTP_Response_Body_bytes

        # defining datetime
        now = datetime.datetime.now()
        request_Time = now.strftime("%Y:%m:%d - %X")

        # calling function that writes in log
        self.log_request(request_Time, 200, method, rout, client_ip)

        # seting future
        response_Future.set_result(HTTP_Response_binary)
        return # leaving thread
    
    async def handle_Client(self, reader, writer):
        try: 
            while True: 
                # checking for request
                request: bytes = await asyncio.wait_for(reader.read(self.bufsize), timeout=self.timeout)
                
                # if client disconnects break
                if not request:
                    break
                
                # defining IP adress
                client_ip = writer.get_extra_info("peername")[0]
                
                # defining Future
                response_Future: Future[any] = Future()

                # starting thread
                thread: threading.Thread = threading.Thread(target=self.call_Route, args=(request, response_Future, client_ip))
                thread.start()

                # waiting for future to respond
                HTTP_Response_binary: bytes = await asyncio.wrap_future(response_Future)

                writer.write(HTTP_Response_binary)
                await writer.drain()
                
        except asyncio.TimeoutError:
            writer.write(self.timeout_Response.encode())
        except (BrokenPipeError, ConnectionResetError):
            print("BrokenPipeError or ConnectionResetError")
        finally:
            writer.close()
            await writer.wait_closed()

    
    async def boot_Server(self):
        # checking if a route exists
        if not self.existingRoute:
            raise "No Definied Route Error"
        
        # binding Server
        server_Socket = await asyncio.start_server(self.handle_Client, self.host, self.port)
        async with server_Socket:
            await server_Socket.serve_forever()
    
    async def start_Server(self):
        asyncio.run(self.boot_Server())

# Making Server Object
myServer = HTTP_Server("127.0.0.1", 8000)
print(myServer)


with open("index.html", "r") as f:
    html = f.read()

with open("yourPost.html", "r") as f:
    htmlPost = f.read()

def myHandler():
    print("Handler...")
    return html.encode()

def myHandler2(body):
    print("Handler2...")
    print(f"Body: {body}")
    return f"<h1>Thank you for your post {body["name"]}</h1>"

async def myHandler3(body):
    await asyncio.sleep(7)
    print("Handler3...")
    return htmlPost.encode()

def myHandler4():
    with open("static/php.png", "rb") as f:
        img = f.read()
    return {"name": True}

# Defining my Routes
myServer.mount_static("/static", "static/")
myServer.add_Route(path="/", handler=myHandler, method_defined="GET", body_Needed=False)
myServer.add_Route(path="/test", handler=myHandler, method_defined="GET", body_Needed=False)
myServer.add_Route(path="/Comment", handler=myHandler2, method_defined="POST", body_Needed=True, easy_Form_Handler=True)
myServer.add_Route(path="/slow", handler=myHandler3, method_defined="GET", body_Needed=True, easy_Form_Handler=False)
# myServer.add_Route(path="/static/img", handler=myHandler4, method_defined="GET", response_Content_Type="image/png")
# myServer.add_Route(path="/slow", handler=slow, method_defined="GET", response_Body="HTTP/1.1 200 OK\r\n\r\nSlow Response", body_Needed=False, easy_Form_Handler=False)

# Booting Server
asyncio.run(myServer.boot_Server())

    
    
            
        




# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def home():
#     return {"message": "Welcome to the Randomizer API"}

