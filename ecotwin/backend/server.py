import os, sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))

import asyncio
import json
from contextlib import asynccontextmanager

import traci
import sumolib
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

SUMO_BINARY = sumolib.checkBinary('sumo')  # resolves via $SUMO_HOME, doesn't depend on PATH
SUMO_CONFIG = "city_grid.sumocfg"
connected_clients: set[WebSocket] = set()


def get_live_sim_state():
    """Pulls current vehicle positions and emissions from the running SUMO instance.
    Sends raw local (x, y) coordinates, not lat/lng: this grid has no real geographic
    projection attached, so traci.simulation.convertGeo just hands the same x, y back
    unchanged on this network — the frontend renders these directly as SVG instead of
    pretending they're real GPS coordinates."""
    vehicles = []
    for veh_id in traci.vehicle.getIDList():
        x, y = traci.vehicle.getPosition(veh_id)
        vehicles.append({
            "id": veh_id,
            "x": x,
            "y": y,
            "co2": traci.vehicle.getCO2Emission(veh_id),
        })
    return {"vehicles": vehicles}


async def simulation_loop():
    """Owns the single TraCI connection for the whole server's lifetime, steps the
    simulation, and broadcasts state to every connected browser tab."""
    traci.start([SUMO_BINARY, "-c", SUMO_CONFIG])
    try:
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            state = json.dumps(get_live_sim_state())
            dead = []
            for ws in connected_clients:
                try:
                    await ws.send_text(state)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                connected_clients.discard(ws)
            await asyncio.sleep(0.1)
    finally:
        traci.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(simulation_loop())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "EcoTwin backend is running"}


@app.websocket("/ws/simulation")
async def simulation_feed(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # keeps the connection open; client sends nothing
    except WebSocketDisconnect:
        connected_clients.discard(websocket)