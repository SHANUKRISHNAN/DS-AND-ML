r"""
Run once from backend\ BEFORE training. Measures how big the reward inputs are under
SUMO's default signals on YOUR route file, and checks the scales set in ecotwin_env.py.
Usage:  venv\Scripts\python.exe calibrate_reward.py
"""
import os, sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci, sumolib
from ecotwin_env import WAIT_REF, CO2_REF, unique_lanes

TLS_IDS = ["A1", "A2", "B0", "B1", "B2", "B3", "C0", "C1", "C2", "C3", "D1", "D2"]
traci.start([sumolib.checkBinary('sumo'), "-c", "city_grid.sumocfg", "--no-warnings"])
lanes = unique_lanes(TLS_IDS)
waits, co2s = [], []
for step in range(300):
    traci.simulationStep()
    if step >= 50:                                   # skip the empty start-up period
        waits.append(sum(traci.lane.getWaitingTime(l) for t in TLS_IDS for l in lanes[t]))
        co2s.append(sum(traci.lane.getCO2Emission(l) for t in TLS_IDS for l in lanes[t]))
traci.close()

def stats(v):
    v = sorted(v); return v[len(v) // 2], v[int(len(v) * 0.9)]

for name, vals, ref in (("wait", waits, WAIT_REF), ("co2", co2s, CO2_REF)):
    med, p90 = stats(vals)
    ok = med <= ref <= p90
    print(f"{name:>5}: median={med:>9.0f}  p90={p90:>9.0f}  | ecotwin_env.py setting={ref:>9.0f}  -> "
          + ("OK (between median and p90)" if ok else f"CHANGE it to a value between {med:.0f} and {p90:.0f}"))