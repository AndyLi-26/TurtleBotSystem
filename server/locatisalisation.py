import json
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


POSITIONS = {
    "r0":{"x":1,"y":0,"theta":0,"status":"STOPPED"}, 
    "r1":{"x":2,"y":0,"theta":0,"status":"STOPPED"},
    "r2":{"x":3,"y":4,"theta":0,"status":"STOPPED"},
    "s3":{"x":4,"y":4,"theta":0,"status":"STOPPED"},
}

class LocationHanderler(BaseHTTPRequestHandler):
    '''
    Class that handles the POST and GET requests from Unity.
    From POST requests moves robot that this server is running on
    '''
    positions = POSITIONS

    def do_GET(self):
        '''
        Handles GET requests
        '''
        data = json.dumps(self.positions)
        self.send_response(200)
        self.send_header("Content-Length", f"{len(data)}")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(data,'UTF-8'))

    def do_POST(self):
        '''
        Handles POST requests
        '''
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        for robot in data["robots"]:
            self.positions[robot["id"]] = robot

        print(self.positions)
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length","0")
        self.end_headers()
        self.wfile.write(bytes())


if __name__ == "__main__":
    host_name: str = "192.168.11.3"
    server_port: int = 8079

    server = ThreadingHTTPServer((host_name, server_port), LocationHanderler)

    print(f"Localisation server started\non http://{host_name}:{server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server")
    server.server_close()
    print("Server stopped")
