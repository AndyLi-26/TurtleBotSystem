import json
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import os
import subprocess

IP = "192.168.11.101"
SPEED = 0.3

con = http.client.HTTPConnection(SERVER_IP)

class TurtleHanderler(BaseHTTPRequestHandler):
    '''
    Class that handles the POST and GET requests from Unity.
    From POST requests moves robot that this server is running on
    '''
    executing = None

    def do_GET(self):
        '''
        Handles GET requests from controller
        '''
        pass

    def do_POST(self):
        '''
        Handles POST requests from controller
        '''
        if self.executing is not None:
            print("terminating previous instructions")
            self.executing.kill()
        url = urlparse(self.path)
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        rotate = f'ros2 action send_goal /rotate_angle irobot_create_msgs/action/RotateAngle "angle: {data["theta"]}\nmax_rotation_speed: {SPEED}"'
        drive = f'ros2 action send_goal /drive_distance irobot_create_msgs/action/DriveDistance "distance: {data["dist"]}\nmax_translation_speed: {SPEED}"'
        TONULL = " > /dev/null" #This quiets output of ros2 commands
        self.executing = subprocess.run(rotate + TONULL + " && " + drive + TONULL,shell=True)
        if self.executingprint.returncode == 0:
            print ("successfully completed instructions")
            con.request("POST","/status","{\"id\": "+agentId+",\"status\": STOPPED}")
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write("{}")




if __name__ == "__main__":
    host_name: str = IP #Turtlebots IP
    server_port: int = 8081 #PORT 8080 conflicts with action server

    server = ThreadingHTTPServer((host_name, server_port), TurtleHanderler)

    print(f"Server started on turtlebot\non http://{host_name}:{server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server")
    server.server_close()
    print("Server stopped")