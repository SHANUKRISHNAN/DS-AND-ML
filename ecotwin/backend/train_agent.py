"""
Trains the RL agent, then automatically compares its traffic-light control
against SUMO's own default signal timing -- no separate diagnostic script
needed. Watch the printed verdict at the end.
"""
import os, sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))

import ray
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.algorithms.algorithm import Algorithm
from ecotwin_env import EcoTwinEnv
import numpy as np
import torch
import traci
import sumolib

TLS_IDS = ["A1", "A2", "B0", "B1", "B2", "B3", "C0", "C1", "C2", "C3", "D1", "D2"]
SUMO_BINARY = sumolib.checkBinary('sumo')
CONTROL_INTERVAL = 10  # hold each chosen phase for this many steps before re-deciding
COMPARISON_STEPS = 300  # how long to run each comparison simulation


def env_creator(config):
    return EcoTwinEnv("city_grid.sumocfg", TLS_IDS, max_steps=200)


register_env("ecotwin_env", env_creator)
ray.init(ignore_reinit_error=True)

config = (
    PPOConfig()
    .environment("ecotwin_env")
    .env_runners(num_env_runners=0)
    .training(
        train_batch_size=2000,
        minibatch_size=128,
        num_epochs=10,
        lr=3e-4,
        gamma=0.99,
    )
)

algo = config.build_algo()

# Raised from 50: 50 was enough to prove the training pipeline works
# mechanically, but a real comparison against the default baseline showed
# the resulting policy performed worse than doing nothing -- an undertrained
# policy on this scale of problem (12 lights, ~16.7M possible joint actions)
# is expected, not a bug. 300 is a reasonable next checkpoint to test; if the
# comparison below still looks bad, go higher still.
NUM_ITERATIONS = 300

for i in range(NUM_ITERATIONS):
    result = algo.train()
    ep_return = result.get("env_runners", {}).get("episode_return_mean")
    print(f"Iteration {i}: episode_return_mean={ep_return}")

    if i % 50 == 0:
        checkpoint_dir = algo.save_to_path(os.path.abspath(f"./checkpoints/iter_{i}"))
        print(f"  Checkpoint saved: {checkpoint_dir}")

final_checkpoint = algo.save_to_path(os.path.abspath("./checkpoints/final"))
print("Final checkpoint saved:", final_checkpoint)

# Extract the trained policy BEFORE stopping algo -- the policy module itself
# is just neural network weights, independent of algo's lifecycle. But algo's
# internal training environment still holds an open TraCI connection at this
# point, which would conflict with the comparison runs below trying to open
# their own -- confirmed directly: skipping algo.stop() here throws
# "Connection 'default' is already active" the moment run_baseline() tries
# to start its own TraCI session.
policy_module = algo.get_module()
algo.stop()


def get_agent_actions(obs):
    obs_tensor = torch.from_numpy(obs.reshape(1, -1).astype(np.float32))
    result = policy_module.forward_inference({"obs": obs_tensor})
    logits = result["action_dist_inputs"].reshape(len(TLS_IDS), 4)
    return torch.argmax(logits, dim=-1).numpy()


def get_obs_and_queue():
    data, total_queue = [], 0
    for tls_id in TLS_IDS:
        lanes = traci.trafficlight.getControlledLanes(tls_id)
        queue = sum(traci.lane.getLastStepHaltingNumber(l) for l in lanes)
        co2 = sum(traci.lane.getCO2Emission(l) for l in lanes)
        data.extend([queue, co2])
        total_queue += queue
    return np.array(data, dtype=np.float32), total_queue


def run_baseline():
    traci.start([SUMO_BINARY, "-c", "city_grid.sumocfg"])
    queues = []
    for step in range(COMPARISON_STEPS):
        traci.simulationStep()
        if step % 10 == 0:
            _, q = get_obs_and_queue()
            queues.append(q)
    traci.close()
    return queues


def run_agent_controlled():
    traci.start([SUMO_BINARY, "-c", "city_grid.sumocfg"])
    queues = []
    for step in range(COMPARISON_STEPS):
        if step % CONTROL_INTERVAL == 0:
            obs, _ = get_obs_and_queue()
            actions = get_agent_actions(obs)
            for tls_id, phase in zip(TLS_IDS, actions):
                traci.trafficlight.setPhase(tls_id, int(phase))
        traci.simulationStep()
        if step % 10 == 0:
            _, q = get_obs_and_queue()
            queues.append(q)
    traci.close()
    return queues


print("\nRunning post-training comparison against default signal timing...")
baseline_queues = run_baseline()
agent_queues = run_agent_controlled()

second_half = len(baseline_queues) // 2
baseline_avg = sum(baseline_queues[second_half:]) / len(baseline_queues[second_half:])
agent_avg = sum(agent_queues[second_half:]) / len(agent_queues[second_half:])

print(f"\n{'':>20} | {'avg queue (2nd half)':>22} | {'max queue':>10}")
print("-" * 58)
print(f"{'Baseline (default)':>20} | {baseline_avg:>22.1f} | {max(baseline_queues):>10}")
print(f"{'Agent (trained)':>20} | {agent_avg:>22.1f} | {max(agent_queues):>10}")

if agent_avg < baseline_avg:
    print(f"\nVERDICT: Agent beats baseline ({agent_avg:.1f} < {baseline_avg:.1f} avg queue). Good to proceed to Week 4.")
else:
    print(f"\nVERDICT: Agent is still worse than baseline ({agent_avg:.1f} >= {baseline_avg:.1f} avg queue).")
    print("Consider raising NUM_ITERATIONS further and retraining before using this checkpoint for live control.")

ray.shutdown()