import sumolib, traci
import sys


GUI = "--gui" in sys.argv
SUMO = sumolib.checkBinary("sumo-gui" if GUI else "sumo")

cmd = [SUMO, "-c", "simulation/carrefour.sumocfg"]
if GUI:
    cmd += ["--start", "--delay", "100", "--quit-on-end"]

traci.start(cmd)

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    traci.trafficlight.setRedYellowGreenState("C", state="rrrrrrrrrrrrrrrrrr")
    t = traci.simulation.getTime()
    if t % 300 == 0:
        NL = traci.trafficlight.getRedYellowGreenState("C")
        print(f"North traffic Light state ${NL}")
        attente = sum(traci.edge.getWaitingTime(e) for e in ["O2C", "N2C", "S2C", "E2C"])
        print(f"t={t:.0f}s  véhicules={traci.vehicle.getIDCount()}  attente={attente:.0f}s")

traci.close()
