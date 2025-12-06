import socket
import asyncio
import threading
import time
import queue
import inspect
from Content_types import basic_content_types
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
            
        
    
    def call_Route(self, request:bytes, future) -> bytes:
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
        
        # Function that returns Future with page_Not_Found_Response
        def page_Not_Found_Action():
            print("Page Not found")
            future.set_result(self.response_Body_If_404)
            return # leaving function

        # calling Route and defining variables and checking if the request method is the same as the defiened method
        if (rout in self.Routes) and (method in self.Methods):
            handler, method_defined, response_Content_Type, body_Needed, easy_Form_Handler = self.Routes[rout]

            if method != method_defined:
                print(f"Definied Method = {method_defined}")
                print(f"Used Method = {method}")
                page_Not_Found_Action()
                return 
        
        else:
            page_Not_Found_Action()
            return
            
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
        # defining Response Body Length
        content_Length = len(response_Body.encode("utf-8")) if response_Body else 0
                    
        # making full HTTP response
        HTTP_Response_str: str = (
            f"HTTP/1.1 {self.status_Code} {self.status_Msg}\r\n"
            f"Content-Type: {response_Content_Type}\r\n"
            f"Content-Length: {content_Length}"
            "\r\n\r\n"
            f"{response_Body}"
        )

        HTTP_Response_binary: bytes = HTTP_Response_str.encode()
        print("------")
        print(HTTP_Response_binary)
        print("------")
        future.set_result(HTTP_Response_binary)
        return
        
        

    
    async def handle_Client(self, reader, writer):
        try: 
            while True: 
                # checking for request
                request: bytes = await asyncio.wait_for(reader.read(self.bufsize), timeout=self.timeout)
                
                # if client disconnects break
                if not request:
                    break

                # defining Response Future                
                Response_Future = Future()
                
                # starting thread
                thread = threading.Thread(target=self.call_Route, args=(request, Response_Future))
                thread.start()

                # geting response 404 Response | other
                HTTP_Response_binary = await asyncio.wrap_future(Response_Future)

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

async def slow():
    return htmlPost

def myHandler():
    print("Handler...")
    return html

def myHandler2(body):
    print("Handler2...")
    print(f"Body: {body}")
    return htmlPost

async def myHandler3():
    await asyncio.sleep(3)
    print("Handler3...")
    return html

# Defining my Routes
myServer.add_Route(path="/", handler=myHandler, method_defined="GET", body_Needed=False)
myServer.add_Route(path="/test", handler=myHandler, method_defined="GET", body_Needed=False)
myServer.add_Route(path="/Comment", handler=myHandler2, method_defined="POST", body_Needed=True, easy_Form_Handler=True)
myServer.add_Route(path="/slow", handler=myHandler3, method_defined="GET", body_Needed=False, easy_Form_Handler=False)
# myServer.add_Route(path="/slow", handler=slow, method_defined="GET", response_Body="HTTP/1.1 200 OK\r\n\r\nSlow Response", body_Needed=False, easy_Form_Handler=False)

# Booting Server
asyncio.run(myServer.boot_Server())

    
    
            
        




# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def home():
#     return {"message": "Welcome to the Randomizer API"}

