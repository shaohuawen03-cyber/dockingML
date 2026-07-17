#!/usr/bin/env python
"""
Single protein full MD pipeline (production: 100ps NVT, 100ps NPT eq, 100ns prod)
Includes analysis reference and visualization preparation.
"""
import os, sys, subprocess, shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

INPUT_PDB = PROJECT_ROOT / "automd" / "examples" / "10gs" / "10gs_protein.pdb"
OUTPUT_DIR = PROJECT_ROOT / "test" / "md_single"
ANALYSIS_DIR = OUTPUT_DIR / "analysis"

def run_single_md():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 80)
    print(" Single Protein Full MD Pipeline")
    print(" Production: 100ps NVT -> 100ps NPT eq -> 100ns production")
    print("=" * 80)

    # Check input
    input_pdb = INPUT_PDB
    if not input_pdb.exists():
        print(f"✗ Input protein PDB missing: {input_pdb}")
        # Try to use complex protein part or default
        alt = PROJECT_ROOT / "automd" / "examples" / "10gs" / "10gs_protein.pdb"
        if alt.exists():
            input_pdb = alt
        else:
            print("✗ No alternative protein PDB found.")
            return False
    print(f"✓ Input: {input_pdb}")

    # Reference to MDP files
    prod_data = PROJECT_ROOT / "automd" / "data" / "production"
    test_data = PROJECT_ROOT / "automd" / "data" / "test"
    print(f"✓ Production MDP files: {prod_data}")
    print(f"✓ Test MDP files: {test_data}")

    # Generate reference commands for full pipeline
    pipeline_script = OUTPUT_DIR / "md_pipeline_single.sh"
    pipeline_script.write_text("#!/bin/bash\n"
        "# Single protein full MD pipeline (production)\n"
        "# Step 1: Energy minimization (test em.mdp or production em.mdp)\n"
        "# gmx grompp -f em.mdp -c input.gro -p topol.top -o em.tpr -maxwarn 5\n"
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
    print(f"✓ Pipeline script generated: {pipeline_script}")

    # Generate analysis commands for single protein
    analysis_script = ANALYSIS_DIR / "analysis_single.sh"
    analysis_script.write_text("#!/bin/bash\n"
        "# Analysis for single protein trajectory (after nojump processing)\n"
        "# 1. RMSD\n"
        "# gmx rms -s prod.tpr -f prod_nojump.xtc -o rmsd_single.xvg -tu ns\n"
        "# 2. RMSF\n"
        "# gmx rmsf -s prod.tpr -f prod_nojump.xtc -o rmsf_single.xvg -res -o rmsf_res_single.xvg\n"
        "# 3. Rg (radius of gyration)\n"
        "# gmx gyrate -s prod.tpr -f prod_nojump.xtc -o gyrate_single.xvg\n"
        "# 4. SASA\n"
        "# gmx sasa -s prod.tpr -f prod_nojump.xtc -o sasa_single.xvg -surface 'Protein' -output 'Protein'\n"
        "# 5. Hydrogen bonds (if analysis module available)\n"
        "# python -c 'from analysis_plot import plot_hbond; plot_hbond(\"single\")'\n"
    )
    analysis_script.chmod(0o755)
    print(f"✓ Analysis script: {analysis_script}")

    # Generate visualization reference (matplotlib)
    plot_ref = ANALYSIS_DIR / "plot_reference.py"
    plot_ref.write_text("# Visualization reference for single protein\n"
                        "# Uses matplotlib to generate PNG, SVG, PDF\n"
                        "import matplotlib.pyplot as plt\n"
                        "# Example: plot RMSD time series\n"
                        "# plt.plot(time, rmsd)\n"
                        "# plt.savefig('rmsd_single.png', dpi=300)\n"
                        "# plt.savefig('rmsd_single.svg')\n"
                        "# plt.savefig('rmsd_single.pdf')\n")
    print(f"✓ Visualization reference: {plot_ref}")

    return True

if __name__ == "__main__":
    ok = run_single_md()
    sys.exit(0 if ok else 1)
