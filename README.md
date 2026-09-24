# Q-Up

Q-Up est un logiciel qui permet d'analyser le traffic au feu tricolore via une simulation et apporte une solution de Machine Learning pour optimiser le temps d'attente des conducteurs et de permettre la sécurité en cas de situation dangereuse

## Outils/Langage 

- SUMO 1.25.0
- TraCI 
- Python

## Installation

Après avoir récupéré le repo, ouvrez un terminal dans son dossier.
Python 3.10 à 3.14 est nécessaire. SUMO est fourni par la dépendance
`eclipse-sumo`, il n'est pas nécessaire de l'installer séparément.

Sur macOS / Linux :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Sur Windows (PowerShell) :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si la fenêtre plante sur macOS avec `Could not find the Qt platform plugin "cocoa"`,
réinstallez les composants de la fenêtre dans l'environnement virtuel :

```bash
python -m pip install --force-reinstall PySide6-Essentials==6.10.2
```

## Lancer une simulation

Depuis la racine du repo, avec l'environnement virtuel activé :

```bash
python scripts/run.py --gui
```

Choisissez dans la fenêtre :

- Un `.osm` pour générer les quatre fichiers et lancer la simulation. Cela
  fonctionne même si les anciens fichiers générés ont été supprimés.
- Un `.sumocfg` pour relancer une simulation déjà générée. Ses fichiers réseau
  et routes doivent toujours être présents ; sinon, choisissez l'OSM pour les recréer.

`run.py` appelle directement la fonction `convert_osm()` de `osm_to_net.py`
si vous choisissez un OSM. Avec un `.sumocfg`, il utilise les XML existants sans
les régénérer : vos modifications sont conservées.

Par exemple, choisissez `simulation/cergy/map.osm` pour Cergy ou
`simulation/sandbox/carrefour.sumocfg` pour le carrefour de démonstration.
Les statistiques d'attente utilisent les routes du réseau sélectionné.

Pour exécuter la simulation sans afficher SUMO :

```bash
python scripts/run.py
```

## Générer les fichiers pour les modifier avant simulation

Avec l'environnement virtuel activé, lancez simplement :

```bash
python scripts/osm_to_net.py
```

Une fenêtre permet de choisir un fichier OSM XML, par exemple le fichier
`simulation/cergy/map.osm` fourni dans le repo ou une zone exportée depuis
OpenStreetMap. Aucun chemin à saisir. Les quatre fichiers sont créés à côté
du fichier choisi (`map.net.xml`, `map.trip.xml`, `map.rou.xml`, `map.sumocfg`).
Le script se termine après la génération. Vous pouvez alors modifier les XML,
puis lancer `python scripts/run.py --gui` et choisir le `.sumocfg` généré.
Choisir de nouveau l'OSM régénérerait les fichiers et remplacerait vos modifications.

Pour choisir explicitement les chemins, la commande reste disponible :

```bash
python scripts/osm_to_net.py simulation/cergy/map.osm -o simulation/cergy/carte.net.xml
python scripts/run.py simulation/cergy/carte.sumocfg --gui
```

Le script crée quatre fichiers dans le dossier de sortie :

- `carte.net.xml` : réseau routier converti avec `netconvert`.
- `carte.trip.xml` : trajets aléatoires (départs et destinations).
- `carte.rou.xml` : routes calculées avec `duarouter`.
- `carte.sumocfg` : configuration à ouvrir dans SUMO.

Le trafic est synthétique : un départ est demandé toutes les 10 secondes pendant
une heure, avec une graine fixe pour reproduire les résultats. Les trajets sans
route possible peuvent être écartés. SUMO s'arrête lorsque tous les véhicules
ont terminé leur trajet. Pour changer la demande, modifiez `--end` et `--period`
dans le script. Les fichiers de sortie existants sont remplacés.
