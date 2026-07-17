#!/bin/bash
# SASA 分析（复合物）
echo '计算 SASA...'
# gmx sasa -s md.tpr -f md_nojump.xtc -o sasa.xvg -surface 'Protein' -output 'Protein_Ligand'
# 说明: 对复合物（Protein + Ligand）计算 SASA
