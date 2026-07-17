"""
Shared test fixtures for dockingML test suite.
"""
import os
import sys
import shutil
import tempfile
from pathlib import Path

import pytest
import numpy as np

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# ---------- Path constants ----------
EXAMPLE_DIR = PROJECT_ROOT / "automd" / "examples" / "10gs"
COMPLEX_PDB = EXAMPLE_DIR / "10gs_complex.pdb"
PROTEIN_PDB = EXAMPLE_DIR / "10gs_protein.pdb"
LIGAND_SDF = EXAMPLE_DIR / "10gs_ligand.sdf"
LIGAND_MOL2 = EXAMPLE_DIR / "10gs_ligand.mol2"
MDP_DIR = PROJECT_ROOT / "automd" / "data"


@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def example_dir():
    return EXAMPLE_DIR


@pytest.fixture
def complex_pdb():
    """Path to the 10gs protein-ligand complex PDB."""
    assert COMPLEX_PDB.exists(), f"Missing test fixture: {COMPLEX_PDB}"
    return str(COMPLEX_PDB)


@pytest.fixture
def protein_pdb():
    """Path to the 10gs receptor PDB."""
    assert PROTEIN_PDB.exists(), f"Missing test fixture: {PROTEIN_PDB}"
    return str(PROTEIN_PDB)


@pytest.fixture
def ligand_sdf():
    """Path to the 10gs ligand SDF."""
    assert LIGAND_SDF.exists(), f"Missing test fixture: {LIGAND_SDF}"
    return str(LIGAND_SDF)


@pytest.fixture
def tmp_dir(tmp_path):
    """Temporary directory for test outputs."""
    return tmp_path


@pytest.fixture
def sample_features():
    """Generate sample feature matrix for ML tests."""
    rng = np.random.RandomState(42)
    n_samples = 200
    n_features = 20
    X = rng.randn(n_samples, n_features)
    # Binary labels with some signal
    y = (X[:, 0] + X[:, 1] * 0.5 + rng.randn(n_samples) * 0.3 > 0).astype(int)
    return X, y


@pytest.fixture
def sample_regression_data():
    """Generate sample regression data for ML tests."""
    rng = np.random.RandomState(42)
    n_samples = 200
    n_features = 20
    X = rng.randn(n_samples, n_features)
    y = X[:, 0] * 2.0 + X[:, 1] * 1.5 + rng.randn(n_samples) * 0.5
    return X, y


@pytest.fixture
def minimal_pdb(tmp_path):
    """Create a minimal PDB file for testing."""
    pdb_content = """\
HEADER    TEST PROTEIN
ATOM      1  N   ALA A   1       0.000   0.000   0.000  1.00  0.00           N
ATOM      2  CA  ALA A   1       1.458   0.000   0.000  1.00  0.00           C
ATOM      3  C   ALA A   1       2.009   1.420   0.000  1.00  0.00           C
ATOM      4  O   ALA A   1       1.250   2.400   0.000  1.00  0.00           O
ATOM      5  CB  ALA A   1       1.960  -0.600  -1.260  1.00  0.00           C
ATOM      6  N   GLY A   2       3.320   1.420   0.000  1.00  0.00           N
ATOM      7  CA  GLY A   2       4.000   2.700   0.000  1.00  0.00           C
ATOM      8  C   GLY A   2       5.500   2.700   0.000  1.00  0.00           C
ATOM      9  O   GLY A   2       6.200   1.700   0.000  1.00  0.00           O
ATOM     10  C1  LIG B   1      10.000  10.000  10.000  1.00  0.00           C
ATOM     11  C2  LIG B   1      11.500  10.000  10.000  1.00  0.00           C
ATOM     12  O1  LIG B   1      12.000  11.100  10.000  1.00  0.00           O
ATOM     13  N1  LIG B   1      10.000  11.200  10.000  1.00  0.00           N
END
"""
    pdb_file = tmp_path / "minimal.pdb"
    pdb_file.write_text(pdb_content)
    return str(pdb_file)


def has_gromacs():
    """Check if GROMACS is installed."""
    return shutil.which("gmx") is not None


def has_obabel():
    """Check if Open Babel is installed."""
    return shutil.which("obabel") is not None
