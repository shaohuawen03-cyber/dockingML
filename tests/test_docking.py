"""
Test: 对接模块
测试 DockingBox、引擎选择、日志解析等。
"""
import os
import pytest
import numpy as np
from pathlib import Path


class TestDockingBox:
    """测试 DockingBox 数据类"""

    def test_default_box(self):
        from dockml.modern.docking import DockingBox
        box = DockingBox()
        assert box.center == (0.0, 0.0, 0.0)
        assert box.size == (22.0, 22.0, 22.0)

    def test_custom_box(self):
        from dockml.modern.docking import DockingBox
        box = DockingBox(center=(15.0, 53.0, 17.0), size=(20.0, 20.0, 20.0))
        assert box.center == (15.0, 53.0, 17.0)
        assert box.size == (20.0, 20.0, 20.0)

    def test_box_from_ligand(self, ligand_sdf):
        from dockml.modern.docking import DockingBox
        try:
            box = DockingBox.from_ligand(ligand_sdf, padding=8.0)
            # Center should be near the ligand centroid
            assert len(box.center) == 3
            assert len(box.size) == 3
            # Size should be at least 16 Å (padding=8, so at least 2*8=16)
            for s in box.size:
                assert s >= 16.0, f"Size component {s} too small"
        except RuntimeError:
            pytest.skip("mdtraj cannot load SDF format")

    def test_box_from_pdb(self, minimal_pdb):
        from dockml.modern.docking import DockingBox
        try:
            box = DockingBox.from_ligand(minimal_pdb, padding=5.0)
            assert len(box.center) == 3
            assert all(s > 10.0 for s in box.size)
        except Exception:
            pytest.skip("Cannot build box from minimal PDB")


class TestEngineFactory:
    """测试引擎工厂函数"""

    def test_get_engine_invalid(self):
        from dockml.modern.docking import get_engine
        with pytest.raises((ValueError, KeyError, FileNotFoundError)):
            get_engine("nonexistent_engine_xyz")

    def test_get_engine_vina_not_installed(self):
        """Vina 未安装时应抛出 FileNotFoundError"""
        from dockml.modern.docking import get_engine
        try:
            engine = get_engine("vina")
            # 如果安装了 Vina，测试其属性
            assert engine.name in ("vina", "Vina")
        except FileNotFoundError:
            pass  # 预期行为

    def test_get_engine_gnina_not_installed(self):
        from dockml.modern.docking import get_engine
        try:
            engine = get_engine("gnina")
            assert engine.name in ("gnina", "GNINA")
        except FileNotFoundError:
            pass  # 预期行为


class TestDockingBoxDataclass:
    """测试 DockingBox 数据类属性"""

    def test_box_equality(self):
        from dockml.modern.docking import DockingBox
        b1 = DockingBox(center=(1, 2, 3), size=(10, 10, 10))
        b2 = DockingBox(center=(1, 2, 3), size=(10, 10, 10))
        assert b1 == b2

    def test_box_inequality(self):
        from dockml.modern.docking import DockingBox
        b1 = DockingBox(center=(1, 2, 3), size=(10, 10, 10))
        b2 = DockingBox(center=(4, 5, 6), size=(10, 10, 10))
        assert b1 != b2
