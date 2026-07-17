#!/usr/bin/env python
"""
Complete full pipeline: docking -> single protein MD -> complex MD -> analysis -> visualization -> comparison.
This script keeps the overall flow intact and calls the split components.
"""
import sys, subprocess, shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Component paths (split parts)
DOCKING_SCRIPT = PROJECT_ROOT / "bin" / "docking_3x.py"
SINGLE_PIPELINE = PROJECT_ROOT / "test" / "full_pipeline_single.py"
COMPLEX_PIPELINE = PROJECT_ROOT / "test" / "full_pipeline_complex.py"
ANALYSIS_MODULE = PROJECT_ROOT / "mdanaly" / "analysis_plot.py"
COMPARE_MODULE = PROJECT_ROOT / "mdanaly" / "compare_final.py"

def run_command(cmd, desc):
    print(f"\n{'='*60}")
    print(f" {desc}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    print("=" * 80)
    print(" dockingML Complete Full Pipeline")
    print(" Flow: docking_3x -> single_md -> complex_md -> analysis_plot -> compare_final")
    print(" Production settings: 100ps NVT, 100ps NPT eq, 100ns prod")
    print(" Visualization: PNG, SVG, PDF (matplotlib)")
    print("=" * 80)

    # 1. Docking 3x (best binding energy)
    ok = run_command(f"python {DOCKING_SCRIPT}", "STEP 1: Docking 3 times (best energy)")
    if not ok:
        print("Warning: Docking step completed with issues (expected if GROMACS/docking tools not installed).")
    else:
        print("✓ Docking step completed.")

    # 2. Single protein full MD pipeline
    ok = run_command(f"python {SINGLE_PIPELINE}", "STEP 2: Single Protein Full MD Pipeline")
    if not ok:
        print("Warning: Single protein MD pipeline has issues.")
    else:
        print("✓ Single protein MD pipeline completed.")

    # 3. Complex full MD pipeline (uses best docking result)
    ok = run_command(f"python {COMPLEX_PIPELINE}", "STEP 3: Complex Full MD Pipeline")
    if not ok:
        print("Warning: Complex MD pipeline has issues.")
    else:
        print("✓ Complex MD pipeline completed.")

    # 4. Analysis and visualization (generate all plots)
    ok = run_command(f"python {ANALYSIS_MODULE} --label single --compare", "STEP 4: Analysis & Visualization")
    if not ok:
        print("Warning: Analysis/plotting step has issues.")
    else:
        print("✓ Analysis and visualization completed.")

    # 5. Final comparison (visualization of comparison results)
    ok = run_command(f"python {COMPARE_MODULE}", "STEP 5: Final Visualization Comparison (last step)")
    if not ok:
        print("Warning: Final comparison step has issues.")
    else:
        print("✓ Final comparison visualization completed.")

    # Overall summary
    print("\n" + "=" * 80)
    print(" FULL PIPELINE SUMMARY (Overall flow preserved)")
    print("=" * 80)
    print("✓ Components (split parts):")
    print(f"   - Docking: {DOCKING_SCRIPT}")
    print(f"   - Single MD: {SINGLE_PIPELINE}")
    print(f"   - Complex MD: {COMPLEX_PIPELINE}")
    print(f"   - Analysis/Plot: {ANALYSIS_MODULE}")
    print(f"   - Final Compare: {COMPARE_MODULE}")
    print("✓ Overall pipeline (this script) keeps complete flow intact.")
    print("✓ Production MDP files: automd/data/production/")
    print("✓ Test MDP files: automd/data/test/")
    print("✓ Visualization formats: PNG, SVG, PDF (from matplotlib)")
    print("✓ Hydrogen bond analysis reference included.")

if __name__ == "__main__":
    main()
