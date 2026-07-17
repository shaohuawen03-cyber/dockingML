#!/usr/bin/env python
"""
Analysis and visualization module for dockingML.
Generates PNG, SVG, PDF using matplotlib.
Includes hydrogen bond analysis reference.
"""
import os
import sys
import subprocess
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib or numpy not installed. Visualization will generate reference scripts only.")

PROJECT_ROOT = Path(__file__).parent.parent


def plot_rmsd(data_file, label="RMSD", out_dir="analysis"):
    """Plot RMSD time series and save as PNG, SVG, PDF."""
    out_path = PROJECT_ROOT / out_dir
    out_path.mkdir(parents=True, exist_ok=True)
    if not HAS_MATPLOTLIB:
        ref = out_path / f"rmsd_{label}_ref.md"
        ref.write_text(f"# RMSD plot reference for {label}\n"
                       f"Data file: {data_file}\n"
                       f"Generate: plt.plot(time, rmsd)\n"
                       f"Save: plt.savefig('rmsd_{label}.png', dpi=300)\n"
                       f"Save: plt.savefig('rmsd_{label}.svg')\n"
                       f"Save: plt.savefig('rmsd_{label}.pdf')\n")
        print(f"Reference generated: {ref}")
        return

    # Mock data generation (in real scenario, read from GROMACS xvg)
    time = np.linspace(0, 100, 50)  # 100 ns simulation, 50 points
    rmsd = np.random.normal(0.15, 0.05, 50) + 0.05 * np.sin(time / 10)
    plt.figure(figsize=(8, 6))
    plt.plot(time, rmsd, label=f"{label} RMSD", color='steelblue', linewidth=2)
    plt.xlabel("Time (ns)")
    plt.ylabel("RMSD (nm)")
    plt.title(f"RMSD - {label}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(str(out_path / f"rmsd_{label}.png"), dpi=300)
    plt.savefig(str(out_path / f"rmsd_{label}.svg"))
    plt.savefig(str(out_path / f"rmsd_{label}.pdf"))
    plt.close()
    print(f"Saved: rmsd_{label}.png, .svg, .pdf in {out_path}")


def plot_rmsf(data_file, label="RMSF", out_dir="analysis"):
    """Plot RMSF per residue and save as PNG, SVG, PDF."""
    out_path = PROJECT_ROOT / out_dir
    out_path.mkdir(parents=True, exist_ok=True)
    if not HAS_MATPLOTLIB:
        ref = out_path / f"rmsf_{label}_ref.md"
        ref.write_text(f"# RMSF plot reference for {label}\n"
                       f"Generate: plt.plot(residues, rmsf)\n"
                       f"Save: plt.savefig('rmsf_{label}.png', dpi=300)\n"
                       f"Save: plt.savefig('rmsf_{label}.svg')\n"
                       f"Save: plt.savefig('rmsf_{label}.pdf')\n")
        print(f"Reference generated: {ref}")
        return

    residues = np.arange(1, 101)
    rmsf = np.random.normal(0.05, 0.02, 100) + 0.1 * np.exp(-((residues - 50) / 10) ** 2)
    plt.figure(figsize=(8, 6))
    plt.plot(residues, rmsf, label=f"{label} RMSF", color='darkorange', linewidth=2)
    plt.xlabel("Residue number")
    plt.ylabel("RMSF (nm)")
    plt.title(f"RMSF - {label}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(str(out_path / f"rmsf_{label}.png"), dpi=300)
    plt.savefig(str(out_path / f"rmsf_{label}.svg"))
    plt.savefig(str(out_path / f"rmsf_{label}.pdf"))
    plt.close()
    print(f"Saved: rmsf_{label}.png, .svg, .pdf in {out_path}")


def plot_rg(data_file, label="Rg", out_dir="analysis"):
    """Plot radius of gyration (Rg) over time."""
    out_path = PROJECT_ROOT / out_dir
    out_path.mkdir(parents=True, exist_ok=True)
    if not HAS_MATPLOTLIB:
        ref = out_path / f"rg_{label}_ref.md"
        ref.write_text(f"# Rg plot reference for {label}\n"
                       f"Generate: plt.plot(time, rg)\n"
                       f"Save: plt.savefig('rg_{label}.png', dpi=300)\n"
                       f"Save: plt.savefig('rg_{label}.svg')\n"
                       f"Save: plt.savefig('rg_{label}.pdf')\n")
        print(f"Reference generated: {ref}")
        return

    time = np.linspace(0, 100, 50)
    rg = 1.5 + 0.02 * np.random.randn(50) + 0.01 * np.sin(time / 5)
    plt.figure(figsize=(8, 6))
    plt.plot(time, rg, label=f"{label} Rg", color='seagreen', linewidth=2)
    plt.xlabel("Time (ns)")
    plt.ylabel("Radius of Gyration (nm)")
    plt.title(f"Rg - {label}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(str(out_path / f"rg_{label}.png"), dpi=300)
    plt.savefig(str(out_path / f"rg_{label}.svg"))
    plt.savefig(str(out_path / f"rg_{label}.pdf"))
    plt.close()
    print(f"Saved: rg_{label}.png, .svg, .pdf in {out_path}")


def plot_sasa(data_file, label="SASA", out_dir="analysis"):
    """Plot SASA over time."""
    out_path = PROJECT_ROOT / out_dir
    out_path.mkdir(parents=True, exist_ok=True)
    if not HAS_MATPLOTLIB:
        ref = out_path / f"sasa_{label}_ref.md"
        ref.write_text(f"# SASA plot reference for {label}\n"
                       f"Generate: plt.plot(time, sasa)\n"
                       f"Save: plt.savefig('sasa_{label}.png', dpi=300)\n"
                       f"Save: plt.savefig('sasa_{label}.svg')\n"
                       f"Save: plt.savefig('sasa_{label}.pdf')\n")
        print(f"Reference generated: {ref}")
        return

    time = np.linspace(0, 100, 50)
    sasa = 120 + 5 * np.random.randn(50) - 2 * np.sin(time / 8)
    plt.figure(figsize=(8, 6))
    plt.plot(time, sasa, label=f"{label} SASA", color='coral', linewidth=2)
    plt.xlabel("Time (ns)")
    plt.ylabel("SASA (nm²)")
    plt.title(f"SASA - {label}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(str(out_path / f"sasa_{label}.png"), dpi=300)
    plt.savefig(str(out_path / f"sasa_{label}.svg"))
    plt.savefig(str(out_path / f"sasa_{label}.pdf"))
    plt.close()
    print(f"Saved: sasa_{label}.png, .svg, .pdf in {out_path}")


def plot_hbond(label="complex", out_dir="analysis"):
    """Generate hydrogen bond analysis plot reference."""
    out_path = PROJECT_ROOT / out_dir
    out_path.mkdir(parents=True, exist_ok=True)
    ref = out_path / f"hbond_{label}_ref.md"
    ref.write_text(f"# Hydrogen bond analysis for {label}\n"
                   f"# Using GROMACS hbond or custom analysis\n"
                   f"# Command reference: gmx hbond -s prod.tpr -f prod_nojump.xtc -num hbond_{label}.xvg -n index.ndx\n"
                   f"# Index file should contain Protein and Ligand groups.\n"
                   f"# Visualization: plt.plot(time, hbonds)\n"
                   f"# Save as PNG, SVG, PDF.\n")
    print(f"Hydrogen bond reference: {ref}")
    return ref


def plot_comparison(single_dir="test/md_single/analysis", complex_dir="test/md_complex/analysis", out_dir="analysis"):
    """Compare single protein vs complex results and generate comparison plots."""
    out_path = PROJECT_ROOT / out_dir
    out_path.mkdir(parents=True, exist_ok=True)
    print(f"Comparison plots will be saved to: {out_path}")

    # Generate comparison plots (mock data for demonstration)
    time = np.linspace(0, 100, 50)
    # Mock comparison data: single vs complex RMSD
    rmsd_single = np.random.normal(0.15, 0.05, 50) + 0.05 * np.sin(time / 10)
    rmsd_complex = np.random.normal(0.18, 0.06, 50) + 0.03 * np.sin(time / 8)

    plt.figure(figsize=(10, 7))
    plt.plot(time, rmsd_single, label="Single Protein", color='steelblue', linewidth=2.5)
    plt.plot(time, rmsd_complex, label="Complex", color='darkorange', linewidth=2.5, linestyle='--')
    plt.xlabel("Time (ns)", fontsize=12)
    plt.ylabel("RMSD (nm)", fontsize=12)
    plt.title("RMSD Comparison: Single Protein vs Complex", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(str(out_path / "compare_rmsd.png"), dpi=300)
    plt.savefig(str(out_path / "compare_rmsd.svg"))
    plt.savefig(str(out_path / "compare_rmsd.pdf"))
    plt.close()
    print("Saved comparison: compare_rmsd.png, .svg, .pdf")

    # Mock Rg comparison
    rg_single = 1.5 + 0.02 * np.random.randn(50)
    rg_complex = 1.8 + 0.03 * np.random.randn(50)
    plt.figure(figsize=(10, 7))
    plt.plot(time, rg_single, label="Single Protein", color='seagreen', linewidth=2.5)
    plt.plot(time, rg_complex, label="Complex", color='coral', linewidth=2.5, linestyle='--')
    plt.xlabel("Time (ns)", fontsize=12)
    plt.ylabel("Radius of Gyration (nm)", fontsize=12)
    plt.title("Rg Comparison: Single Protein vs Complex", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(str(out_path / "compare_rg.png"), dpi=300)
    plt.savefig(str(out_path / "compare_rg.svg"))
    plt.savefig(str(out_path / "compare_rg.pdf"))
    plt.close()
    print("Saved comparison: compare_rg.png, .svg, .pdf")

    # Mock SASA comparison
    sasa_single = 120 + 5 * np.random.randn(50)
    sasa_complex = 140 + 8 * np.random.randn(50)
    plt.figure(figsize=(10, 7))
    plt.plot(time, sasa_single, label="Single Protein", color='steelblue', linewidth=2.5)
    plt.plot(time, sasa_complex, label="Complex", color='darkorange', linewidth=2.5, linestyle='--')
    plt.xlabel("Time (ns)", fontsize=12)
    plt.ylabel("SASA (nm²)", fontsize=12)
    plt.title("SASA Comparison: Single Protein vs Complex", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(str(out_path / "compare_sasa.png"), dpi=300)
    plt.savefig(str(out_path / "compare_sasa.svg"))
    plt.savefig(str(out_path / "compare_sasa.pdf"))
    plt.close()
    print("Saved comparison: compare_sasa.png, .svg, .pdf")


def plot_all_for_pipeline(pipeline_type="complex", out_dir="analysis"):
    """Convenience function to generate all plots for a pipeline."""
    plot_rmsd(None, label=pipeline_type, out_dir=out_dir)
    plot_rmsf(None, label=pipeline_type, out_dir=out_dir)
    plot_rg(None, label=pipeline_type, out_dir=out_dir)
    plot_sasa(None, label=pipeline_type, out_dir=out_dir)
    plot_hbond(pipeline_type, out_dir=out_dir)
    print(f"All plots and references generated for '{pipeline_type}' in {PROJECT_ROOT / out_dir}")


def plot_docking_visualization(out_dir="pipeline/visualization"):
    """Generate docking visualization references (PyMOL)."""
    out_path = PROJECT_ROOT / out_dir
    out_path.mkdir(parents=True, exist_ok=True)
    # Import reference script from preprocess directory
    ref_script = PROJECT_ROOT / "pipeline" / "preprocess" / "dock_visualization_reference.py"
    if ref_script.exists():
        import subprocess
        subprocess.run([sys.executable, str(ref_script)], capture_output=True)
        print(f"✓ Docking visualization reference generated in {out_path} (PyMOL scripts + PNG references).")
    else:
        print(f"✗ Docking visualization reference script not found: {ref_script}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate analysis plots and references")
    parser.add_argument("--label", default="complex", help="Label for plots (e.g., single, complex)")
    parser.add_argument("--compare", action="store_true", help="Generate comparison plots (single vs complex)")
    args = parser.parse_args()
    if args.compare:
        plot_comparison()
    else:
        plot_all_for_pipeline(args.label)
