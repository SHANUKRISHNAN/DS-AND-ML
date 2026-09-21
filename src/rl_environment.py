import numpy as np

class EcoTwinEnv:
    """Small, dependency-free environment for the EcoTwin project.

    Actions:
      0 = no control
      1 = increase traffic-signal offset by 10 s
      2 = decrease traffic-signal offset by 10 s
      3 = activate green corridor
      4 = increase ventilation by 1 MW

    The environment uses one dataset row as the starting urban state. CO2 is
    changed with a transparent, project-demo control equation. This is a
    simulation for RL learning, not a calibrated atmospheric dispersion model.
    """
    ACTIONS={0:'No control',1:'Increase signal offset',2:'Decrease signal offset',3:'Activate green corridor',4:'Increase ventilation'}
    def __init__(self, data, seed=42):
        self.data=data.reset_index(drop=True)
        self.rng=np.random.default_rng(seed)
        self.action_space_n=5
        self.observation_columns=['co2_concentration_ppm','traffic_emission_rate_kg_h','wind_speed_ms','temperature_c','humidity_pct','rl_traffic_signal_offset_s','rl_green_corridor_active','rl_ventilation_control_mw']
        self.index=0; self.state=None
    def reset(self, index=0):
        self.index=int(index)%len(self.data); self.state=self.data.loc[self.index].copy(); return self._obs()
    def _obs(self):
        return self.state[self.observation_columns].astype(float).to_numpy()
    def step(self, action):
        action=int(action)
        if action not in self.ACTIONS: raise ValueError('action must be 0, 1, 2, 3, or 4')
        before=float(self.state['co2_concentration_ppm'])
        if action==1: self.state['rl_traffic_signal_offset_s']=np.clip(self.state['rl_traffic_signal_offset_s']+10,-60,60)
        elif action==2: self.state['rl_traffic_signal_offset_s']=np.clip(self.state['rl_traffic_signal_offset_s']-10,-60,60)
        elif action==3: self.state['rl_green_corridor_active']=1
        elif action==4: self.state['rl_ventilation_control_mw']=np.clip(self.state['rl_ventilation_control_mw']+1,0,10)
        traffic=float(self.state['traffic_emission_rate_kg_h']); wind=float(self.state['wind_speed_ms']); ventilation=float(self.state['rl_ventilation_control_mw']); corridor=int(self.state['rl_green_corridor_active']); offset=float(self.state['rl_traffic_signal_offset_s'])
        # Transparent simulation: controls reduce effective concentration; wind helps dispersion.
        reduction=0.025*offset + 22*corridor + 14*ventilation + 2.0*wind
        if action==0: reduction=2.0*wind + 10*ventilation + 15*corridor
        new_co2=max(250.0,before-reduction)
        self.state['co2_concentration_ppm']=new_co2
        reward=before-new_co2
        done=True
        info={'action_name':self.ACTIONS[action],'co2_before':before,'co2_after':new_co2,'co2_reduction_ppm':reward}
        return self._obs(),float(reward),done,info
