# ecotwin_env.py
import gym
from gym import spaces
import numpy as np
import traci


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

    def reset(self):
        if traci.isLoaded():
            traci.close()
        traci.start(["sumo", "-c", self.sumocfg_path])
        self.current_step = 0
        return self._get_obs()

    def step(self, action):
        for tls_id, phase in zip(self.tls_ids, action):
            traci.trafficlight.setPhase(tls_id, int(phase))
        traci.simulationStep()
        self.current_step += 1

        obs = self._get_obs()
        reward = self._compute_reward()
        done = self.current_step >= self.max_steps
        return obs, reward, done, {}

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
        # Multi-objective: balance commute time against pollution hot-spots
        return -(0.5 * total_wait + 0.5 * (total_co2 / 1000.0))

    def close(self):
        if traci.isLoaded():
            traci.close()