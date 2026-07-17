#!/bin/bash
# Docking command for run 3
# Using dockml/dock.py or modern docking
python -m dockml.dock -r receptor.pdb -l ligand.mol2 -o docked_3.pdbqt -b 22 22 22
