import os, sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))

import asyncio
import json
from contextlib import asynccontextmanager

import numpy as np
import ray
import sumolib
import torch
import traci
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from ray.rllib.algorithms.algorithm import Algorithm
from ray.tune.registry import register_env

# The live server builds observations and decision timing from the SAME code the
# agent was trained with, so the two cannot drift apart.
from ecotwin_env import EcoTwinEnv, ACTION_REPEAT, build_observation, unique_lanes

SUMO_BINARY = sumolib.checkBinary('sumo')
SUMO_CONFIG = "city_grid.sumocfg"
TLS_IDS = ["A1", "A2", "B0", "B1", "B2", "B3", "C0", "C1", "C2", "C3", "D1", "D2"]
CHECKPOINT_PATH = os.path.abspath("./checkpoints/final")

GRID_SIZE = 620
CELL_SIZE = 62
NUM_CELLS = GRID_SIZE // CELL_SIZE
HEATMAP_EVERY_N_STEPS = 5

connected_clients: set[WebSocket] = set()

# from_checkpoint() rebuilds the algorithm's environment runners, which needs the
# env name registered in THIS process (the checkpoint stores only the name).
register_env(
    "ecotwin_env",
    lambda config: EcoTwinEnv(SUMO_CONFIG, TLS_IDS, max_steps=30, action_repeat=ACTION_REPEAT),
)
ray.init(ignore_reinit_error=True, log_to_driver=False)
trained_algo = Algorithm.from_checkpoint(CHECKPOINT_PATH)
policy_module = trained_algo.get_module()


def get_agent_actions(obs):
    """One phase decision per traffic light: logits (1, 48) -> (12, 4) -> argmax."""
    obs_tensor = torch.from_numpy(obs.reshape(1, -1).astype(np.float32))
    with torch.no_grad():
        result = policy_module.forward_inference({"obs": obs_tensor})
    logits = result["action_dist_inputs"].reshape(len(TLS_IDS), 4)
    return torch.argmax(logits, dim=-1).numpy()


def compute_heatmap():
    """Buckets each vehicle's CO2 into a 10x10 grid. Indices are clamped because a
    few network coordinates sit slightly outside 0-620 at the grid edges."""
    cells = {}
    for veh_id in traci.vehicle.getIDList():
        x, y = traci.vehicle.getPosition(veh_id)
        cx = max(0, min(NUM_CELLS - 1, int(x // CELL_SIZE)))
        cy = max(0, min(NUM_CELLS - 1, int(y // CELL_SIZE)))
        key = f"{cx},{cy}"
        cells[key] = cells.get(key, 0.0) + traci.vehicle.getCO2Emission(veh_id)
    return cells


def get_vehicles():
    vehicles = []
    for veh_id in traci.vehicle.getIDList():
        x, y = traci.vehicle.getPosition(veh_id)
        vehicles.append({
            "id": veh_id,
            "x": x,
            "y": y,
            "co2": traci.vehicle.getCO2Emission(veh_id),
            "angle": traci.vehicle.getAngle(veh_id),
        })
    return vehicles


async def simulation_loop():
    """Owns the single TraCI connection. The trained agent decides every
    ACTION_REPEAT simulated seconds (exactly as in training); the world steps
    every second and is broadcast to every connected browser tab."""
    traci.start([SUMO_BINARY, "-c", SUMO_CONFIG, "--no-warnings"])
    lanes_by_tls = unique_lanes(TLS_IDS)
    step_count = 0
    last_heatmap = {}
    try:
        while traci.simulation.getMinExpectedNumber() > 0:
            if step_count % ACTION_REPEAT == 0:
                obs = build_observation(TLS_IDS, lanes_by_tls)
                for tls_id, phase in zip(TLS_IDS, get_agent_actions(obs)):
                    traci.trafficlight.setPhase(tls_id, int(phase))

            traci.simulationStep()
            step_count += 1

            # Recompute the (slower-changing) heatmap only every N steps, but send
            # the latest one every message so the frontend never sees it vanish.
            if step_count % HEATMAP_EVERY_N_STEPS == 0:
                last_heatmap = compute_heatmap()
            state = json.dumps({"vehicles": get_vehicles(), "heatmap": last_heatmap})

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
            await websocket.receive_text()  # keeps the connection open
    except WebSocketDisconnect:
        connected_clients.discard(websocket)