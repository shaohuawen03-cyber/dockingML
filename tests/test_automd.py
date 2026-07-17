"""
Test: AutoRunMD 模块
测试 MD 工作流类的方法存在性和参数处理。
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestAutoRunMDInit:
    """测试 AutoRunMD 初始化"""

    def test_init(self):
        from automd.autoRunMD_gmx import AutoRunMD
        app = AutoRunMD()
        assert app is not None
        assert app.PROJECT_ROOT is not None

    def test_project_root_exists(self):
        from automd.autoRunMD_gmx import AutoRunMD
        app = AutoRunMD()
        assert os.path.isdir(app.PROJECT_ROOT)


class TestAutoRunMDMethods:
    """测试方法存在性"""

    def test_generate_top_exists(self):
        from automd.autoRunMD_gmx import AutoRunMD
        app = AutoRunMD()
        assert hasattr(app, 'generate_top')
        assert callable(app.generate_top)

    def test_add_box_exists(self):
        from automd.autoRunMD_gmx import AutoRunMD
        app = AutoRunMD()
        assert hasattr(app, 'add_box')
        assert callable(app.add_box)

    def test_add_solvent_exists(self):
        from automd.autoRunMD_gmx import AutoRunMD
        app = AutoRunMD()
        assert hasattr(app, 'add_solvent')
        assert callable(app.add_solvent)

    def test_add_ions_exists(self):
        from automd.autoRunMD_gmx import AutoRunMD
        app = AutoRunMD()
        assert hasattr(app, 'add_ions')
        assert callable(app.add_ions)

    def test_minimize_exists(self):
        from automd.autoRunMD_gmx import AutoRunMD
        app = AutoRunMD()
        assert hasattr(app, 'minimize')
        assert callable(app.minimize)

    def test_md_exists(self):
        from automd.autoRunMD_gmx import AutoRunMD
        app = AutoRunMD()
        assert hasattr(app, 'md')
        assert callable(app.md)

    def test_modify_mdp_exists(self):
        from automd.autoRunMD_gmx import AutoRunMD
        app = AutoRunMD()
        assert hasattr(app, 'modify_mdp')
        assert callable(app.modify_mdp)


class TestAutoRunMDModifyMDP:
    """测试 MDP 文件修改功能"""

    def test_modify_mdp(self, tmp_path):
        from automd.autoRunMD_gmx import AutoRunMD
        app = AutoRunMD()

        # 创建测试 MDP 文件
        inmdp = tmp_path / "test_in.mdp"
        outmdp = tmp_path / "test_out.mdp"

        inmdp.write_text("""\
; Test MDP
integrator = md
dt         = 0.002
nsteps     = 50000
; Temperature coupling
Tcoupl     = V-rescale
ref_t      = 300
""")

        params = {
            "nsteps": ["100"],
            "dt": ["0.001"],
        }

        app.modify_mdp(str(inmdp), str(outmdp), params)

        content = outmdp.read_text()
        assert "100" in content
        assert "0.001" in content
        # 验证修改后的参数
        for line in content.splitlines():
            line_stripped = line.strip()
            if line_stripped.startswith("nsteps"):
                assert "100" in line
            if line_stripped.startswith("dt"):
                assert "0.001" in line


class TestAutoRunMDSubprocess:
    """测试 run_subprocess 错误处理"""

    def test_run_subprocess_failure(self):
        from automd.autoRunMD_gmx import AutoRunMD
        app = AutoRunMD()
        with pytest.raises(RuntimeError, match="GROMACS command failed"):
            app.run_suprocess("false")  # 'false' always returns non-zero

    def test_run_subprocess_success(self):
        from automd.autoRunMD_gmx import AutoRunMD
        app = AutoRunMD()
        result = app.run_suprocess("true")  # 'true' always returns 0
        assert result is app  # should return self for chaining
