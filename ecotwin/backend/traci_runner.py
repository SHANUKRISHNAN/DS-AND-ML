# traci_runner.py
import traci
import sumolib

SUMO_BINARY = sumolib.checkBinary('sumo')  # swap to 'sumo-gui' to watch it visually
SUMO_CONFIG = "city_grid.sumocfg"

def run_simulation():
    traci.start([SUMO_BINARY, "-c", SUMO_CONFIG])
    step = 0
    while step < 3600:
        traci.simulationStep()
        for veh_id in traci.vehicle.getIDList():
            co2 = traci.vehicle.getCO2Emission(veh_id)
            x, y = traci.vehicle.getPosition(veh_id)
        step += 1
    traci.close()

if __name__ == "__main__":
    run_simulation()