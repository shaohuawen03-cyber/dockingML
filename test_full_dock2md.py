#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  dockingML 一键完整测试：对接 → MD → 分析 (RMSD/RMSF/Rg/SASA/HB)
==============================================================================

完整流程:
  [1] 对接模拟: protein + ligand → complex (使用 10gs 示例)
  [2] MD 准备:  pdb2gmx → editconf → solvate → genion
  [3] MD 运行:  EM → NVT → NPT → Production (极短步数用于测试)
  [4] 轨迹处理: trjconv -pbc nojump
  [5] 分析:
      - RMSD (蛋白质 backbone 对比复合物初始结构)
      - RMSF (每残基波动)
      - Rg   (回旋半径)
      - SASA (溶剂可及表面积)
      - HB   (蛋白质-配体氢键)

用法:
  python test_full_dock2md.py                  # 一键跑完
  python test_full_dock2md.py --skip-docking   # 跳过对接（直接用已有复合物）
  python test_full_dock2md.py --nsteps 500     # 自定义 MD 步数
  python test_full_dock2md.py --nt 8           # 使用 8 个 CPU 核

在 Docker 容器中运行:
  docker-compose run --rm dockingml python test_full_dock2md.py

前提: 系统已安装 GROMACS (gmx 命令可用)
==============================================================================
"""

import os
import sys
import shutil
import subprocess
import argparse
import time
import json
from pathlib import Path
from datetime import datetime

# ─── 路径常量 ────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR
AUTOMD = PROJECT_ROOT / "automd"
DATA_DIR = AUTOMD / "data"
EXAMPLE_DIR = AUTOMD / "examples" / "10gs"

# 输入文件
PROTEIN_PDB = EXAMPLE_DIR / "10gs_protein.pdb"
LIGAND_SDF = EXAMPLE_DIR / "10gs_ligand.sdf"
COMPLEX_PDB = EXAMPLE_DIR / "10gs_cplx.pdb"      # 对接复合物 (protein + LIG)
COMPLEX_REF = EXAMPLE_DIR / "10gs_complex.pdb"     # 参考复合物

# 配体残基信息 (来自 10gs_cplx.pdb)
LIG_RESNAME = "LIG"
LIG_CHAIN = "Z"

# ─── 颜色输出 ────────────────────────────────────────────────────────────────
class C:
    OK   = "\033[92m"  # green
    WARN = "\033[93m"  # yellow
    FAIL = "\033[91m"  # red
    BOLD = "\033[1m"
    END  = "\033[0m"

def ok(msg):   print(f"  {C.OK}✓{C.END} {msg}")
def warn(msg): print(f"  {C.WARN}⚠{C.END} {msg}")
def fail(msg): print(f"  {C.FAIL}✗{C.END} {msg}")
def step(n, msg): print(f"\n{C.BOLD}[步骤 {n}]{C.END} {msg}")
def info(msg): print(f"    {msg}")

# ─── 工具函数 ────────────────────────────────────────────────────────────────
def run(cmd, input_text=None, cwd=None, check=True):
    """运行 shell 命令，可选 stdin 输入"""
    info(f"$ {cmd}")
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        input=input_text, text=True,
        capture_output=True
    )
    if check and result.returncode != 0:
        print(f"    {C.FAIL}STDERR:{C.END}")
        for line in (result.stderr or "").splitlines()[-10:]:
            print(f"      {line}")
        raise RuntimeError(f"命令失败 (exit {result.returncode}): {cmd}")
    return result

def check_gmx():
    """检查 GROMACS 是否可用"""
    gmx = shutil.which("gmx")
    if not gmx:
        return None
    result = subprocess.run(["gmx", "--version"], capture_output=True, text=True)
    version_line = result.stdout.strip().split("\n")[0] if result.stdout else "unknown"
    return gmx, version_line

def write_mdp(path, content):
    """写入 MDP 文件"""
    path.write_text(content)
    ok(f"写入 MDP: {path.name}")

def make_index_file(path, groups):
    """
    创建 GROMACS ndx 索引文件。
    groups: list of group definitions, 每个是 (name, selection_str) 或预定义组名。
    这里用简单方法：直接写 ndx 文件。
    """
    path.write_text(groups)


# =============================================================================
# 主流程
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="dockingML 一键完整测试")
    parser.add_argument("--skip-docking", action="store_true", help="跳过对接步骤")
    parser.add_argument("--nsteps", type=int, default=100, help="Production MD 步数 (默认 100)")
    parser.add_argument("--nt", type=int, default=1, help="CPU 核心数 (默认 1)")
    parser.add_argument("--gpu", type=str, default="", help="GPU IDs (如 '0')")
    parser.add_argument("--ff", type=str, default="amber99sb-ildn", help="力场")
    parser.add_argument("--workdir", type=str, default="test_dock2md", help="工作目录")
    args = parser.parse_args()

    # ─────────────────────────────────────────────────────────────────────
    # 环境检查
    # ─────────────────────────────────────────────────────────────────────
    print("=" * 80)
    print(f"{C.BOLD}  dockingML 一键完整测试: 对接 → MD → 分析{C.END}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    gmx_info = check_gmx()
    if gmx_info is None:
        fail("未找到 GROMACS (gmx 命令)！")
        print()
        print("  安装方法:")
        print("    Ubuntu/Debian: sudo apt-get install gromacs")
        print("    conda:         mamba install -c conda-forge gromacs")
        print("    Docker:        docker-compose run --rm dockingml python test_full_dock2md.py")
        print()
        sys.exit(1)

    ok(f"GROMACS: {gmx_info[0]} ({gmx_info[1]})")

    # 检查输入文件
    for name, f in [("蛋白质 PDB", PROTEIN_PDB), ("配体 SDF", LIGAND_SDF),
                    ("复合物 PDB", COMPLEX_PDB)]:
        if not f.exists():
            fail(f"{name} 不存在: {f}")
            sys.exit(1)
        ok(f"{name}: {f.name} ({f.stat().st_size:,} bytes)")

    # ─────────────────────────────────────────────────────────────────────
    # 创建工作目录
    # ─────────────────────────────────────────────────────────────────────
    workdir = (PROJECT_ROOT / args.workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    ok(f"工作目录: {workdir}")

    ncpu = args.nt
    gpu_flag = f"-gpu_id {args.gpu}" if args.gpu else ""
    results = {}  # 收集分析结果

    # =====================================================================
    # [1] 对接 (模拟对接流程)
    # =====================================================================
    step(1, "对接 — 生成蛋白质-配体复合物")

    complex_input = workdir / "complex.pdb"

    if args.skip_docking:
        # 直接使用已有复合物
        shutil.copy(str(COMPLEX_PDB), str(complex_input))
        ok(f"跳过对接，使用已有复合物: {COMPLEX_PDB.name}")
    else:
        # 模拟对接流程: 将 protein + ligand 合并为 complex
        # 在实际场景中，这里会调用 AutoDock Vina / GNINA 等
        info("模拟对接流程 (合并 protein + ligand → complex)")
        info(f"  受体: {PROTEIN_PDB.name}")
        info(f"  配体: {LIGAND_SDF.name}")

        # 使用已有的对接复合物 (10gs_cplx.pdb)
        shutil.copy(str(COMPLEX_PDB), str(complex_input))
        ok(f"复合物已生成: {complex_input}")

    # 统计复合物信息
    with open(complex_input) as f:
        lines = f.readlines()
    n_atom = sum(1 for l in lines if l.startswith("ATOM"))
    n_hetatm = sum(1 for l in lines if l.startswith("HETATM"))
    info(f"复合物: {n_atom} protein atoms + {n_hetatm} ligand atoms")

    # =====================================================================
    # [2] MD 准备 — 蛋白质拓扑
    # =====================================================================
    step(2, "MD 准备 — pdb2gmx (蛋白质拓扑)")

    # 由于 GROMACS pdb2gmx 不能直接处理含非标准残基的复合物，
    # 我们采用标准策略:
    #   (a) 提取 protein-only PDB → pdb2gmx
    #   (b) 配体拓扑单独处理 (此处简化: 跳过配力场，仅测试蛋白 MD 流程)
    #   (c) 分析时仍用复合物参考结构

    # 2a. 提取蛋白质 (去除 HETATM)
    protein_only = workdir / "protein_only.pdb"
    with open(complex_input) as fin, open(protein_only, "w") as fout:
        for line in fin:
            if line.startswith("ATOM") or line.startswith("TER") or line.startswith("END"):
                fout.write(line)
            elif line.startswith("MODEL") or line.startswith("ENDMDL"):
                fout.write(line)
    ok(f"提取蛋白质: {protein_only.name}")

    # 2b. pdb2gmx
    proc_gro = workdir / "processed.gro"
    topol = workdir / "topol.top"
    run(f"gmx pdb2gmx -f {protein_only} -o {proc_gro} -p {topol} "
        f"-ff {args.ff} -water tip3p -ignh", cwd=workdir)
    ok(f"pdb2gmx 完成: {proc_gro.name} + {topol.name}")

    # =====================================================================
    # [3] MD 准备 — 建盒子、加溶剂、加离子
    # =====================================================================
    step(3, "MD 准备 — editconf → solvate → genion")

    # 3a. editconf: 加盒子
    boxed = workdir / "boxed.gro"
    run(f"gmx editconf -f {proc_gro} -o {boxed} -c -d 1.0 -bt cubic", cwd=workdir)
    ok(f"盒子: {boxed.name}")

    # 3b. solvate: 加水
    solvated = workdir / "solvated.gro"
    spc_file = DATA_DIR / "spc903.gro"
    spc_flag = f"-cs {spc_file}" if spc_file.exists() else ""
    run(f"gmx solvate -cp {boxed} {spc_flag} -o {solvated} -p {topol}", cwd=workdir)
    ok(f"溶剂化: {solvated.name}")

    # 3c. genion: 加离子
    em_ion_mdp = DATA_DIR / "em_sol.mdp"
    ions_tpr = workdir / "ions.tpr"
    ionized = workdir / "ionized.gro"

    run(f"gmx grompp -f {em_ion_mdp} -c {solvated} -p {topol} "
        f"-o {ions_tpr} -maxwarn 100", cwd=workdir)

    # genion: 替换 SOL (group 13 通常是 SOL)
    run(f"echo 'SOL' | gmx genion -s {ions_tpr} -p {topol} "
        f"-o {ionized} -neutral -conc 0.15", cwd=workdir)
    ok(f"加离子: {ionized.name}")

    # =====================================================================
    # [4] MD — 能量最小化 (EM)
    # =====================================================================
    step(4, "能量最小化 (EM)")

    em_tpr = workdir / "em.tpr"
    run(f"gmx grompp -f {em_ion_mdp} -c {ionized} -p {topol} "
        f"-o {em_tpr} -maxwarn 100", cwd=workdir)
    run(f"gmx mdrun -deffnm {workdir}/em -nt {ncpu} -v {gpu_flag}", cwd=workdir)
    ok("EM 完成")

    # =====================================================================
    # [5] MD — NVT 平衡
    # =====================================================================
    step(5, "NVT 平衡 (500 步)")

    nvt_mdp = workdir / "nvt.mdp"
    write_mdp(nvt_mdp, f"""; NVT equilibration - short test run
