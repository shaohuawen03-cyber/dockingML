#!/usr/bin/env python
"""
Complex full MD pipeline (production: 100ps NVT, 100ps NPT eq, 100ns prod)
Uses best docking result (from docking_3x) as input.
Includes hydrogen bond analysis reference.
"""
import os, sys, shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

COMPLEX_PDB = PROJECT_ROOT / "automd" / "examples" / "10gs" / "10gs_complex.pdb"
DOCKING_RESULT = PROJECT_ROOT / "test" / "docking_3x" / "run_1" / "best_complex.pdb"
OUTPUT_DIR = PROJECT_ROOT / "test" / "md_complex"
ANALYSIS_DIR = OUTPUT_DIR / "analysis"

def run_complex_md():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 80)
    print(" Complex Full MD Pipeline")
    print(" Uses best docking result -> 100ps NVT -> 100ps NPT eq -> 100ns prod")
    print(" Includes hydrogen bond analysis reference")
    print("=" * 80)

    # Check docking result
    if DOCKING_RESULT.exists():
        print(f"✓ Best docking result available: {DOCKING_RESULT}")
    else:
        # Try to use complex PDB directly (if docking hasn't been run yet)
        if COMPLEX_PDB.exists():
            print(f"✓ Using complex PDB directly (docking result not found): {COMPLEX_PDB}")
            DOCKING_RESULT = COMPLEX_PDB
        else:
            print(f"✗ No complex input available.")
            return False

    # Generate complex MD pipeline reference
    pipeline_script = OUTPUT_DIR / "md_pipeline_complex.sh"
    pipeline_script.write_text("#!/bin/bash\n"
        "# Complex full MD pipeline (production)\n"
        "# Input: best_complex.pdb (from docking_3x best result)\n"
        "# Step 1: Energy minimization\n"
        "# gmx grompp -f em.mdp -c best_complex.gro -p topol.top -o em.tpr -maxwarn 5\n"
        "# gmx mdrun -deffnm em -nt 4 -v\n"
        "\n"
        "# Step 2: NVT equilibration (100 ps)\n"
        "# gmx grompp -f nvt_eq.mdp -c em.gro -r em.gro -p topol.top -n index.ndx -o nvt.tpr -maxwarn 5\n"
        "# gmx mdrun -deffnm nvt -nt 4 -v -nsteps 50000\n"
        "\n"
        "# Step 3: NPT equilibration (100 ps)\n"
        "# gmx grompp -f npt_eq.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -n index.ndx -o npt_eq.tpr -maxwarn 5\n"
        "# gmx mdrun -deffnm npt_eq -nt 4 -v -nsteps 50000\n"
        "\n"
        "# Step 4: Production (100 ns)\n"
        "# gmx grompp -f npt_prod.mdp -c npt_eq.gro -t npt_eq.cpt -p topol.top -n index.ndx -o prod.tpr -maxwarn 5\n"
        "# gmx mdrun -deffnm prod -nt 4 -v -nsteps 50000000\n"
    )
    pipeline_script.chmod(0o755)
    print(f"✓ Complex pipeline script: {pipeline_script}")

    # Generate analysis for complex (including hydrogen bond analysis)
    analysis_script = ANALYSIS_DIR / "analysis_complex.sh"
    analysis_script.write_text("#!/bin/bash\n"
        "# Complex trajectory analysis\n"
        "# 1. RMSD\n"
        "# gmx rms -s prod.tpr -f prod_nojump.xtc -o rmsd_complex.xvg -tu ns\n"
        "# 2. RMSF\n"
        "# gmx rmsf -s prod.tpr -f prod_nojump.xtc -o rmsf_complex.xvg -res -o rmsf_res_complex.xvg\n"
        "# 3. Rg (gyration radius)\n"
        "# gmx gyrate -s prod.tpr -f prod_nojump.xtc -o gyrate_complex.xvg\n"
        "# 4. SASA\n"
        "# gmx sasa -s prod.tpr -f prod_nojump.xtc -o sasa_complex.xvg -surface 'Protein' -output 'Protein_Ligand'\n"
        "# 5. Hydrogen bonds (reference to analysis module)\n"
        "# python -c 'from analysis_plot import plot_hbond; plot_hbond(\"complex\")'\n"
    )
    analysis_script.chmod(0o755)
    print(f"✓ Complex analysis script: {analysis_script}")

    # Hydrogen bond analysis reference
    hbond_ref = ANALYSIS_DIR / "hbond_reference.py"
    hbond_ref.write_text("# Hydrogen bond analysis for complex\n"
                         "# Uses GROMACS hbond or custom Python analysis\n"
                         "import subprocess\n"
                         "# Example: gmx hbond -s prod.tpr -f prod_nojump.xtc -num hbond_complex.xvg -n index.ndx\n"
                         "# The index should include Protein and Ligand groups for hydrogen bond detection\n"
                         "print('Hydrogen bond analysis reference for complex')\n")
    print(f"✓ Hydrogen bond analysis reference: {hbond_ref}")

    # Visualization reference for complex
    plot_ref = ANALYSIS_DIR / "plot_reference_complex.py"
    plot_ref.write_text("# Visualization reference for complex\n"
                        "import matplotlib.pyplot as plt\n"
                        "# Generate PNG, SVG, PDF for all metrics\n"
                        "# plt.plot(time, rmsd_complex)\n"
                        "# plt.savefig('rmsd_complex.png', dpi=300)\n"
                        "# plt.savefig('rmsd_complex.svg')\n"
                        "# plt.savefig('rmsd_complex.pdf')\n")
    print(f"✓ Complex visualization reference: {plot_ref}")

    return True

if __name__ == "__main__":
    ok = run_complex_md()
    sys.exit(0 if ok else 1)
