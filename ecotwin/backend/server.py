import os, sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))

import asyncio
import json
from contextlib import asynccontextmanager

import traci
import sumolib
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from ray.rllib.algorithms.algorithm import Algorithm
import numpy as np
import torch

SUMO_BINARY = sumolib.checkBinary('sumo')  # resolves via $SUMO_HOME, doesn't depend on PATH
SUMO_CONFIG = "city_grid.sumocfg"
connected_clients: set[WebSocket] = set()

GRID_SIZE = 620      # matches the SVG viewBox from GridMap.jsx / LiveMap.jsx
CELL_SIZE = 62       # 10x10 heatmap cells across the grid
NUM_CELLS = GRID_SIZE // CELL_SIZE  # 10

CHECKPOINT_PATH = os.path.abspath("./checkpoints/final")
TLS_IDS = ["A1", "A2", "B0", "B1", "B2", "B3", "C0", "C1", "C2", "C3", "D1", "D2"]

import ray
from ray.tune.registry import register_env
from ecotwin_env import EcoTwinEnv

TLS_IDS = ["A1", "A2", "B0", "B1", "B2", "B3", "C0", "C1", "C2", "C3", "D1", "D2"]
register_env("ecotwin_env", lambda config: EcoTwinEnv("city_grid.sumocfg", TLS_IDS, max_steps=200))

ray.init(ignore_reinit_error=True, log_to_driver=False)

trained_algo = Algorithm.from_checkpoint(CHECKPOINT_PATH)
policy_module = trained_algo.get_module()


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

CONTROL_INTERVAL=10
async def simulation_loop():
    step_count = 0
    traci.start([SUMO_BINARY, "-c", SUMO_CONFIG])
    try:
        while traci.simulation.getMinExpectedNumber() > 0:
            if step_count % CONTROL_INTERVAL == 0:
                obs = get_agent_observation()  # same shape _get_obs() builds in ecotwin_env.py
                actions = get_agent_actions(obs)
                for tls_id, phase in zip(TLS_IDS, actions):
                    traci.trafficlight.setPhase(tls_id, int(phase))

            traci.simulationStep()
            step_count += 1
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


def get_agent_observation():
    """Mirrors EcoTwinEnv._get_obs() exactly -- the live server must build the
    same observation shape/order the policy was trained on, or its decisions
    will be meaningless."""
    data = []
    for tls_id in TLS_IDS:
        lanes = traci.trafficlight.getControlledLanes(tls_id)
        queue = sum(traci.lane.getLastStepHaltingNumber(l) for l in lanes)
        co2 = sum(traci.lane.getCO2Emission(l) for l in lanes)
        data.extend([queue, co2])
    return np.array(data, dtype=np.float32)

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

def get_agent_actions(obs):
    """Runs one inference pass and decodes the flat logits into one phase
    decision per traffic light. Verified shape: MultiDiscrete([4]*12) produces
    a (1, 48) logits tensor -> reshape to (12, 4) -> argmax per row."""
    obs_tensor = torch.from_numpy(obs.reshape(1, -1).astype(np.float32))
    result = policy_module.forward_inference({"obs": obs_tensor})
    logits = result["action_dist_inputs"].reshape(len(TLS_IDS), 4)
    return torch.argmax(logits, dim=-1).numpy()