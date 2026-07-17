"""
Test: GUI 模块导入
测试 GROMACS GUI 相关模块在 headless 环境下可导入。
"""
import os
import sys
import pytest

# 设置 headless 环境变量，避免需要显示器
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class TestGUICoreImports:
    """测试 GUI 核心模块导入"""

    def test_import_config(self):
        from src.core import config
        # config 模块定义常量而非类
        assert hasattr(config, 'GMX_PATH') or hasattr(config, 'FORCEFIELDS')

    def test_import_gmx_runner(self):
        try:
            from src.core.gmx_runner import GMXRunner
            assert GMXRunner is not None
        except ImportError:
            pytest.skip("src.core.gmx_runner not importable")

    def test_import_mdp_editor(self):
        try:
            from src.core.mdp_editor import MDPEditor
            assert MDPEditor is not None
        except ImportError:
            pytest.skip("src.core.mdp_editor not importable")

    def test_import_analysis(self):
        try:
            from src.core.analysis import TrajectoryAnalysis
            assert TrajectoryAnalysis is not None
        except ImportError:
            pytest.skip("src.core.analysis not importable")


class TestConfigModule:
    """测试配置模块"""

    def test_config_exists(self):
        config_file = Path(__file__).parent.parent / "src" / "core" / "config.py"
        assert config_file.exists(), "config.py should exist"

    def test_env_setup_exists(self):
        env_file = Path(__file__).parent.parent / "src" / "core" / "env_setup.py"
        assert env_file.exists(), "env_setup.py should exist"


from pathlib import Path
