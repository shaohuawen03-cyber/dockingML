# Hydrogen bond analysis for single
# Using GROMACS hbond or custom analysis
# Command reference: gmx hbond -s prod.tpr -f prod_nojump.xtc -num hbond_single.xvg -n index.ndx
# Index file should contain Protein and Ligand groups.
# Visualization: plt.plot(time, hbonds)
# Save as PNG, SVG, PDF.
