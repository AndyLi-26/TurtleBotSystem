import http.client
import json
from enum import Enum
import urllib.parse
from time import sleep
from math import atan, sqrt


AGENTS = {
    "1":"IP:PORT",
    "2":"IP:PORT",
    "3":"IP:PORT"
}
LOCALISATION_IP = "IP:PORT"
CONS_LOCAL = http.client.HTTPConnection(LOCALISATION_IP)
CONS_AGENTS = [http.client.HTTPConnection(i) for i in AGENTS.values()]
PRECISION = 0.5
INTERVAL = 1000
PATHS = [
    [(1, 0), (0, 0), (0, -1)],
    [(6, 0), (7, 0), (8, 0)],
    [(4, 4), (4, 5), (4, 6)]
]

timestep = 1
running = True
while running:
    positions = CONS_LOCAL.request("GET","/")
    running = False
    for agentId in AGENTS.keys():
        aPath = PATHS[AGENTS[agentId]]
        if len(aPath) < timestep:
            continue
        running = True
        
        pos = positions[agentId]
        if abs(pos['x'] - aPath[timestep - 1][0]) > PRECISION:
            print(f"turtlebot {agentId} has not reached goal")
            ###course correction
            pass
        if abs(pos['y'] - aPath[timestep - 1][1]) > PRECISION:
            print(f"turtlebot {agentId} has not reached goal")
            ###course correction
            pass

        ###DO MATHS###
        theta = pos['theta'] - atan((pos['y'] - aPath[timestep][1])/(pos['x'] - aPath[timestep][0]))  ###MATHS HERE
        dist =  sqrt(((pos['x'] - aPath[timestep][0])**2) + ((pos['y'] - aPath[timestep][1])**2))

        CONS_AGENTS.request("POST","/","{\"id\": "+agentId+",\"theta\": "+theta+ ",\"dist\": "+dist+"}")
        sleep(INTERVAL)
        timestep+=1

