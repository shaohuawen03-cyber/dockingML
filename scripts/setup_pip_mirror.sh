#!/bin/bash
# =============================================================================
# pip 换源脚本 — 国内镜像加速
# =============================================================================
# 用法:
#   bash scripts/setup_pip_mirror.sh           # 默认使用清华镜像
#   bash scripts/setup_pip_mirror.sh aliyun    # 使用阿里云镜像
#   bash scripts/setup_pip_mirror.sh tencent   # 使用腾讯云镜像
#   bash scripts/setup_pip_mirror.sh huawei    # 使用华为云镜像
#   bash scripts/setup_pip_mirror.sh douban    # 使用豆瓣镜像
# =============================================================================

set -e

MIRROR=${1:-tsinghua}

case "$MIRROR" in
    tsinghua|thu|清华)
        URL="https://pypi.tuna.tsinghua.edu.cn/simple"
        HOST="pypi.tuna.tsinghua.edu.cn"
        NAME="清华大学"
        ;;
    aliyun|ali|阿里)
        URL="https://mirrors.aliyun.com/pypi/simple"
        HOST="mirrors.aliyun.com"
        NAME="阿里云"
        ;;
    tencent|tx|腾讯)
        URL="https://mirrors.cloud.tencent.com/pypi/simple"
        HOST="mirrors.cloud.tencent.com"
        NAME="腾讯云"
        ;;
    huawei|hw|华为)
        URL="https://repo.huaweicloud.com/repository/pypi/simple"
        HOST="repo.huaweicloud.com"
        NAME="华为云"
        ;;
    douban|db|豆瓣)
        URL="https://pypi.doubanio.com/simple"
        HOST="pypi.doubanio.com"
        NAME="豆瓣"
        ;;
    *)
        echo "未知镜像: $MIRROR"
        echo "可选: tsinghua (默认), aliyun, tencent, huawei, douban"
        exit 1
        ;;
esac

echo "============================================"
echo " 配置 pip 镜像源: $NAME"
echo " URL: $URL"
echo "============================================"

# 创建 pip 配置目录
mkdir -p ~/.config/pip

# 写入配置文件
cat > ~/.config/pip/pip.conf << EOF
[global]
index-url = $URL
trusted-host = $HOST
timeout = 120

[install]
trusted-host = $HOST
EOF

echo ""
echo "✓ 已配置 pip 镜像源: $NAME"
echo "  配置文件: ~/.config/pip/pip.conf"
echo ""
echo "验证配置:"
pip config list 2>/dev/null || echo "  (pip config 命令不可用，但配置文件已写入)"
echo ""
echo "测试安装速度:"
echo "  pip install numpy  # 应该会从 $NAME 下载"
echo ""
echo "如需恢复默认源:"
echo "  rm ~/.config/pip/pip.conf"
