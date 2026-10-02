"""
Tests your REAL trained checkpoint, with the control-interval fix applied
(re-decide phases every CONTROL_INTERVAL steps instead of every single step).
Compare this output directly against diagnose_baseline.py's output.

If total_queue behaves like the baseline (rises, then drops back down
periodically) -> the frequency fix alone solved the gridlock.
If total_queue keeps climbing and never drops -> the policy itself likely
needs more training, independent of the frequency fix.

Usage: python diagnose_agent_control.py
"""
import os, sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import ray
from ray.tune.registry import register_env
from ray.rllib.algorithms.algorithm import Algorithm
from ecotwin_env import EcoTwinEnv
import numpy as np
import torch
import traci
import sumolib

TLS_IDS = ["A1", "A2", "B0", "B1", "B2", "B3", "C0", "C1", "C2", "C3", "D1", "D2"]
CHECKPOINT_PATH = os.path.abspath("./checkpoints/final")
CONTROL_INTERVAL = 10  # re-decide every 10 steps, not every step

register_env("ecotwin_env", lambda config: EcoTwinEnv("city_grid.sumocfg", TLS_IDS, max_steps=200))
ray.init(ignore_reinit_error=True, log_to_driver=False)
algo = Algorithm.from_checkpoint(CHECKPOINT_PATH)
policy_module = algo.get_module()


def get_agent_actions(obs):
    obs_tensor = torch.from_numpy(obs.reshape(1, -1).astype(np.float32))
    result = policy_module.forward_inference({"obs": obs_tensor})
    logits = result["action_dist_inputs"].reshape(len(TLS_IDS), 4)
    return torch.argmax(logits, dim=-1).numpy()


def get_obs_and_total_queue():
    data = []
    total_queue = 0
    for tls_id in TLS_IDS:
        lanes = traci.trafficlight.getControlledLanes(tls_id)
        queue = sum(traci.lane.getLastStepHaltingNumber(l) for l in lanes)
        co2 = sum(traci.lane.getCO2Emission(l) for l in lanes)
        data.extend([queue, co2])
        total_queue += queue
    return np.array(data, dtype=np.float32), total_queue


SUMO_BINARY = sumolib.checkBinary('sumo')
traci.start([SUMO_BINARY, "-c", "city_grid.sumocfg"])

print(f"{'step':>5} | {'total_queue':>12} | {'total_vehicles':>15}")
print("-" * 40)

for step in range(300):
    if step % CONTROL_INTERVAL == 0:
        obs, _ = get_obs_and_total_queue()
        actions = get_agent_actions(obs)
        for tls_id, phase in zip(TLS_IDS, actions):
            traci.trafficlight.setPhase(tls_id, int(phase))
    traci.simulationStep()
    if step % 10 == 0:
        _, total_queue = get_obs_and_total_queue()
        total_vehicles = len(traci.vehicle.getIDList())
        print(f"{step:>5} | {total_queue:>12} | {total_vehicles:>15}")

traci.close()
algo.stop()
ray.shutdown()
print("\nDone. Compare this total_queue pattern against diagnose_baseline.py's output.")