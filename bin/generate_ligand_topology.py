#!/usr/bin/env python
"""
Ligand Topology Generator for GROMACS
Supports ACPYPE (recommended), CGenFF, and Amber GAFF via antechamber.

Usage examples:
  # ACPYPE (recommended, easiest)
  python bin/generate_ligand_topology.py -i ligand.pdb --method acpype --resname LIG

  # Amber GAFF (via antechamber)
  python bin/generate_ligand_topology.py -i ligand.pdb --method gaff --resname UNL
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def check_command(cmd):
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def generate_with_acpype(pdb_file, resname, charge=0, workdir="."):
    """Generate topology using ACPYPE (recommended)."""
    if not check_command("acpype"):
        print("❌ ACPYPE not found. Install with: pip install acpype")
        print("   or conda install -c conda-forge acpype")
        return False

    print(f"🚀 Running ACPYPE on {pdb_file} (resname={resname}, charge={charge})...")

    cmd = [
        "acpype",
        "-i", str(pdb_file),
        "-b", resname,
        "-c", "bcc",           # AM1-BCC charges
        "-n", str(charge),
        "-o", "gmx"            # output GROMACS format
    ]

    result = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("❌ ACPYPE failed:", result.stderr)
        return False

    # Expected output files
    base = Path(workdir) / f"{resname}.acpype"
    itp = base / f"{resname}_GMX.itp"
    gro = base / f"{resname}_GMX.gro"

    if itp.exists() and gro.exists():
        # Copy to current directory with clean names
        os.system(f"cp {itp} {resname}.itp")
        os.system(f"cp {gro} {resname}.gro")
        print(f"✅ Generated: {resname}.itp and {resname}.gro")
        return True
    else:
        print("❌ Expected output files not found in acpype directory")
        return False

def generate_with_gaff(pdb_file, resname, charge=0, workdir="."):
    """Generate topology using Amber GAFF + antechamber."""
    if not check_command("antechamber"):
        print("❌ antechamber not found. Please activate AmberTools environment.")
        return False

    print(f"🚀 Running Amber GAFF (antechamber) on {pdb_file}...")

    # This is a simplified version - full implementation would need more steps
    print("⚠️  GAFF generation is complex. Consider using ACPYPE instead.")
    return False

def main():
    parser = argparse.ArgumentParser(description="Generate ligand .itp + .gro for GROMACS")
    parser.add_argument("-i", "--input", required=True, help="Ligand PDB file")
    parser.add_argument("--method", choices=["acpype", "gaff"], default="acpype",
                        help="Topology generation method (default: acpype)")
    parser.add_argument("--resname", default="LIG", help="Residue name in topology (default: LIG)")
    parser.add_argument("--charge", type=int, default=0, help="Net charge of ligand (default: 0)")
    parser.add_argument("--workdir", default=".", help="Working directory")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ Input file not found: {args.input}")
        sys.exit(1)

    if args.method == "acpype":
        success = generate_with_acpype(args.input, args.resname, args.charge, args.workdir)
    else:
        success = generate_with_gaff(args.input, args.resname, args.charge, args.workdir)

    if success:
        print("\n✅ Ligand topology generation completed!")
        print("   You can now use the generated .itp and .gro in the GUI Ligand Simulator tab.")
    else:
        print("\n❌ Topology generation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
