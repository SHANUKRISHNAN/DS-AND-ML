import os, sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import traci
import sumolib

SUMO_BINARY = sumolib.checkBinary('sumo')  # resolves via $SUMO_HOME, doesn't depend on PATH


class EcoTwinEnv(gym.Env):
    """Gym wrapper around a SUMO/TraCI simulation for multi-objective traffic control."""

    def __init__(self, sumocfg_path, tls_ids, max_steps=3600):
        super().__init__()
        self.sumocfg_path = sumocfg_path
        self.tls_ids = tls_ids
        self.max_steps = max_steps
        self.current_step = 0

        # One discrete phase choice (0-3) per traffic light
        self.action_space = spaces.MultiDiscrete([4] * len(tls_ids))

        # Per intersection: [queue length, CO2 emission]
        self.observation_space = spaces.Box(
            low=0, high=np.inf, shape=(len(tls_ids) * 2,), dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if traci.isLoaded():
            traci.close()
        traci.start([SUMO_BINARY, "-c", self.sumocfg_path])
        self.current_step = 0
        return self._get_obs(), {}

    def step(self, action):
        for tls_id, phase in zip(self.tls_ids, action):
            traci.trafficlight.setPhase(tls_id, int(phase))
        traci.simulationStep()
        self.current_step += 1

        obs = self._get_obs()
        reward = self._compute_reward()
        terminated = self.current_step >= self.max_steps
        truncated = False
        return obs, reward, terminated, truncated, {}

    def _get_obs(self):
        data = []
        for tls_id in self.tls_ids:
            lanes = traci.trafficlight.getControlledLanes(tls_id)
            queue = sum(traci.lane.getLastStepHaltingNumber(l) for l in lanes)
            co2 = sum(traci.lane.getCO2Emission(l) for l in lanes)
            data.extend([queue, co2])
        return np.array(data, dtype=np.float32)

    def _compute_reward(self):
        total_wait, total_co2 = 0.0, 0.0
        for tls_id in self.tls_ids:
            lanes = traci.trafficlight.getControlledLanes(tls_id)
            total_wait += sum(traci.lane.getWaitingTime(l) for l in lanes)
            total_co2 += sum(traci.lane.getCO2Emission(l) for l in lanes)
        return -(0.5 * total_wait + 0.5 * (total_co2 / 1000.0))

    def close(self):
        if traci.isLoaded():
            traci.close()