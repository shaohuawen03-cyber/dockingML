#!/bin/bash
# Installation script for independent docking-ML pipeline
# Includes: GROMACS, AmberTools, Open Babel, conda environment, Python dependencies
# Usage: bash install_dependencies.sh

set -e

echo "=========================================="
echo " Independent Pipeline Dependency Installation"
echo "=========================================="

# 1. Check existing installations
echo "[1/7] Checking existing installations..."
which gmx && echo "  ✓ GROMACS (gmx) found" || echo "  ✗ GROMACS not found"
which antechamber && echo "  ✓ AmberTools (antechamber) found" || echo "  ✗ AmberTools not found"
which tleap && echo "  ✓ AmberTools (tleap) found" || echo "  ✗ tleap not found"
which conda && echo "  ✓ conda found" || echo "  ✗ conda not found"
which python3 && echo "  ✓ python3 found" || PYTHON_CMD=python

# 2. Python dependencies (matplotlib, numpy, etc.)
echo "[2/7] Installing Python dependencies..."
pip install --quiet matplotlib numpy pandas joblib openbabel || echo "  ⚠ Some Python packages may need manual installation"

# 3. Conda environment (optional but recommended)
echo "[3/7] Setting up conda environment (if conda available)..."
if command -v conda >/dev/null 2>&1; then
    conda create -n dockingmd python=3.10 -y 2>/dev/null || echo "  ⚠ Conda env 'dockingmd' may already exist"
    echo "  Run: conda activate dockingmd"
else
    echo "  ⚠ conda not available; using system Python"
fi

# 4. GROMACS installation reference (not executed, instructions only)
echo "[4/7] GROMACS installation reference..."
echo "  To install GROMACS:"
echo "    conda install -c conda-forge gromacs -y"
echo "  OR build from source: https://manual.gromacs.org/"

# 5. AmberTools installation reference
echo "[5/7] AmberTools installation reference..."
echo "  Download from: https://ambermd.org/AmberTools.php"
echo "  Then: ./configure gnu; make install"
echo "  Set AMBERHOME in environment."

# 6. Docking tools reference
echo "[6/7] Docking tools reference..."
echo "  AutoDock Vina: https://vina.scripps.edu/"
echo "  Meeko (RDKit-based): pip install meeko"
echo "  Open Babel: conda install -c conda-forge openbabel"

# 7. Dependency verification script
echo "[7/7] Running dependency check..."
python3 -c "
import subprocess, sys
missing = []
for cmd in ['gmx', 'antechamber', 'tleap', 'obabel', 'python3']:
    try:
        subprocess.run(['which', cmd], capture_output=True, check=True)
        print(f'  ✓ {cmd}')
    except:
        print(f'  ✗ {cmd} MISSING')
        missing.append(cmd)
if missing:
    print(f'  ⚠ Missing: {missing}')
else:
    print('  ✓ All core dependencies available.')
"

echo "=========================================="
echo " Installation references complete."
echo " To fully install, follow the printed instructions."
echo "=========================================="