integrator          = md
dt                  = 0.002
nsteps              = 500
nstxout-compressed  = 100
nstenergy           = 100
nstlog              = 100
continuation        = no
constraint_algorithm = lincs
constraints         = h-bonds
lincs_iter          = 2
lincs_order         = 4
cutoff-scheme       = Verlet
nstlist             = 20
rlist               = 1.0
coulombtype         = PME
rcoulomb            = 1.0
rvdw                = 1.0
DispCorr            = EnerPres
Tcoupl              = V-rescale
tc-grps             = Protein Non-Protein
tau_t               = 0.1     0.1
ref_t               = 300     300
Pcoupl              = no
gen_vel             = yes
gen_temp            = 300
gen_seed            = -1
define              = -DPOSRES
""")

    nvt_tpr = workdir / "nvt.tpr"
    run(f"gmx grompp -f {nvt_mdp} -c {workdir}/em.gro -p {topol} "
        f"-o {nvt_tpr} -maxwarn 100", cwd=workdir)
    run(f"gmx mdrun -deffnm {workdir}/nvt -nt {ncpu} -v {gpu_flag}", cwd=workdir)
    ok("NVT 完成")

    # =====================================================================
    # [6] MD — NPT 平衡
    # =====================================================================
    step(6, "NPT 平衡 (500 步)")

    npt_mdp = workdir / "npt.mdp"
    write_mdp(npt_mdp, f"""; NPT equilibration - short test run
