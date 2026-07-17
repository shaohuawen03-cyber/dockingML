#!/bin/bash
# 轨迹去除跳跃脚本（复合物测试标准步骤）
echo '运行 gmx trjconv -pbc nojump ...'
# gmx trjconv -f md.xtc -s md.tpr -o md_nojump.xtc -pbc nojump -ur compact -center
