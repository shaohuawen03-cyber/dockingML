"""
Test: 模块导入测试
验证所有核心模块可以正确导入。
"""
import pytest


class TestCoreImports:
    """测试核心模块导入"""

    def test_import_dockml(self):
        import dockml
        assert dockml is not None

    def test_import_automd(self):
        import automd
        assert automd is not None

    def test_import_mdanaly(self):
        import mdanaly
        assert mdanaly is not None


class TestDockmlImports:
    """测试 dockml 子模块导入"""

    def test_import_features(self):
        from dockml import features
        assert features is not None

    def test_import_pdbio(self):
        from dockml import pdbIO
        assert pdbIO is not None

    def test_import_dock(self):
        from dockml import dock
        assert dock is not None

    def test_import_index(self):
        from dockml import index
        assert index is not None

    def test_import_convert(self):
        from dockml import convert
        assert convert is not None


class TestModernImports:
    """测试 v2 modern 子模块导入"""

    def test_import_modern_docking(self):
        from dockml.modern import docking
        assert docking is not None

    def test_import_modern_features(self):
        from dockml.modern import features
        assert features is not None

    def test_import_modern_chemistry(self):
        from dockml.modern.features import chemistry
        assert chemistry is not None

    def test_import_modern_contacts(self):
        from dockml.modern.features import contacts
        assert contacts is not None

    def test_import_modern_interactions(self):
        from dockml.modern.features import interactions
        assert interactions is not None

    def test_import_modern_scoring(self):
        from dockml.modern import scoring
        assert scoring is not None

    def test_import_classical_scoring(self):
        from dockml.modern.scoring import classical
        assert classical is not None

    def test_import_modern_pipeline(self):
        from dockml.modern import pipeline
        assert pipeline is not None


class TestAutoMDImports:
    """测试 automd 子模块导入"""

    def test_import_autorun(self):
        from automd.autoRunMD_gmx import AutoRunMD
        assert AutoRunMD is not None

    def test_import_mdrun(self):
        from automd import mdrun
        assert mdrun is not None

    def test_import_topology(self):
        from automd import topology
        assert topology is not None


class TestMDAnalyImports:
    """测试 mdanaly 子模块导入"""

    def test_import_cmap(self):
        from mdanaly import cmap
        assert cmap is not None

    def test_import_pca(self):
        from mdanaly import pca
        assert pca is not None

    def test_import_dynamics(self):
        from mdanaly import dynamics
        assert dynamics is not None

    def test_import_plot(self):
        from mdanaly import plot
        assert plot is not None
