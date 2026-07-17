"""
Test: 特征计算模块
测试 ResidueInteractionFeatures 和 OnionNetContacts (如 mdtraj 可用)。
"""
import pytest
import numpy as np
from pathlib import Path

try:
    import mdtraj
    HAVE_MDTRAJ = True
except ImportError:
    HAVE_MDTRAJ = False


@pytest.mark.skipif(not HAVE_MDTRAJ, reason="mdtraj not installed")
class TestResidueInteractionFeatures:
    """测试残基相互作用特征"""

    def test_import(self):
        from dockml.modern.features.contacts import ResidueInteractionFeatures
        assert ResidueInteractionFeatures is not None

    def test_from_pdb(self, complex_pdb):
        from dockml.modern.features.contacts import ResidueInteractionFeatures
        # 使用复合物 PDB，配体残基名为 "GIO"（10gs 中的配体）
        # 先尝试常见配体名
        for lig_name in ("GIO", "LIG", "MOL", "UNL"):
            try:
                rf = ResidueInteractionFeatures.from_pdb(
                    complex_pdb, ligand_resname=lig_name
                )
                assert rf is not None
                return
            except (ValueError, KeyError):
                continue
        pytest.skip("Could not find ligand residue in complex PDB")


@pytest.mark.skipif(not HAVE_MDTRAJ, reason="mdtraj not installed")
class TestOnionNetContacts:
    """测试 OnionNet 多层接触特征"""

    def test_import(self):
        from dockml.modern.features.contacts import OnionNetContacts
        assert OnionNetContacts is not None


@pytest.mark.skipif(not HAVE_MDTRAJ, reason="mdtraj not installed")
class TestInteractionFingerprints:
    """测试蛋白质-配体相互作用指纹"""

    def test_import(self):
        from dockml.modern.features.interactions import InteractionFingerprints
        assert InteractionFingerprints is not None

    def test_init(self, complex_pdb):
        from dockml.modern.features.interactions import InteractionFingerprints
        for lig_name in ("GIO", "LIG", "MOL", "UNL"):
            try:
                ifp = InteractionFingerprints(complex_pdb, ligand_resname=lig_name)
                assert ifp is not None
                return
            except (ValueError, KeyError):
                continue
        pytest.skip("Could not find ligand residue in complex PDB")


class TestSafeElement:
    """测试元素符号清理函数"""

    def test_safe_element_normal(self):
        from dockml.modern.features.contacts import _safe_element
        assert _safe_element("C") == "C"
        assert _safe_element("CA") == "Ca"
        assert _safe_element("cl") == "Cl"
        assert _safe_element("FE") == "Fe"

    def test_safe_element_edge_cases(self):
        from dockml.modern.features.contacts import _safe_element
        assert _safe_element("") == "Du"
        assert _safe_element("  ") == "Du"

    def test_safe_element_single_char(self):
        from dockml.modern.features.contacts import _safe_element
        assert _safe_element("N") == "N"
        assert _safe_element("O") == "O"
        assert _safe_element("H") == "H"
