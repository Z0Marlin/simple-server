from server import TCPServer, Client
import os
import sys
from http import HTTPStatus

def echo_request(request):
    close_connection  = True
    br_response = "HTTP/1.0 "+str(HTTPStatus.BAD_REQUEST.value)+" Bad Request\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Error 400 Bad Request</h1></body></html>\r\n\r\n"
    nf_response = " "+str(HTTPStatus.NOT_FOUND.value)+" Not found\r\nContent-Type: text/html\r\n\r\n<html><body><h1>Error 404 File Not Found</h1></body></html>\r\n\r\n"
    ok_response = " "+str(HTTPStatus.OK.value)+"OK\r\nContent-Type: text/plain\r\n\r\n"
    request = request.decode()
    lines = request.split("\r\n")
    first_line = lines[0]
    words = first_line.split()
    try:
        req = {"method":words[0],"resource":words[1],"http-version":words[2]}
    except IndexError:
        return (br_response.encode("utf-8"), close_connection)
    if req["method"] != "GET":
        return (br_response.encode("utf-8"), close_connection)

    nf_response = req["http-version"]+nf_response

    resource = req["resource"]
    if resource == "/":
        filename  = "index.html"
        ok_response = ok_response.replace("plain","html")
    else:    
        _, filename = os.path.split(resource)
    try:
        f = open(filename,"r")
    except FileNotFoundError:
        return (nf_response.encode("utf-8"), close_connection)
    ok_response = req["http-version"] + ok_response
    ok_response = ok_response + f.read()
    if ok_response.endswith("\r\n"):
        ok_response += "\r\n"
    else:
        ok_response += "\r\n"*2
    return (ok_response.encode("utf-8"), close_connection)

def main():
    if len(sys.argv)<4:
        print("Usage: python3 myscript.py <server|client> <IP> <PORT>")
    else:
        if sys.argv[1] == "server":
            server = TCPServer((sys.argv[2],int(sys.argv[3])), echo_request)
            server.start_server()
            print('Server Started')
            print('Press CTRL+D to stop')
            while True:
                try:
                    input()
                except EOFError:
                    server.stop_server()
                    print('Server stopped')
                    break
        elif sys.argv[1] == "client":
            client = Client()
            client.connect((sys.argv[2],int(sys.argv[3])))
            client.talk_to_sever()


if __name__ == "__main__":
    main()