"""
Test: 完整流程集成测试
使用 mock 模拟 GROMACS 命令，测试端到端工作流。
"""
import os
import pytest
import shutil
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


class TestExampleFiles:
    """测试示例文件完整性"""

    def test_complex_pdb_exists(self):
        f = PROJECT_ROOT / "automd" / "examples" / "10gs" / "10gs_complex.pdb"
        assert f.exists(), f"Missing: {f}"

    def test_protein_pdb_exists(self):
        f = PROJECT_ROOT / "automd" / "examples" / "10gs" / "10gs_protein.pdb"
        assert f.exists(), f"Missing: {f}"

    def test_ligand_sdf_exists(self):
        f = PROJECT_ROOT / "automd" / "examples" / "10gs" / "10gs_ligand.sdf"
        assert f.exists(), f"Missing: {f}"

    def test_ligand_mol2_exists(self):
        f = PROJECT_ROOT / "automd" / "examples" / "10gs" / "10gs_ligand.mol2"
        assert f.exists(), f"Missing: {f}"

    def test_complex_pdb_not_empty(self):
        f = PROJECT_ROOT / "automd" / "examples" / "10gs" / "10gs_complex.pdb"
        assert f.stat().st_size > 1000, "Complex PDB suspiciously small"

    def test_complex_pdb_has_atoms(self):
        f = PROJECT_ROOT / "automd" / "examples" / "10gs" / "10gs_complex.pdb"
        content = f.read_text()
        atom_lines = [l for l in content.splitlines() if l.startswith("ATOM")]
        assert len(atom_lines) > 100, "Complex PDB has too few atoms"


class TestDataFiles:
    """测试数据文件完整性"""

    def test_spc903_gro_exists(self):
        f = PROJECT_ROOT / "automd" / "data" / "spc903.gro"
        assert f.exists(), f"Missing: {f}"

    def test_em_sol_mdp_exists(self):
        f = PROJECT_ROOT / "automd" / "data" / "em_sol.mdp"
        assert f.exists(), f"Missing: {f}"

    def test_amino_acids_lib_exists(self):
        f = PROJECT_ROOT / "automd" / "data" / "amino_acids.lib"
        assert f.exists(), f"Missing: {f}"


class TestDockmlModulePresence:
    """测试 dockml 对接模块存在性（不删除）"""

    def test_dockml_dir_exists(self):
        d = PROJECT_ROOT / "dockml"
        assert d.exists() and d.is_dir()

    def test_dock_py_exists(self):
        f = PROJECT_ROOT / "dockml" / "dock.py"
        assert f.exists(), "dockml/dock.py should not be deleted"

    def test_modern_docking_exists(self):
        f = PROJECT_ROOT / "dockml" / "modern" / "docking.py"
        assert f.exists()

    def test_modern_pipeline_exists(self):
        f = PROJECT_ROOT / "dockml" / "modern" / "pipeline.py"
        assert f.exists()


class TestEndToEndMLPipeline:
    """端到端 ML 流程测试（不需要 GROMACS）"""

    def test_feature_generation_and_training(self, sample_features, tmp_path):
        """模拟: 生成特征 → 训练 → 预测 → 保存/加载"""
        from dockml.modern.scoring.classical import ClassicalRescorer

        X, y = sample_features

        # 1. 训练模型
        model = ClassicalRescorer(model="rf", task="classify", n_estimators=50)
        model.fit(X, y)

        # 2. 预测
        proba = model.predict_proba(X[:10])
        assert len(proba) == 10

        # 3. 交叉验证
        cv = model.cv_evaluate(X, y, n_fold=3)
        assert "test_roc_auc" in cv
        assert cv["test_roc_auc"] > 0.5

        # 4. 保存/加载
        model_path = str(tmp_path / "model.pkl")
        model.save(model_path)
        loaded = ClassicalRescorer.load(model_path)
        proba2 = loaded.predict_proba(X[:10])
        np.testing.assert_allclose(proba, proba2)

    def test_multi_model_consensus(self, sample_features):
        """测试多模型共识评分"""
        from dockml.modern.scoring.classical import ClassicalRescorer, ConsensusRescorer

        X, y = sample_features

        models = []
        for name in ("rf", "lr"):
            kwargs = {"n_estimators": 50} if name == "rf" else {"scale": True}
            m = ClassicalRescorer(model=name, task="classify", **kwargs)
            m.fit(X, y)
            models.append(m)

        cons = ConsensusRescorer()
        for m in models:
            cons.add(m, weight=1.0)

        scores = cons.predict(X)
        assert scores.shape == (len(X),)
        ranks = cons.rank_average(X)
        assert ranks.shape == (len(X),)


@pytest.mark.gromacs
class TestGROMACSIntegration:
    """需要 GROMACS 安装的集成测试"""

    @pytest.fixture(autouse=True)
    def require_gromacs(self):
        if not shutil.which("gmx"):
            pytest.skip("GROMACS (gmx) not installed")

    def test_gmx_version(self):
        import subprocess
        result = subprocess.run(["gmx", "--version"],
                                capture_output=True, text=True, timeout=10)
        assert result.returncode == 0

    def test_pdb2gmx_on_example(self, protein_pdb, tmp_path):
        """测试 pdb2gmx 命令"""
        import subprocess
        outgro = str(tmp_path / "out.gro")
        topol = str(tmp_path / "topol.top")
        result = subprocess.run(
            ["gmx", "pdb2gmx", "-f", protein_pdb, "-o", outgro,
             "-p", topol, "-ff", "amber99sb-ildn", "-water", "tip3p", "-ignh"],
            capture_output=True, text=True, timeout=120
        )
        assert result.returncode == 0, f"pdb2gmx failed: {result.stderr}"
        assert os.path.exists(outgro)
        assert os.path.exists(topol)
