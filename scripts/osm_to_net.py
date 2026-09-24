"""Génère les fichiers SUMO depuis un OSM, sans lancer la simulation."""

import argparse
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import sumolib


def convert_osm(osm, output=None):
    """Génère les quatre fichiers et renvoie le chemin du .sumocfg."""
    osm = Path(osm)
    output = Path(output) if output else osm.with_suffix(".net.xml")
    output.parent.mkdir(parents=True, exist_ok=True)
    netconvert = sumolib.checkBinary("netconvert")
    subprocess.run(
        [netconvert,
         "--osm-files", str(osm), "--output-file", str(output)],
        check=True,
    )

    # randomTrips génère les trajets et utilise duarouter pour calculer les routes.
    prefix = output.name.removesuffix(".net.xml")
    trips = output.with_name(f"{prefix}.trip.xml")
    routes = output.with_name(f"{prefix}.rou.xml")
    config = output.with_name(f"{prefix}.sumocfg")
    sumo_home = Path(os.environ.get("SUMO_HOME", Path(netconvert).resolve().parent.parent))
    subprocess.run(
        [sys.executable, str(sumo_home / "tools" / "randomTrips.py"),
         "-n", str(output), "-o", str(trips), "-r", str(routes),
         "--end", "3600", "--period", "10", "--seed", "42"],
        check=True,
    )

    # Les chemins sont relatifs au fichier .sumocfg.
    configuration = ET.Element("configuration")
    inputs = ET.SubElement(configuration, "input")
    ET.SubElement(inputs, "net-file", value=output.name)
    ET.SubElement(inputs, "route-files", value=routes.name)
    ET.indent(configuration)
    ET.ElementTree(configuration).write(config, encoding="utf-8", xml_declaration=True)
    print(f"Simulation créée : {config}")
    return config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("osm", nargs="?", type=Path, help="Fichier OSM (sinon ouvre une fenêtre)")
    parser.add_argument("-o", "--output", type=Path, help="Fichier .net.xml de sortie")
    args = parser.parse_args()

    if args.osm is None:
        from PySide6.QtWidgets import QApplication, QFileDialog

        app = QApplication([])
        filename, _ = QFileDialog.getOpenFileName(
            None, "Choisir une zone OSM",
            str(Path(__file__).resolve().parents[1] / "simulation"),
            "Fichiers OpenStreetMap (*.osm *.osm.xml);;Tous les fichiers (*)",
        )
        if not filename:
            return
        args.osm = Path(filename)

    convert_osm(args.osm, args.output)


if __name__ == "__main__":
    main()
