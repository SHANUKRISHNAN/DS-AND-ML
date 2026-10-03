# train_agent.py
import os, sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))

import ray
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPOConfig
from ecotwin_env import EcoTwinEnv

TLS_IDS = ["A1", "A2", "B0", "B1", "B2", "B3", "C0", "C1", "C2", "C3", "D1", "D2"]


def env_creator(config):
    return EcoTwinEnv("city_grid.sumocfg", TLS_IDS, max_steps=200)


register_env("ecotwin_env", env_creator)
ray.init(ignore_reinit_error=True)

config = (
    PPOConfig()
    .environment("ecotwin_env")
    .env_runners(num_env_runners=0)  # 0 = run inline; raise once stable to parallelize
    .training(
        train_batch_size=2000,
        minibatch_size=128,
        num_epochs=10,
        lr=3e-4,
        gamma=0.99,
    )
)

algo = config.build_algo()

NUM_ITERATIONS = 200
for i in range(NUM_ITERATIONS):
    result = algo.train()
    ep_return = result.get("env_runners", {}).get("episode_return_mean")
    print(f"Iteration {i}: episode_return_mean={ep_return}")

    if i % 10 == 0:
        checkpoint_dir = algo.save_to_path(os.path.abspath(f"./checkpoints/iter_{i}"))
        print(f"  Checkpoint saved: {checkpoint_dir}")

final_checkpoint = algo.save_to_path(os.path.abspath("./checkpoints/final"))
print("Final checkpoint saved:", final_checkpoint)

ray.shutdown()