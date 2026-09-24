"""
Standalone smoke test for EcoTwinEnv — proves the Gym environment itself
works (reset, step, reward) without needing Ray RLlib or any RL library yet.

Usage:
    python get_tls_ids.py          # copy the printed list
    # paste it into TLS_IDS below
    python smoke_test_env.py
"""
from ecotwin_env import EcoTwinEnv

# Paste the output of get_tls_ids.py here:
TLS_IDS = ["A1", "A2", "B0", "B1", "B2", "B3", "C0", "C1", "C2", "C3", "D1", "D2"]

env = EcoTwinEnv("city_grid.sumocfg", TLS_IDS, max_steps=20)

obs, info = env.reset()
print("Reset OK. Observation shape:", obs.shape, "dtype:", obs.dtype)
print("First obs sample:", obs[:6])

for i in range(10):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    print(f"Step {i}: reward={reward:.3f}  terminated={terminated}  obs[:4]={obs[:4]}")

env.close()
print("Closed cleanly.")