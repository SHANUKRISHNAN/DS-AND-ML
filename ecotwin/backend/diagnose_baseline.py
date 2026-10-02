"""
Baseline check: how do queues behave with SUMO's own default traffic light
program, no agent involved at all? Run this first, note the pattern (queue
should rise then periodically DROP as lights cycle properly), then compare
against diagnose_agent_control.py's output.

Usage: python diagnose_baseline.py
"""
import os, sys
sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci
import sumolib

TLS_IDS = ["A1", "A2", "B0", "B1", "B2", "B3", "C0", "C1", "C2", "C3", "D1", "D2"]
SUMO_BINARY = sumolib.checkBinary('sumo')

traci.start([SUMO_BINARY, "-c", "city_grid.sumocfg"])

print(f"{'step':>5} | {'total_queue':>12} | {'total_vehicles':>15}")
print("-" * 40)

for step in range(300):
    traci.simulationStep()  # no setPhase calls -- default program runs untouched
    if step % 10 == 0:
        total_queue = 0
        for tls_id in TLS_IDS:
            lanes = traci.trafficlight.getControlledLanes(tls_id)
            total_queue += sum(traci.lane.getLastStepHaltingNumber(l) for l in lanes)
        total_vehicles = len(traci.vehicle.getIDList())
        print(f"{step:>5} | {total_queue:>12} | {total_vehicles:>15}")

traci.close()
print("\nDone. A healthy pattern shows total_queue rising AND periodically")
print("dropping back down as lights cycle -- not climbing forever.")