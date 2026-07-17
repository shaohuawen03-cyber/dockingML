# =============================================================================
# dockingML v2.0 — Docker 镜像
# =============================================================================
# 构建:  docker build -t dockingml .
# 运行:  docker run -it --rm -v $(pwd):/workspace dockingml bash
# 或使用 docker-compose (见 docker-compose.yml)
# =============================================================================

# ---------- Stage 1: 基础镜像 (GROMACS + Open Babel + 系统依赖) ----------
FROM ubuntu:22.04 AS base

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# ---- pip 换源: 清华镜像 (国内加速) ----
# 如需其他镜像, 修改下方 PIP_INDEX_URL:
#   清华: https://pypi.tuna.tsinghua.edu.cn/simple
#   阿里: https://mirrors.aliyun.com/pypi/simple
#   腾讯: https://mirrors.cloud.tencent.com/pypi/simple
#   华为: https://repo.huaweicloud.com/repository/pypi/simple
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        gfortran \
        git \
        wget \
        curl \
        ca-certificates \
        # GROMACS 依赖
        libfftw3-dev \
        libgsl-dev \
        libhwloc-dev \
        # Open Babel
        openbabel \
        libopenbabel-dev \
        # Python
        python3 \
        python3-pip \
        python3-dev \
        python3-venv \
        # GROMACS 预编译包 (Ubuntu 官方)
        gromacs \
        # GUI 依赖 (headless 模式)
        libgl1-mesa-glx \
        libglib2.0-0 \
        libxkbcommon0 \
        libdbus-1-3 \
        libegl1 \
        libfontconfig1 \
        libxcb-cursor0 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-shape0 \
        libxcb-sync1 \
        libxcb-xfixes0 \
        libxcb-xinerama0 \
        libxcb-xkb1 \
        libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

# ---- Python 依赖 (使用国内镜像) ----
RUN python3 -m pip install --upgrade pip setuptools wheel

WORKDIR /app

# 先复制依赖文件, 利用 Docker 缓存层
COPY requirements.txt setup.py ./

# 安装基础依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装核心 Python 包
COPY . .
RUN pip install --no-cache-dir -e ".[dev]"

# ---- 验证安装 ----
RUN python3 -c "import dockml; print('dockml OK')" && \
    python3 -c "import automd; print('automd OK')" && \
    python3 -c "import mdanaly; print('mdanaly OK')" && \
    gmx --version || true && \
    obabel -V || true

# 默认工作目录
WORKDIR /workspace
VOLUME ["/workspace"]

# 默认入口: bash shell
ENTRYPOINT ["bash"]


# ---------- Stage 2: 完整版 (含深度学习可选依赖) ----------
FROM base AS full

RUN pip install --no-cache-dir -e ".[dl,openff]" || true

ENTRYPOINT ["bash"]