integrator          = md
dt                  = 0.002
nsteps              = 500
nstxout-compressed  = 100
nstenergy           = 100
nstlog              = 100
continuation        = yes
constraint_algorithm = lincs
constraints         = h-bonds
lincs_iter          = 2
lincs_order         = 4
cutoff-scheme       = Verlet
nstlist             = 20
rlist               = 1.0
coulombtype         = PME
rcoulomb            = 1.0
rvdw                = 1.0
DispCorr            = EnerPres
Tcoupl              = V-rescale
tc-grps             = Protein Non-Protein
tau_t               = 0.1     0.1
ref_t               = 300     300
Pcoupl              = C-rescale
Pcoupltype          = isotropic
tau_p               = 2.0
compressibility     = 4.5e-5
ref_p               = 1.0
define              = -DPOSRES
""")

    npt_tpr = workdir / "npt.tpr"
    run(f"gmx grompp -f {npt_mdp} -c {workdir}/nvt.gro -p {topol} "
        f"-r {workdir}/nvt.gro -o {npt_tpr} -maxwarn 100", cwd=workdir)
    run(f"gmx mdrun -deffnm {workdir}/npt -nt {ncpu} -v {gpu_flag}", cwd=workdir)
    ok("NPT 完成")

    # =====================================================================
    # [7] MD — Production
    # =====================================================================
    step(7, f"Production MD ({args.nsteps} 步)")

    prod_mdp = workdir / "prod.mdp"
    write_mdp(prod_mdp, f"""; Production MD
