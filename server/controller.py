import http.client
import json
from time import sleep
from math import atan, sqrt, pi
import argparse
import asyncio


def get_args():
    parser = argparse.ArgumentParser(prog = 'ControllerServer',description='Acts as a control server, requests location data and sends actions to agents',epilog='That\'s all folks')
    parser.add_argument('file',type=str,help='Config file in JSON format of scenario')
    arg = parser.parse_args()   
    print(f'Reading file {arg.file}')
    with open(arg.file) as f:
        j = json.load(f)

    print(f'Sending starting positions to localisation server\nmake sure localisation server at {j["LOCALISATION_IP"]} is online')
    print("NOT IMPLEMENTED YET")

    return j['AGENTS'], j['LOCALISATION_IP'], j['PRECISION'], j['PATHS']

AGENTS,LOCALISATION_IP,PRECISION,PATHS = get_args()
print('Recieved configuration')
CONS_LOCAL = http.client.HTTPConnection(LOCALISATION_IP)
CONS_AGENTS = {i:http.client.HTTPConnection(AGENTS[i]) for i in AGENTS}
timesteps = {i:1 for i in AGENTS}


def getPositions():
    CONS_LOCAL.request("GET","/")
    r = CONS_LOCAL.getresponse()
    if r.status != 200:
        print(f"error code {r.status} recieved")
        print("check if valid GetRequest")
    return json.loads(r.read())
    
async def main(agentId,pos):
    timestep = timesteps[agentId]
    aPath = PATHS[agentId]
    if len(aPath) <= timestep:
        return

    pos = positions[agentId]
    if pos['status'] != "STOPPED":
        return

    if abs(pos['x'] - aPath[timestep - 1][0]) > PRECISION:
        print(f"turtlebot {agentId} has not reached goal")
        ###course correction
        pass
    if abs(pos['y'] - aPath[timestep - 1][1]) > PRECISION:
        print(f"turtlebot {agentId} has not reached goal")
        ###course correction
        pass

    ###DO MATHS###
    run = (pos['x'] - aPath[timestep][0])
    rise = (pos['y'] - aPath[timestep][1])
    if run == 0:
        theta = pos['theta'] - pi
    else:
        theta = pos['theta'] - atan(rise/run)
    dist =  sqrt(((pos['x'] - aPath[timestep][0])**2) + ((pos['y'] - aPath[timestep][1])**2))

    print(f'moving {agentId} with distance = {dist} and theta = {theta}')

    CONS_AGENTS[agentId].request("POST","/","{\"id\": "+str(agentId)+",\"theta\": "+str(theta)+ ",\"dist\": "+str(dist)+"}")
    r = CONS_AGENTS[agentId].getresponse()
    data = json.loads(r.read())
    CONS_AGENTS[agentId].close()

    CONS_LOCAL.request("POST","/",json.dumps(pos | {"id":agentId,"status":data["status"]}))
    CONS_LOCAL.close()
        

running = True
while running:
    positions = getPositions()
    running = False
    for agentId in AGENTS:
        asyncio.create_task(main(agentId,positions))
    sleep(0.2)
