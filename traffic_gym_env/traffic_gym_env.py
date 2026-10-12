# rl/traffic_gym_env.py
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import traci
import sumolib

from reward import compute_reward


class EcoTwinTrafficEnv(gym.Env):
    """
    Wraps a SUMO city-grid simulation as a Gym environment.
    Action: for each controlled intersection, choose a traffic-light phase.
    Observation: per-intersection queue lengths + local CO2 concentration.
    Reward: multi-objective — penalizes both wait time AND localized CO2 buildup.
    """

    def __init__(self, sumocfg_path, use_gui=False, max_steps=3600):
        super().__init__()
        self.sumocfg_path = sumocfg_path
        self.sumo_binary = "sumo-gui" if use_gui else "sumo"
        self.max_steps = max_steps
        self.step_count = 0

        # Launch once to discover the network topology (junctions, phases)
        traci.start([self.sumo_binary, "-c", self.sumocfg_path, "--no-step-log", "true"])
        self.tls_ids = traci.trafficlight.getIDList()          # controllable intersections
        self.n_tls = len(self.tls_ids)
        # Each TLS can have a different number of valid phases; we take the max
        self.phase_counts = [
            len(traci.trafficlight.getAllProgramLogics(tls)[0].phases)
            for tls in self.tls_ids
        ]
        traci.close()
