import sumolib, traci

SUMO = sumolib.checkBinary("sumo")  # "sumo-gui" pour voir la simulation
traci.start([SUMO, "-c", "simulation/carrefour.sumocfg"])

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    t = traci.simulation.getTime()
    if t % 300 == 0:
        attente = sum(traci.edge.getWaitingTime(e) for e in ["O2C", "N2C", "S2C", "E2C"])
        print(f"t={t:.0f}s  véhicules={traci.vehicle.getIDCount()}  attente={attente:.0f}s")

traci.close()
