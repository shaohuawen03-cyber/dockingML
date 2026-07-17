"""
Test: MDP 文件完整性
验证所有 MDP 参数文件存在且格式正确。
"""
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MDP_DIRS = {
    "legacy": PROJECT_ROOT / "automd" / "data",
    "modern": PROJECT_ROOT / "automd" / "data" / "modern",
    "production": PROJECT_ROOT / "automd" / "data" / "production",
}


class TestMDPFilesExist:
    """测试 MDP 文件是否存在"""

    def test_modern_em_mdp(self):
        f = MDP_DIRS["modern"] / "em.mdp"
        assert f.exists(), f"Missing: {f}"

    def test_modern_nvt_eq_mdp(self):
        f = MDP_DIRS["modern"] / "nvt_eq.mdp"
        assert f.exists(), f"Missing: {f}"

    def test_modern_npt_eq_mdp(self):
        f = MDP_DIRS["modern"] / "npt_eq.mdp"
        assert f.exists(), f"Missing: {f}"

    def test_modern_npt_prod_mdp(self):
        f = MDP_DIRS["modern"] / "npt_prod.mdp"
        assert f.exists(), f"Missing: {f}"


class TestMDPContent:
    """测试 MDP 文件内容"""

    @pytest.fixture(params=["em", "nvt_eq", "npt_eq", "npt_prod"])
    def modern_mdp(self, request):
        path = MDP_DIRS["modern"] / f"{request.param}.mdp"
        if not path.exists():
            pytest.skip(f"MDP file not found: {path}")
        return path.read_text()

    def test_mdp_has_integrator(self, modern_mdp):
        # 每个 MDP 必须定义 integrator
        assert "integrator" in modern_mdp

    def test_mdp_no_berendsen_pressure_in_production(self):
        """生产 MDP 不应使用 Berendsen 压力耦合"""
        prod = MDP_DIRS["modern"] / "npt_prod.mdp"
        if not prod.exists():
            pytest.skip("Production MDP not found")
        content = prod.read_text().lower()
        # Berendsen 只适用于平衡，不应用于生产
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith(";") or stripped.startswith("#"):
                continue
            if "pcoupl" in stripped and "berendsen" in stripped:
                pytest.fail("Production MDP uses Berendsen pressure coupling")

    def test_modern_em_uses_steep(self):
        """EM 应该使用 steep 或 cg 积分器"""
        f = MDP_DIRS["modern"] / "em.mdp"
        if not f.exists():
            pytest.skip("EM MDP not found")
        content = f.read_text()
        assert "steep" in content or "cg" in content

    def test_mdp_has_constraints(self):
        """NVT/NPT MDP 应该有约束"""
        for name in ("nvt_eq", "npt_eq", "npt_prod"):
            f = MDP_DIRS["modern"] / f"{name}.mdp"
            if f.exists():
                content = f.read_text()
                assert "constraints" in content, f"{name}.mdp missing constraints"

    def test_mdp_has_cutoff_scheme(self):
        """现代 MDP 应使用 Verlet cutoff"""
        for name in ("em", "nvt_eq", "npt_eq", "npt_prod"):
            f = MDP_DIRS["modern"] / f"{name}.mdp"
            if f.exists():
                content = f.read_text()
                assert "cutoff-scheme" in content or "Verlet" in content, \
                    f"{name}.dp missing cutoff scheme"
