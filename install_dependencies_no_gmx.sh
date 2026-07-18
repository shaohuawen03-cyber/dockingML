#!/bin/bash
# ============================================================
# dockingML 依赖安装脚本（不包含 GROMACS）
# ============================================================
# 用途：为图形化界面 + 配体拓扑生成 + 分析功能准备环境
# ============================================================

set -e

echo "=============================================================="
echo "  dockingML 依赖安装（不安装 GROMACS）"
echo "=============================================================="

# 检查 conda/mamba
if ! command -v mamba &> /dev/null; then
    echo "❌ 未找到 mamba，请先安装 Miniconda/Mambaforge"
    exit 1
fi

# 创建环境（Python 3.10）
ENV_NAME="dockingml"
echo "📦 创建 conda 环境: $ENV_NAME (python=3.10)"

mamba create -n $ENV_NAME python=3.10 -y

echo "✅ 环境创建完成"
echo ""

# 激活环境
echo "🔄 激活环境: $ENV_NAME"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

echo "📥 安装核心依赖..."

# 基础科学计算 + GUI
mamba install -c conda-forge -y \
    numpy \
    scipy \
    pandas \
    matplotlib \
    seaborn \
    pyqt6 \
    pyyaml \
    tqdm \
    joblib

# 结构/轨迹分析
mamba install -c conda-forge -y \
    mdtraj \
    mdanalysis \
    parmed \
    rdkit

# 机器学习
mamba install -c conda-forge -y \
    scikit-learn \
    xgboost \
    lightgbm

# 配体拓扑生成（ACPYPE + OpenBabel）
echo "🧪 安装 ACPYPE（配体拓扑生成）..."
mamba install -c conda-forge -y acpype

# 可选：安装 dockingML 本身（开发模式）
echo "📦 安装 dockingML（开发模式）..."
pip install -e .

echo ""
echo "=============================================================="
echo "✅ 所有依赖安装完成！"
echo "=============================================================="
echo ""
echo "使用方法："
echo "  conda activate $ENV_NAME"
echo "  python src/main.py          # 启动图形界面"
echo ""
echo "配体拓扑生成示例："
echo "  python bin/generate_ligand_topology.py -i ligand.pdb --method acpype --resname LIG"
echo ""
echo "注意：GROMACS 需要单独安装（conda install -c conda-forge gromacs）"
echo "=============================================================="