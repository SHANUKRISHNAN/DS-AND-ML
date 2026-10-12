"""
Trains the RL agent against the rebuilt EcoTwinEnv, then compares it with SUMO's
default signal timing using the same average-queue metric as before.

IMPORTANT: this environment has a different observation (36 values instead of
24), a rescaled reward and 10-second decisions, so OLD checkpoints are not
compatible. Rename your old folder first:   ren checkpoints checkpoints_old
"""
import os, sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))

import ray
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.algorithms.algorithm import Algorithm
from ecotwin_env import EcoTwinEnv, ACTION_REPEAT, build_observation, unique_lanes
import numpy as np
import torch
import traci

TLS_IDS = ["A1", "A2", "B0", "B1", "B2", "B3", "C0", "C1", "C2", "C3", "D1", "D2"]
EPISODE_AGENT_STEPS = 30          # 30 decisions x 10 s = 300 simulated seconds
NUM_ITERATIONS = 200
CHECKPOINT_EVERY = 25
RESUME = False                    # set True to continue the NEW run from checkpoints/final
CHECKPOINT_DIR = os.path.abspath("./checkpoints")
FINAL = os.path.join(CHECKPOINT_DIR, "final")

if not RESUME and os.path.exists(FINAL):
    sys.exit("checkpoints/final already exists and is from the OLD environment (incompatible).\n"
             "Run:  ren checkpoints checkpoints_old   then start again.")


def env_creator(config):
    return EcoTwinEnv("city_grid.sumocfg", TLS_IDS, max_steps=EPISODE_AGENT_STEPS, action_repeat=ACTION_REPEAT)


register_env("ecotwin_env", env_creator)
ray.init(ignore_reinit_error=True)

if RESUME:
    print("Resuming from", FINAL)
    algo = Algorithm.from_checkpoint(FINAL)
else:
    config = (
        PPOConfig()
        .environment("ecotwin_env")
        .env_runners(num_env_runners=0)
        .training(
            train_batch_size=600,
            minibatch_size=128,
            num_epochs=10,
            lr=3e-4,
            # Shorter horizon: one decision is 10 s, so 0.95 looks ~200 s ahead.
            gamma=0.95,
            # RLlib's docs: vf_clip_param "is sensitive to the scale of the
            # rewards. If your expected V is large, increase this." The default
            # (10) was too small for the old reward scale (~ -87 per step).
            vf_clip_param=100.0,
        )
    )
    algo = config.build_algo()

# What to watch (verified metric names):
#  entropy          starts near its maximum, 12*ln(4)=16.64, and should FALL as the
#                   policy commits to behaviour
#  vf_explained_var ~R^2 of the critic. Stuck at ~0 = the critic is not learning
#                   (this is what the old setup showed: 0.00002 after 600 iterations)
recent_vf = []
for i in range(NUM_ITERATIONS):
    result = algo.train()
    ep_return = result.get("env_runners", {}).get("episode_return_mean")
    stats = result.get("learners", {}).get("default_policy", {})
    entropy, kl, vf = stats.get("entropy"), stats.get("mean_kl_loss"), stats.get("vf_explained_var")
    print(f"Iteration {i}: return={ep_return:.2f}  entropy={entropy:.2f}  kl={kl:.4f}  vf_explained_var={vf:.4f}")

    recent_vf.append(vf)
    if len(recent_vf) == 10:
        print(f"  -- mean vf_explained_var over last 10 iterations: {sum(recent_vf) / 10:.3f}")
        recent_vf = []

    if i % CHECKPOINT_EVERY == 0 and i > 0:
        print("  Checkpoint saved:", algo.save_to_path(os.path.join(CHECKPOINT_DIR, f"iter_{i}")))

print("Final checkpoint saved:", algo.save_to_path(FINAL))

# The policy module is just weights; algo.stop() closes the training env's TraCI
# connection, which would otherwise block the comparison runs below.
policy_module = algo.get_module()
algo.stop()


def queue_now():
    return sum(traci.lane.getLastStepHaltingNumber(l)
               for t in TLS_IDS for l in traci.trafficlight.getControlledLanes(t))


def run_comparison(use_agent):
    env = EcoTwinEnv("city_grid.sumocfg", TLS_IDS, max_steps=EPISODE_AGENT_STEPS, action_repeat=ACTION_REPEAT)
    obs, _ = env.reset()
    queues = []
    for _ in range(EPISODE_AGENT_STEPS):
        if use_agent:
            logits = policy_module.forward_inference(
                {"obs": torch.from_numpy(obs.reshape(1, -1))})["action_dist_inputs"]
            action = torch.argmax(logits.reshape(len(TLS_IDS), 4), dim=-1).numpy()
            obs, *_ = env.step(action)
        else:
            for _ in range(ACTION_REPEAT):          # default signals, untouched
                traci.simulationStep()
        queues.append(queue_now())
    env.close()
    return queues


print("\nRunning post-training comparison against default signal timing...")
baseline_q, agent_q = run_comparison(False), run_comparison(True)
half = len(baseline_q) // 2
b_avg, a_avg = sum(baseline_q[half:]) / len(baseline_q[half:]), sum(agent_q[half:]) / len(agent_q[half:])

print(f"\n{'':>20} | {'avg queue (2nd half)':>22} | {'max queue':>10}")
print("-" * 58)
print(f"{'Baseline (default)':>20} | {b_avg:>22.1f} | {max(baseline_q):>10}")
print(f"{'Agent (trained)':>20} | {a_avg:>22.1f} | {max(agent_q):>10}")
if a_avg < b_avg:
    print(f"\nVERDICT: Agent beats baseline ({a_avg:.1f} < {b_avg:.1f}).")
else:
    print(f"\nVERDICT: Agent is still worse than baseline ({a_avg:.1f} >= {b_avg:.1f}).")

ray.shutdown()