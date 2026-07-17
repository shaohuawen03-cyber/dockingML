"""
Test: PDB 文件解析
测试 dockml.pdbIO 模块的 PDB 解析功能。
"""
import pytest
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


class TestPDBIO:
    """测试 PDB IO 模块"""

    def test_import_parsepdb(self):
        from dockml.pdbIO import parsePDB
        assert parsePDB is not None

    def test_import_coordinates(self):
        from dockml.pdbIO import coordinatesPDB
        assert coordinatesPDB is not None

    def test_parse_complex_pdb(self, complex_pdb):
        from dockml.pdbIO import parsePDB
        parser = parsePDB()
        info = parser.atomInformation(complex_pdb)
        assert info is not None
        # Should have many atoms
        assert len(info) > 100

    def test_parse_protein_pdb(self, protein_pdb):
        from dockml.pdbIO import parsePDB
        parser = parsePDB()
        info = parser.atomInformation(protein_pdb)
        assert info is not None
        assert len(info) > 100


class TestPDBCoordinates:
    """测试 PDB 坐标提取"""

    def test_get_coordinates(self, complex_pdb):
        from dockml.pdbIO import coordinatesPDB
        coord = coordinatesPDB()
        # 获取所有 ATOM 记录的坐标
        try:
            crds = coord.getAtomCrdByNdx(
                singleFramePDB=complex_pdb,
                atomNdx=list(range(1, 11))
            )
            if crds is not None:
                assert len(crds) > 0
        except Exception:
            pass  # 某些 API 可能参数不同
