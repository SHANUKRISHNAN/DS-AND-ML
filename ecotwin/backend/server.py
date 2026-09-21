import os, sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
 
import asyncio
import json
from contextlib import asynccontextmanager
 
import traci
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
 
SUMO_CONFIG = "city_grid.sumocfg"
connected_clients: set[WebSocket] = set()
 
 
def get_live_sim_state():
    """Pulls current vehicle positions and emissions from the running SUMO instance."""
    vehicles = []
    for veh_id in traci.vehicle.getIDList():
        x, y = traci.vehicle.getPosition(veh_id)
        lon, lat = traci.simulation.convertGeo(x, y)
        vehicles.append({
            "id": veh_id,
            "lat": lat,
            "lng": lon,
            "co2": traci.vehicle.getCO2Emission(veh_id),
        })
    return {"vehicles": vehicles}
 
 
async def simulation_loop():
    """Owns the single TraCI connection for the whole server's lifetime, steps the
    simulation, and broadcasts state to every connected browser tab."""
    traci.start(["sumo", "-c", SUMO_CONFIG])
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
 
 
@app.websocket("/ws/simulation")
async def simulation_feed(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # keeps the connection open; client sends nothing
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
 