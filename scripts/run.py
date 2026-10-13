"""Choisit une zone ou une configuration et lance sa simulation avec TraCI."""

import argparse
from pathlib import Path
import env
import runner
from osm_to_net import convert_osm


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
        
    envSimulation = env.EnvSimulation(config, runner.libsumoRunner())
    # envSimulation = env.EnvSimulation(config, runner.TraciRunner(True)) # Lancer le mode GUI
    envSimulation.run_simulation()


if __name__ == "__main__":
    main()
