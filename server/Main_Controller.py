from __future__ import annotations
from dataclasses import dataclass
import http.client
import json
from math import atan2, sqrt, pi, dist
import argparse
import asyncio
import aiohttp


@dataclass
class Pose:
    id: str
    x: float
    y: float
    theta: float

    @staticmethod
    def from_json(o: dict) -> Pose:
        return Pose(**o)


@dataclass(slots=True, frozen=True)
class Point:
    x: float
    y: float

    @staticmethod
    def from_pair(pair: list[float]) -> Point:
        return Point(pair[0], pair[1])


def get_args():
    parser = argparse.ArgumentParser(
        prog="ControllerServer",
        description="Acts as a control server, requests location data and sends actions to agents",
        epilog="That's all folks",
    )
    parser.add_argument(
        "config", type=str, help="Config file in JSON format of scenario"
    )
    parser.add_argument("path", type=str, help="Path file in JSON format")
    arg = parser.parse_args()
    print(f"Reading file {arg.config}")
    with open(arg.config) as f1:
        j = json.load(f1)

    print(f"Reading file {arg.path}")
    with open(arg.path) as f2:
        paths: dict[str, list[Point]] = {
            id: [Point.from_pair(pair) for pair in path]
            for id, path in json.load(f2).items()
        }

    return j["AGENTS"], j["LOCALISATION_IP"], j["PRECISION"], paths


AGENTS, LOCALISATION_IP, PRECISION, PATHS = get_args()
AGENTS: dict[str, str] # agent id to IP
PATHS: dict[str, list[Point]]
print("Recieved configuration")
CONS_LOCAL = http.client.HTTPConnection(LOCALISATION_IP)
timesteps = {i: 0 for i in AGENTS}
agentStatus = {i: "STOPPED" for i in AGENTS}


def getPositions() -> dict[str, Pose]:
    CONS_LOCAL.request("GET", "/")
    r = CONS_LOCAL.getresponse()
    if r.status != 200:
        print(f"error code {r.status} recieved")
        print("check if valid GetRequest")
    return {robot: Pose.from_json(pose) for robot, pose in json.loads(r.read()).items()}


def scheduled(curId: str, positions: dict[str, Pose]):
    AVOIDANCE_RADIUS = 0.6
    x = PATHS[curId][timesteps[curId]].x
    y = PATHS[curId][timesteps[curId]].y
    # THIS takes advantage of not being able to go between points
    for id in AGENTS:
        if id == curId:
            return True  ##GIVES this agent prioity.

        curClose = (
            dist((x, y), (positions[id].x, positions[id].y)) < AVOIDANCE_RADIUS
        )
        furClose = (
            dist((x, y), (PATHS[id][timesteps[id]].x, PATHS[id][timesteps[id]].y))
            < AVOIDANCE_RADIUS
        )

        if curClose and furClose:
            return False
    return True


async def moveRobot(agentId: str, positions: dict[str, Pose]):
    timestep = timesteps[agentId]
    aPath = PATHS[agentId]
    if len(aPath) <= timestep:
        return

    pos = positions[agentId]
    if agentStatus[agentId] != "STOPPED":
        return
    agentStatus[agentId] = "RUNNING"

    if not scheduled(agentId, positions):
        return

    # if abs(pos['x'] - aPath[timestep - 1][0]) > PRECISION:
    #     print(f"turtlebot {agentId} has not reached goal")
    #     ###course correction
    #     pass
    # if abs(pos['y'] - aPath[timestep - 1][1]) > PRECISION:
    #     print(f"turtlebot {agentId} has not reached goal")
    #     ###course correction
    #     pass

    ###DO MATHS###
    target_x = aPath[timestep].x
    target_y = aPath[timestep].y
    run = target_x - pos.x
    rise = target_y - pos.y
    theta = (atan2(rise, run) - pos.theta + pi * 2) % (pi * 2)
    if theta > pi:
        theta -= 2*pi
    dist = sqrt(((pos.x - target_x) ** 2) + ((pos.y - target_y) ** 2))

    # print(f"starting at {pos} to {target_x},{target_y}")
    # print(f"moving {agentId} with distance = {dist} and theta = {theta}")
    # print(AGENTS, agentId)
    async with aiohttp.ClientSession(f"http://{AGENTS[agentId]}") as session:
        async with session.post(
            "/", json={"id": agentId, "theta": theta, "dist": dist}
        ) as resp:
            await resp.text()

    agentStatus[agentId] = "STOPPED"
    timesteps[agentId] += 1


async def main():
    running = True
    while running:
        positions = getPositions()
        # use `await` to wait for all robots to complete before the next step
        # ignore it (_ = ...) to run in background but don't wait for robots to complete.
        await asyncio.gather(*[moveRobot(agentId, positions) for agentId in AGENTS])
        
        # not necessary if awaiting the above task
        await asyncio.sleep(10)


asyncio.run(main())
