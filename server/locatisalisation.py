import json
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

class LocationHanderler(BaseHTTPRequestHandler):
    '''
    Class that handles the POST and GET requests from Unity.
    From POST requests moves robot that this server is running on
    '''
    positions = {}
    def do_GET(self):
        '''
        Handles GET requests
        '''
        print("received")
        data = json.dumps(self.positions)
        self.wfile.write(data)
        self.send_response(200)
        self.send_header("Content-Length", f"{len(data)}")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write("{}")

    def do_POST(self):
        '''
        Handles POST requests
        '''
        data = json.loads(self.rfile.read())
        self.positions[data["id"]] = {'x':data["x"],'y':data["y"],'theta':data["theta"]}

if __name__ == "__main__":
    host_name: str = "118.138.113.89"
    server_port: int = 8081

    server = ThreadingHTTPServer((host_name, server_port), LocationHanderler)

    print(f"Localisation server started\non http://{host_name}:{server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server")
    server.server_close()
    print("Server stopped")
