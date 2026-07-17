# Final Visualization Comparison Report

## Pipeline Overview
1. Docking 3x (best binding energy selected)
2. Single Protein Full MD (100ps NVT, 100ps NPT eq, 100ns prod)
3. Complex Full MD (100ps NVT, 100ps NPT eq, 100ns prod)
4. Analysis (RMSD, RMSF, Rg, SASA, Hydrogen Bonds)
5. Visualization (matplotlib PNG, SVG, PDF)
6. Final Comparison (this report)

## Key Comparisons
- **RMSD**: Complex may show higher initial fluctuations due to ligand flexibility.
- **Rg**: Complex Rg should be slightly larger than single protein due to ligand presence.
- **SASA**: Complex SASA may decrease over time as protein-ligand interface buries surface area.
- **Hydrogen Bonds**: Complex analysis includes H-bond count between protein and ligand.

## Visualization Formats
- PNG: high-resolution (300 dpi) for presentations.
- SVG: vector format for editing and publication.
- PDF: vector format for reports.

## File Locations
- Single protein analysis: `test/md_single/analysis/`
- Complex analysis: `test/md_complex/analysis/`
- Comparison plots: `analysis/compare_*.png/.svg/.pdf`
- Docking best result: `test/docking_3x/run_X/best_complex.pdb`
