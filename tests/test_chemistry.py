"""
Test: 化学常量和 PLIF 定义
验证 VDW 半径、电负性等化学常量数据完整性。
"""
import pytest


class TestChemistryConstants:
    """测试化学常量"""

    def test_vdw_radii_keys(self):
        from dockml.modern.features.chemistry import VDW_RADII
        # 必须包含常见元素
        for elem in ("H", "C", "N", "O", "S", "P", "F", "Cl", "Br"):
            assert elem in VDW_RADII, f"Missing VDW radius for {elem}"

    def test_vdw_radii_values(self):
        from dockml.modern.features.chemistry import VDW_RADII
        # 所有值必须为正且合理 (< 3.0 Å)
        for elem, r in VDW_RADII.items():
            assert 0.5 < r < 3.0, f"VDW radius for {elem} out of range: {r}"

    def test_electronegativity_keys(self):
        from dockml.modern.features.chemistry import ELEMENT_NEGATIVITY
        for elem in ("H", "C", "N", "O", "F", "S", "P"):
            assert elem in ELEMENT_NEGATIVITY

    def test_electronegativity_values(self):
        from dockml.modern.features.chemistry import ELEMENT_NEGATIVITY
        # Pauling scale: 0.5 to 4.0
        for elem, en in ELEMENT_NEGATIVITY.items():
            assert 0.5 < en < 4.5, f"Electronegativity for {elem} out of range: {en}"

    def test_fluorine_most_electronegative(self):
        from dockml.modern.features.chemistry import ELEMENT_NEGATIVITY
        max_elem = max(ELEMENT_NEGATIVITY, key=ELEMENT_NEGATIVITY.get)
        assert max_elem == "F", "Fluorine should be most electronegative"

    def test_cutoff_values(self):
        from dockml.modern.features.chemistry import (
            CUTOFF_CONTACT, CUTOFF_HBOND, CUTOFF_HYDROPHOBIC,
            CUTOFF_PISTACK, CUTOFF_SALTBRIDGE, CUTOFF_PICATION,
            CUTOFF_HALOGEN,
        )
        # 所有距离截断值必须为正且合理
        for name, val in [
            ("CONTACT", CUTOFF_CONTACT),
            ("HBOND", CUTOFF_HBOND),
            ("HYDROPHOBIC", CUTOFF_HYDROPHOBIC),
            ("PISTACK", CUTOFF_PISTACK),
            ("SALTBRIDGE", CUTOFF_SALTBRIDGE),
            ("PICLICATION", CUTOFF_PICATION),
            ("HALOGEN", CUTOFF_HALOGEN),
        ]:
            assert 1.0 < val < 10.0, f"Cutoff {name}={val} out of range"

    def test_residue_sets(self):
        from dockml.modern.features.chemistry import (
            AROMATIC_RES, CATION_RES, ANION_RES,
        )
        # 芳香族残基
        assert "PHE" in AROMATIC_RES
        assert "TYR" in AROMATIC_RES
        assert "TRP" in AROMATIC_RES
        assert "HIS" in AROMATIC_RES
        # 阳离子残基
        assert "LYS" in CATION_RES
        assert "ARG" in CATION_RES
        # 阴离子残基
        assert "ASP" in ANION_RES
        assert "GLU" in ANION_RES

    def test_hbond_elements(self):
        from dockml.modern.features.chemistry import HBOND_DONOR_HEAVY, HBOND_ACCEPTOR
        assert "N" in HBOND_DONOR_HEAVY
        assert "O" in HBOND_DONOR_HEAVY
        assert "N" in HBOND_ACCEPTOR
        assert "O" in HBOND_ACCEPTOR
        assert "F" in HBOND_ACCEPTOR

    def test_angle_cutoff(self):
        from dockml.modern.features.chemistry import ANGLE_HBOND_MIN
        assert 90.0 < ANGLE_HBOND_MIN < 180.0
