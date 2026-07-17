#!/bin/bash
# RMSD 分析（复合物）
echo '计算 RMSD...'
# gmx rms -s md.tpr -f md_nojump.xtc -o rmsd.xvg -tu ns
# 参考结构: 复合物初始结构或能量最小化后结构
