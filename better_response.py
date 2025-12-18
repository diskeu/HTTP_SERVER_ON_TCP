from better_response_final import HTTP_Server
import asyncio

def handler():
    return "<h1>Home</h1>"
http_Server = HTTP_Server("127.0.0.1", 8000)

http_Server.add_Route(path="/home", handler=handler, method_defined="GET")

asyncio.run(http_Server.boot_Server())
