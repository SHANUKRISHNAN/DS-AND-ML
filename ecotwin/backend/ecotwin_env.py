import os, sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import traci
import sumolib

SUMO_BINARY = sumolib.checkBinary('sumo')

# One agent decision = this many simulated seconds. The live server MUST use the
# same value (it imports it from here), otherwise the policy is deployed in a
# different regime from the one it was trained in.
ACTION_REPEAT = 10

# Scales, set from measured default-signal traffic on this network (run
# calibrate_reward.py on your own route file and adjust if yours differ):
#   total waiting time under default signals: median ~118, p90 ~529
#   total CO2 under default signals:          median ~129k, p90 ~172k
WAIT_REF = 200.0
CO2_REF = 110000.0
TERM_CAP = 5.0              # soft ceiling per reward term (avoids hard saturation)
QUEUE_OBS_SCALE = 20.0      # brings observations to roughly O(1) for the network
CO2_OBS_SCALE = 50000.0


def unique_lanes(tls_ids):
    """getControlledLanes repeats a lane once per movement it serves; count each once."""
    return {t: sorted(set(traci.trafficlight.getControlledLanes(t))) for t in tls_ids}


def build_observation(tls_ids, lanes_by_tls):
    """Shared by training and the live server so they can never drift apart.
    Per light: [queue, co2, current_phase/3], each scaled to roughly 0-1."""
    data = []
    for tls_id in tls_ids:
        lanes = lanes_by_tls[tls_id]
        queue = sum(traci.lane.getLastStepHaltingNumber(l) for l in lanes)
        co2 = sum(traci.lane.getCO2Emission(l) for l in lanes)
        phase = traci.trafficlight.getPhase(tls_id)
        data.extend([queue / QUEUE_OBS_SCALE, co2 / CO2_OBS_SCALE, phase / 3.0])
    return np.clip(np.array(data, dtype=np.float32), 0.0, TERM_CAP)


class EcoTwinEnv(gym.Env):
    """One agent step = ACTION_REPEAT simulated seconds. Observations and rewards
    are scaled to roughly O(1) so the network and value function can learn."""

    def __init__(self, sumocfg_path, tls_ids, max_steps=30, action_repeat=ACTION_REPEAT):
        super().__init__()
        self.sumocfg_path = sumocfg_path
        self.tls_ids = tls_ids
        self.max_steps = max_steps
        self.action_repeat = action_repeat
        self.current_step = 0
        self._lanes = None

        self.action_space = spaces.MultiDiscrete([4] * len(tls_ids))
        self.observation_space = spaces.Box(
            low=0.0, high=TERM_CAP, shape=(len(tls_ids) * 3,), dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if traci.isLoaded():
            traci.close()
        traci.start([SUMO_BINARY, "-c", self.sumocfg_path, "--no-warnings"])
        self._lanes = unique_lanes(self.tls_ids)
        self.current_step = 0
        return build_observation(self.tls_ids, self._lanes), {}

    def step(self, action):
        for tls_id, phase in zip(self.tls_ids, action):
            traci.trafficlight.setPhase(tls_id, int(phase))

        reward_sum, ended = 0.0, False
        for _ in range(self.action_repeat):
            traci.simulationStep()
            reward_sum += self._compute_reward()
            if traci.simulation.getMinExpectedNumber() <= 0:
                ended = True
                break
        self.current_step += 1

        obs = build_observation(self.tls_ids, self._lanes)
        reward = reward_sum / self.action_repeat
        truncated = self.current_step >= self.max_steps
        return obs, reward, ended, truncated, {}

    def _compute_reward(self):
        total_wait, total_co2 = 0.0, 0.0
        for tls_id in self.tls_ids:
            for l in self._lanes[tls_id]:
                total_wait += traci.lane.getWaitingTime(l)
                total_co2 += traci.lane.getCO2Emission(l)
        norm_wait = min(total_wait / WAIT_REF, TERM_CAP)
        norm_co2 = min(total_co2 / CO2_REF, TERM_CAP)
        return -(0.5 * norm_wait + 0.5 * norm_co2)

    def close(self):
        if traci.isLoaded():
            traci.close()