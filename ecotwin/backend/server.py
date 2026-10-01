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

GRID_SIZE = 620      # matches the SVG viewBox from GridMap.jsx / LiveMap.jsx
CELL_SIZE = 62       # 10x10 heatmap cells across the grid
NUM_CELLS = GRID_SIZE // CELL_SIZE  # 10


def compute_heatmap():
    """Buckets every vehicle's CO2 output into a coarse grid for the heatmap overlay.
    Cell indices are clamped because a few network coordinates sit slightly outside
    0-620 at the grid's edges (confirmed empirically: one real vehicle landed in
    cell (4, -1) before clamping was added)."""
    cells = {}
    for veh_id in traci.vehicle.getIDList():
        x, y = traci.vehicle.getPosition(veh_id)
        cell_x = max(0, min(NUM_CELLS - 1, int(x // CELL_SIZE)))
        cell_y = max(0, min(NUM_CELLS - 1, int(y // CELL_SIZE)))
        co2 = traci.vehicle.getCO2Emission(veh_id)
        key = f"{cell_x},{cell_y}"
        cells[key] = cells.get(key, 0.0) + co2
    return cells

# Modify get_live_sim_state() in server.py to include the heatmap:
def get_live_sim_state():
    vehicles = []
    for veh_id in traci.vehicle.getIDList():
        x, y = traci.vehicle.getPosition(veh_id)
        vehicles.append({
            "id": veh_id,
            "x": x,
            "y": y,
            "co2": traci.vehicle.getCO2Emission(veh_id),
        })
    return {"vehicles": vehicles, "heatmap": compute_heatmap()}

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