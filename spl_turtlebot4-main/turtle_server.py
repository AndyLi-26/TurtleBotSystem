import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import os
import subprocess

SPEED = 0.3

class TurtleHanderler(BaseHTTPRequestHandler):
    '''
    Class that handles the POST and GET requests from Unity.
    From POST requests moves robot that this server is running on
    '''
    executing = None

    def do_GET(self):
        '''
        Handles GET requests from Unity
        '''
        pass

    def do_POST(self):
        '''
        Handles POST requests from Unity
        '''
        if self.executing is not None:
            print("terminating previous instructions")
            self.executing.kill()
        url = urlparse(self.path)
        data = json.loads(self.rfile.read())
        rotate = f'ros2 action send_goal /rotate_angle irobot_create_msgs/action/RotateAngle "angle: {data["theta"]}\nmax_rotation_speed: {SPEED}"'
        drive = f'ros2 action send_goal /drive_distance irobot_create_msgs/action/DriveDistance "distance: {data["dist"]}\nmax_translation_speed: {SPEED}"'
        TONULL = " > /dev/null"
        self.executing = subprocess.run(rotate + TONULL + " && " + drive + TONULL,shell=True)
        print("successfully completed instructions")




if __name__ == "__main__":
    host_name: str = "192.168.1.124"
    server_port: int = 8080

    server = ThreadingHTTPServer((host_name, server_port), TurtleHanderler)

    print(f"Server started on turtlebot\non http://{host_name}:{server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server")
    server.server_close()
    print("Server stopped")
