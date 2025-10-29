import http.client
import json
from time import sleep
from math import atan2, sqrt, pi, dist
import argparse
import asyncio
import aiohttp


def get_args():
    parser = argparse.ArgumentParser(prog = 'ControllerServer',description='Acts as a control server, requests location data and sends actions to agents',epilog='That\'s all folks')
    parser.add_argument('config',type=str,help='Config file in JSON format of scenario')
    parser.add_argument('path',type=str,help='Path file in JSON format')
    arg = parser.parse_args()   
    print(f'Reading file {arg.config}')
    with open(arg.config) as f1:
        j = json.load(f1)

    print(f'Reading file {arg.path}')
    with open(arg.path) as f2:
        paths = json.load(f2)

    print(f'Sending starting positions to localisation server\nmake sure localisation server at {j["LOCALISATION_IP"]} is online')
    print("NOT IMPLEMENTED YET")

    return j['AGENTS'], j['LOCALISATION_IP'], j['PRECISION'], paths


AGENTS,LOCALISATION_IP,PRECISION,PATHS = get_args()
print('Recieved configuration')
CONS_LOCAL = http.client.HTTPConnection(LOCALISATION_IP)
timesteps = {i:1 for i in AGENTS}


def getPositions():
    CONS_LOCAL.request("GET","/")
    r = CONS_LOCAL.getresponse()
    if r.status != 200:
        print(f"error code {r.status} recieved")
        print("check if valid GetRequest")
    return json.loads(r.read())
    
def scheduled(curId,positions):
    AVOIDANCE_RADIUS = 0.6
    x = PATHS[curId][timesteps[curId]][0]
    y = PATHS[curId][timesteps[curId]][1]
    #THIS takes advantage of not being able to go between points
    for id in AGENTS:
        if id == curId:
            return True ##GIVES this agent prioity.
        
        curClose = dist((x,y),(positions[id]['x'],positions[id]['y'])) < AVOIDANCE_RADIUS
        furClose = dist((x,y),(PATHS[id][timesteps[id]][0],PATHS[id][timesteps[id]][1])) < AVOIDANCE_RADIUS
        
        if curClose and furClose:
            return False
    return True

        

async def moveRobot(agentId,positions):
    timestep = timesteps[agentId]
    aPath = PATHS[agentId]
    if len(aPath) <= timestep:
        return

    pos = positions[agentId]
    if pos['status'] != "STOPPED":
        return

    if not scheduled(agentId,positions):
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
    run = aPath[timestep][0] - pos['x']
    rise = aPath[timestep][1] - pos['y']
    theta = atan2(rise,run)
    dist =  sqrt(((pos['x'] - aPath[timestep][0])**2) + ((pos['y'] - aPath[timestep][1])**2))

    print(f'moving {agentId} with distance = {dist} and theta = {theta}')
    # j = json.dumps({"id": agentId, "theta": theta, "dist": dist})
    print(AGENTS, agentId)
    async with aiohttp.ClientSession(f"http://{AGENTS[agentId]}") as session:
        async with session.post("/", json={"id": agentId, "theta": theta, "dist": dist}) as resp:
            await resp.text()
    # r = CONS_AGENTS[agentId].getresponse()
    # data = json.loads(r.read())

    CONS_LOCAL.request("POST","/",json.dumps(pos | {"id":agentId,"status":"STOPPED"}))
    timesteps[agentId] += 1
    CONS_LOCAL.close()

async def main():
    running = True
    while running:
        positions = getPositions()
        asyncio.gather(*[moveRobot(agentId,positions) for agentId in AGENTS])
        sleep(0.2)

asyncio.run(main())
