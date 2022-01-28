#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):    

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        startLine = self.getStartLine(self.data)

        response = ""
        body = ""

        try:
        # check HTTP method, startLine[0]
            if(startLine[0] == "GET"):
                (file_path, status, content_type) = self.handleGetRequest(startLine[1])
                f = open(file_path, "r")
                body = f.read()

                response += "HTTP/1.1 %s OK Not FOUND!\r\n" % str(status)
                response += content_type
                response += "Content-Length: %s\r\n" % str(len(body))

            else:
                response += "HTTP/1.1 405 Method Not Allowed\r\n"
        except:
            response += "HTTP/1.1 404 Path Not Found\r\n"

        response += "Connection: close\r\n"
        response += body
        self.request.sendall(bytearray(response,'utf-8'))
    
    # Return the HTTP request start line as a str[]
    def getStartLine(self, raw_data):
        data_list = raw_data.decode("utf-8").split("\r\n")

        print("COMPONENTS", data_list)

        # first element in data_list contains the HTTP request start line
        # ex: GET /index.html HTTP/1.1

        startLine = data_list[0].split()
        return startLine

    # Return tuple: (file_path, status, content_type)
    def handleGetRequest(self, target: str):
        root_path = os.path.realpath("./www")

        # let default status be 200 and default content type be text/html
        file_path = ""
        status = 200
        content_type_base = "Content-Type: text/%s; charset=UTF-8\r\n"
        content_type = content_type_base % "html"
   
        if ".css" in target:
            # content type css
            content_type = content_type_base % "css"
            file_path += self.doesFileExist(root_path, target)
        elif ".html" in target:
            # content type html
            file_path += self.doesFileExist(root_path, target)
        elif target == "/":
            # redirect to index.html
            file_path += root_path + "/index.html"
        elif target[-1] == "/":
            # target is a path. Check if it exists.
            file_path += self.doesFileExist(root_path + target, "index.html")
        else:
            # target is a path, but it needs to be redirected
            status = 301
            file_path += self.doesFileExist(root_path + target, "/index.html")
        
        return (file_path, status, content_type)
    
    def doesFileExist(self, path, file):
        full_file_path = path + file
        if(os.path.isfile(full_file_path)):
            return full_file_path
        else:
            raise Exception("Invalid target: {target} does not exist")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