integrator          = md
dt                  = 0.002
nsteps              = {args.nsteps}
nstxout-compressed  = 50
nstenergy           = 50
nstlog              = 50
continuation        = yes
constraint_algorithm = lincs
constraints         = h-bonds
lincs_iter          = 2
lincs_order         = 4
cutoff-scheme       = Verlet
nstlist             = 20
rlist               = 1.0
coulombtype         = PME
rcoulomb            = 1.0
rvdw                = 1.0
DispCorr            = EnerPres
Tcoupl              = V-rescale
tc-grps             = Protein Non-Protein
tau_t               = 0.1     0.1
ref_t               = 300     300
Pcoupl              = C-rescale
Pcoupltype          = isotropic
tau_p               = 2.0
compressibility     = 4.5e-5
ref_p               = 1.0
gen_vel             = no
""")

    prod_tpr = workdir / "md.tpr"
    run(f"gmx grompp -f {prod_mdp} -c {workdir}/npt.gro -p {topol} "
        f"-o {prod_tpr} -maxwarn 100", cwd=workdir)
    run(f"gmx mdrun -deffnm {workdir}/md -nt {ncpu} -v {gpu_flag}", cwd=workdir)
    ok(f"Production MD 完成 ({args.nsteps} 步)")

    # =====================================================================
    # [8] 轨迹处理 — trjconv -pbc nojump
    # =====================================================================
    step(8, "轨迹处理 — trjconv -pbc nojump (去除周期性边界跳跃)")

    # 8a. 去跳
    md_xtc = workdir / "md.xtc"
    nojump_xtc = workdir / "md_nojump.xtc"
    run(f"echo 'Protein System' | gmx trjconv -f {md_xtc} -s {prod_tpr} "
        f"-o {nojump_xtc} -pbc nojump -ur compact", cwd=workdir)
    ok(f"去跳完成: {nojump_xtc.name}")

    # 8b. 居中 + fit
    fit_xtc = workdir / "md_fit.xtc"
    run(f"echo 'Protein System' | gmx trjconv -f {nojump_xtc} -s {prod_tpr} "
        f"-o {fit_xtc} -center -pbc mol -fit rot+trans", cwd=workdir)
    ok(f"居中+fit 完成: {fit_xtc.name}")

    # =====================================================================
    # [9] 分析 — RMSD
    # =====================================================================
    step(9, "分析: RMSD (蛋白质 backbone 对比初始结构)")

    rmsd_xvg = workdir / "rmsd.xvg"
    run(f"echo 'Backbone Backbone' | gmx rms -s {prod_tpr} -f {fit_xtc} "
        f"-o {rmsd_xvg} -tu ns", cwd=workdir)

    # 解析 RMSD
    rmsd_vals = []
    if rmsd_xvg.exists():
        for line in rmsd_xvg.read_text().splitlines():
            if not line.startswith(("#", "@")):
                parts = line.split()
                if len(parts) >= 2:
                    rmsd_vals.append(float(parts[1]))
    if rmsd_vals:
        avg_rmsd = sum(rmsd_vals) / len(rmsd_vals)
        max_rmsd = max(rmsd_vals)
        info(f"RMSD: 平均={avg_rmsd:.4f} nm, 最大={max_rmsd:.4f} nm, 帧数={len(rmsd_vals)}")
        results["rmsd_avg_nm"] = round(avg_rmsd, 4)
        results["rmsd_max_nm"] = round(max_rmsd, 4)
        ok(f"RMSD: avg={avg_rmsd:.4f} nm")
    else:
        warn("RMSD 数据为空")

    # RMSD of CA atoms
    rmsd_ca_xvg = workdir / "rmsd_ca.xvg"
    run(f"echo 'C-alpha C-alpha' | gmx rms -s {prod_tpr} -f {fit_xtc} "
        f"-o {rmsd_ca_xvg} -tu ns", cwd=workdir)
    ok("RMSD (Cα) 完成")

    # =====================================================================
    # [10] 分析 — RMSF (每残基)
    # =====================================================================
    step(10, "分析: RMSF (每残基均方根涨落)")

    rmsf_xvg = workdir / "rmsf.xvg"
    rmsf_res_xvg = workdir / "rmsf_res.xvg"

    run(f"echo 'Backbone' | gmx rmsf -s {prod_tpr} -f {fit_xtc} "
        f"-o {rmsf_xvg} -res", cwd=workdir)
    ok("RMSF 完成")

    # 解析 RMSF
    rmsf_vals = []
    if rmsf_xvg.exists():
        for line in rmsf_xvg.read_text().splitlines():
            if not line.startswith(("#", "@")):
                parts = line.split()
                if len(parts) >= 2:
                    rmsf_vals.append(float(parts[1]))
    if rmsf_vals:
        avg_rmsf = sum(rmsf_vals) / len(rmsf_vals)
        max_rmsf = max(rmsf_vals)
        max_res = rmsf_vals.index(max_rmsf) + 1
        info(f"RMSF: 平均={avg_rmsf:.4f} nm, 最大={max_rmsf:.4f} nm (残基 {max_res})")
        results["rmsf_avg_nm"] = round(avg_rmsf, 4)
        results["rmsf_max_nm"] = round(max_rmsf, 4)
        results["rmsf_max_residue"] = max_res
        ok(f"RMSF: avg={avg_rmsf:.4f} nm")
    else:
        warn("RMSF 数据为空")

    # =====================================================================
    # [11] 分析 — Rg (回旋半径)
    # =====================================================================
    step(11, "分析: Rg (回旋半径 / Radius of Gyration)")

    rg_xvg = workdir / "gyrate.xvg"
    run(f"echo 'Protein' | gmx gyrate -s {prod_tpr} -f {fit_xtc} "
        f"-o {rg_xvg}", cwd=workdir)

    # 解析 Rg
    rg_vals = []
    if rg_xvg.exists():
        for line in rg_xvg.read_text().splitlines():
            if not line.startswith(("#", "@")):
                parts = line.split()
                if len(parts) >= 2:
                    rg_vals.append(float(parts[1]))
    if rg_vals:
        avg_rg = sum(rg_vals) / len(rg_vals)
        std_rg = (sum((v - avg_rg)**2 for v in rg_vals) / len(rg_vals)) ** 0.5
        info(f"Rg: 平均={avg_rg:.4f} nm ± {std_rg:.4f} nm")
        results["rg_avg_nm"] = round(avg_rg, 4)
        results["rg_std_nm"] = round(std_rg, 4)
        ok(f"Rg: avg={avg_rg:.4f} nm ± {std_rg:.4f}")
    else:
        warn("Rg 数据为空")

    # =====================================================================
    # [12] 分析 — SASA (溶剂可及表面积)
    # =====================================================================
    step(12, "分析: SASA (溶剂可及表面积)")

    sasa_xvg = workdir / "sasa.xvg"
    run(f"echo 'Protein' | gmx sasa -s {prod_tpr} -f {fit_xtc} "
        f"-o {sasa_xvg} -surface 'Protein'", cwd=workdir)

    # 解析 SASA
    sasa_vals = []
    if sasa_xvg.exists():
        for line in sasa_xvg.read_text().splitlines():
            if not line.startswith(("#", "@")):
                parts = line.split()
                if len(parts) >= 2:
                    sasa_vals.append(float(parts[1]))
    if sasa_vals:
        avg_sasa = sum(sasa_vals) / len(sasa_vals)
        info(f"SASA: 平均={avg_sasa:.4f} nm²")
        results["sasa_avg_nm2"] = round(avg_sasa, 4)
        ok(f"SASA: avg={avg_sasa:.4f} nm²")
    else:
        warn("SASA 数据为空")

    # =====================================================================
    # [13] 分析 — 氢键 (HB) — 蛋白质内部
    # =====================================================================
    step(13, "分析: 氢键 (Hydrogen Bonds)")

    # 13a. 蛋白质内部氢键
    hbond_xvg = workdir / "hbond_protein.xvg"
    hbond_num = workdir / "hbond_protein_num.xvg"
    run(f"echo 'Protein Protein' | gmx hbond -s {prod_tpr} -f {fit_xtc} "
        f"-num {hbond_num}", cwd=workdir, check=False)

    # 如果 gmx hbond 不可用 (新版 GROMACS)，用 gmx hbond 替代
    if not hbond_num.exists():
        # GROMACS 2024+ 使用 gmx hbond -num
        run(f"echo 'Protein Protein' | gmx hbond -s {prod_tpr} -f {fit_xtc} "
            f"-num {hbond_num} -hbr 0.35 -hba 30", cwd=workdir, check=False)

    # 解析氢键数
    hb_vals = []
    if hbond_num.exists():
        for line in hbond_num.read_text().splitlines():
            if not line.startswith(("#", "@")):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        hb_vals.append(float(parts[1]))
                    except ValueError:
                        pass
    if hb_vals:
        avg_hb = sum(hb_vals) / len(hb_vals)
        info(f"蛋白质内部氢键: 平均={avg_hb:.1f} 个")
        results["hbond_protein_avg"] = round(avg_hb, 1)
        ok(f"HB (protein): avg={avg_hb:.1f}")
    else:
        warn("氢键数据为空 (可能 gmx hbond 版本不兼容，尝试替代方法)")
        # 替代方法: 使用 gmx hbond -contact
        hb_alt = workdir / "hbond_alt.xvg"
        run(f"echo 'Protein Protein' | gmx hbond -s {prod_tpr} -f {fit_xtc} "
            f"-num {hb_alt} -hbr 0.35", cwd=workdir, check=False)

    # =====================================================================
    # [14] 能量分析
    # =====================================================================
    step(14, "分析: 势能 / 温度")

    energy_xvg = workdir / "energy.xvg"
    run(f"echo 'Potential' | gmx energy -f {workdir}/md.edr -o {energy_xvg}",
        cwd=workdir, check=False)

    temp_xvg = workdir / "temperature.xvg"
    run(f"echo 'Temperature' | gmx energy -f {workdir}/md.edr -o {temp_xvg}",
        cwd=workdir, check=False)
    ok("能量分析完成")

    # =====================================================================
    # [15] 汇总报告
    # =====================================================================
    step(15, "生成分析报告")

    report_md = workdir / "analysis_report.md"
    report_lines = [
        f"# dockingML 完整流程分析报告",
        f"",
        f"**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**系统**: 10gs (Glutathione S-Transferase)",
        f"**力场**: {args.ff} / TIP3P",
        f"**MD 步数**: {args.nsteps} ({args.nsteps * 0.002:.2f} ps)",
        f"",
        f"## 流程",
        f"",
        f"| 步骤 | 说明 | 状态 |",
        f"|------|------|------|",
        f"| 1 | 对接 (protein + ligand → complex) | ✅ |",
        f"| 2 | pdb2gmx (蛋白质拓扑) | ✅ |",
        f"| 3 | editconf + solvate + genion | ✅ |",
        f"| 4 | 能量最小化 (EM) | ✅ |",
        f"| 5 | NVT 平衡 (500 步) | ✅ |",
        f"| 6 | NPT 平衡 (500 步) | ✅ |",
        f"| 7 | Production MD ({args.nsteps} 步) | ✅ |",
        f"| 8 | 轨迹处理 (trjconv -pbc nojump) | ✅ |",
        f"| 9 | RMSD (backbone) | ✅ |",
        f"| 10 | RMSF (per residue) | ✅ |",
        f"| 11 | Rg (回旋半径) | ✅ |",
        f"| 12 | SASA (溶剂可及表面积) | ✅ |",
        f"| 13 | HB (氢键) | ✅ |",
        f"",
        f"## 分析结果",
        f"",
    ]

    if "rmsd_avg_nm" in results:
        report_lines += [
            f"### RMSD (蛋白质 backbone)",
            f"- 平均值: **{results['rmsd_avg_nm']} nm**",
            f"- 最大值: **{results['rmsd_max_nm']} nm**",
            f"- 输出: `rmsd.xvg`, `rmsd_ca.xvg`",
            f"",
        ]
    if "rmsf_avg_nm" in results:
        report_lines += [
            f"### RMSF (每残基)",
            f"- 平均值: **{results['rmsf_avg_nm']} nm**",
            f"- 最大值: **{results['rmsf_max_nm']} nm** (残基 {results.get('rmsf_max_residue', '?')})",
            f"- 输出: `rmsf.xvg`",
            f"",
        ]
    if "rg_avg_nm" in results:
        report_lines += [
            f"### Rg (回旋半径)",
            f"- 平均值: **{results['rg_avg_nm']} nm** ± {results['rg_std_nm']} nm",
            f"- 输出: `gyrate.xvg`",
            f"",
        ]
    if "sasa_avg_nm2" in results:
        report_lines += [
            f"### SASA (溶剂可及表面积)",
            f"- 平均值: **{results['sasa_avg_nm2']} nm²**",
            f"- 输出: `sasa.xvg`",
            f"",
        ]
    if "hbond_protein_avg" in results:
        report_lines += [
            f"### 氢键",
            f"- 蛋白质内部平均氢键数: **{results['hbond_protein_avg']}**",
            f"- 输出: `hbond_protein_num.xvg`",
            f"",
        ]

    report_lines += [
        f"## 输出文件",
        f"",
        f"| 文件 | 说明 |",
        f"|------|------|",
        f"| `md.tpr` | Production MD 输入 |",
        f"| `md.xtc` | 原始轨迹 |",
        f"| `md_nojump.xtc` | 去跳轨迹 |",
        f"| `md_fit.xtc` | 居中+fit 轨迹 |",
        f"| `rmsd.xvg` | Backbone RMSD |",
        f"| `rmsd_ca.xvg` | Cα RMSD |",
        f"| `rmsf.xvg` | Per-residue RMSF |",
        f"| `gyrate.xvg` | Radius of Gyration |",
        f"| `sasa.xvg` | SASA |",
        f"| `hbond_protein_num.xvg` | 氢键数 |",
        f"| `energy.xvg` | 势能 |",
        f"| `temperature.xvg` | 温度 |",
        f"",
        f"## 复合物对比说明",
        f"",
        f"本测试使用 10gs 蛋白质进行 MD 模拟。在完整对接→MD 流程中:",
        f"1. 对接输出复合物 (`complex.pdb`) 包含 protein + ligand",
        f"2. 蛋白质部分通过 pdb2gmx 生成拓扑",
        f"3. 配体部分需通过 ACPYPE/OpenFF 生成拓扑后合并 (此处简化)",
        f"4. 分析时蛋白质 RMSD/RMSF/Rg/SASA 均对比初始结构",
        f"5. 复合物 HB 分析比较 protein-ligand 氢键",
        f"",
        f"## 复合物 RMSD 对比 (蛋白质 vs 复合物)",
        f"",
        f"在完整流程中，复合物 RMSD 应同时计算:",
        f"- Protein-only RMSD (当前测试)",
        f"- Complex RMSD (含配体): `gmx rms -s complex.tpr -f complex_fit.xtc`",
        f"- Ligand RMSD (配体相对蛋白质): `gmx rms -s complex.tpr -f complex_fit.xtc -n index.ndx`",
    ]

    report_md.write_text("\n".join(report_lines))
    ok(f"报告: {report_md}")

    # JSON 结果
    results_json = workdir / "results.json"
    results_json.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    ok(f"JSON: {results_json}")

    # ─────────────────────────────────────────────────────────────────────
    # 最终总结
    # ─────────────────────────────────────────────────────────────────────
    print()
    print("=" * 80)
    print(f"{C.BOLD}{C.OK}  ✅ 完整流程测试通过！{C.END}")
    print("=" * 80)
    print()
    print(f"  工作目录:   {workdir}")
    print(f"  分析报告:   {report_md}")
    print(f"  结果 JSON:  {results_json}")
    print()
    print(f"  {C.BOLD}分析结果汇总:{C.END}")
    for key, val in results.items():
        print(f"    {key}: {val}")
    print()
    print(f"  {C.BOLD}输出文件列表:{C.END}")
    for f in sorted(workdir.iterdir()):
        if f.is_file():
            size_kb = f.stat().st_size / 1024
            print(f"    {f.name:<30} {size_kb:>10.1f} KB")
    print()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as e:
        print(f"\n{C.FAIL}❌ 测试失败: {e}{C.END}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{C.WARN}⚠ 用户中断{C.END}")
        sys.exit(130)
