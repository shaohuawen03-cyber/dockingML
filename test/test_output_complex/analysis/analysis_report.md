# 复合物分析报告模板

## 输入
- 复合物: `automd/examples/10gs/10gs_complex.pdb`
- 轨迹（去除跳跃后）: `md_nojump.xtc`
- 结构: `md.tpr`

## 分析步骤
1. **轨迹预处理**: `gmx trjconv -pbc nojump`
2. **RMSD**: `gmx rms -o rmsd.xvg`
3. **RMSF**: `gmx rmsf -res -o rmsf_res.xvg`
4. **Rg**: `gmx gyrate -o gyrate.xvg`
5. **SASA**: `gmx sasa -surface 'Protein' -output 'Protein_Ligand' -o sasa.xvg`

## 说明
- 以复合物测试跑通为准，分析脚本已添加到测试目录。
- 对接部分（dockml/）未被删除，可继续组装对接 → 动力学流程。
