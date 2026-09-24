"""Choisit une zone ou une configuration et lance sa simulation avec TraCI."""

import argparse
from pathlib import Path

import sumolib
import traci

from osm_to_net import convert_osm


def run_simulation(config, gui=False):
    """Exécute une configuration SUMO et affiche les statistiques TraCI."""
    SUMO = sumolib.checkBinary("sumo-gui" if gui else "sumo")
    cmd = [SUMO, "-c", str(config)]
    if gui:
        cmd += ["--start", "--delay", "100", "--quit-on-end"]

    traci.start(cmd)

    try:
        edges = [edge for edge in traci.edge.getIDList() if not edge.startswith(":")]
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            t = traci.simulation.getTime()
            if t % 300 == 0:
                attente = sum(traci.edge.getWaitingTime(edge) for edge in edges)
                print(f"t={t:.0f}s  véhicules={traci.vehicle.getIDCount()}  attente={attente:.0f}s")
    finally:
        traci.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path, help="Fichier OSM ou .sumocfg")
    parser.add_argument("--gui", action="store_true", help="Afficher la simulation")
    args = parser.parse_args()

    if args.source is None:
        from PySide6.QtWidgets import QApplication, QFileDialog

        app = QApplication([])
        filename, _ = QFileDialog.getOpenFileName(
            None, "Choisir une zone OSM ou une simulation",
            str(Path(__file__).resolve().parents[1] / "simulation"),
            "Zones et simulations (*.osm *.osm.xml *.sumocfg)",
        )
        if not filename:
            return
        args.source = Path(filename)

    config = args.source.resolve()
    if config.suffix != ".sumocfg":
        config = convert_osm(config)
    run_simulation(config, gui=args.gui)


if __name__ == "__main__":
    main()
