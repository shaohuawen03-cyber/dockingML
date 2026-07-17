#!/bin/bash
# =============================================================================
# Docker 快速启动脚本
# =============================================================================
# 用法:
#   bash scripts/docker_run.sh build       # 构建镜像
#   bash scripts/docker_run.sh shell       # 进入容器 shell
#   bash scripts/docker_run.sh test        # 运行测试
#   bash scripts/docker_run.sh gui         # 运行 GUI (需要 X11)
#   bash scripts/docker_run.sh pipeline    # 运行完整流程测试
# =============================================================================

set -e

CMD=${1:-shell}
IMAGE_NAME="dockingml"

case "$CMD" in
    build)
        echo "构建 Docker 镜像..."
        docker build -t ${IMAGE_NAME}:latest .
        echo "✓ 构建完成: ${IMAGE_NAME}:latest"
        ;;
    shell)
        echo "进入容器 shell..."
        docker run -it --rm \
            -v "$(pwd):/workspace" \
            -w /workspace \
            ${IMAGE_NAME}:latest \
            bash
        ;;
    test)
        echo "运行 pytest 测试..."
        docker run -it --rm \
            -v "$(pwd):/workspace" \
            -w /workspace \
            ${IMAGE_NAME}:latest \
            -c "pytest tests/ -v --tb=short"
        ;;
    gui)
        echo "启动 GUI (需要 X11 转发)..."
        xhost +local:docker 2>/dev/null || true
        docker run -it --rm \
            -v "$(pwd):/workspace" \
            -v /tmp/.X11-unix:/tmp/.X11-unix \
            -e DISPLAY="$DISPLAY" \
            -e QT_QPA_PLATFORM=xcb \
            --network host \
            -w /workspace \
            ${IMAGE_NAME}:latest \
            -c "python3 src/main.py"
        ;;
    pipeline)
        echo "运行完整流程测试..."
        docker run -it --rm \
            -v "$(pwd):/workspace" \
            -w /workspace \
            ${IMAGE_NAME}:latest \
            -c "python test_full_pipeline.py"
        ;;
    compose)
        echo "使用 docker-compose..."
        docker-compose run --rm dockingml bash
        ;;
    *)
        echo "用法: bash $0 {build|shell|test|gui|pipeline|compose}"
        echo ""
        echo "  build     构建 Docker 镜像"
        echo "  shell     进入容器交互式 shell"
        echo "  test      运行 pytest 测试套件"
        echo "  gui       启动 GROMACS GUI (需要 X11)"
        echo "  pipeline  运行完整流程测试"
        echo "  compose   使用 docker-compose 启动"
        exit 1
        ;;
esac
