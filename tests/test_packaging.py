"""Packaging smoke test: build the wheel, install it clean, run the CLI.

The journey tests import the code in place, so they can never catch a
broken wheel (missing package data, bad packages list, broken entry
point). This module builds the real artifact and exercises it:

1. Assemble the publishable layout (in the monorepo this means running
   scripts/publish_oss.py into a temp dir; in the public repo the layout
   already exists).
2. `uv build` a wheel there.
3. Install the wheel into a fresh venv.
4. Run the installed `gcontext` binary and assert the bundled package
   data (seed module, secrets.md, core templates) actually shipped.

Requires `uv` on PATH; skipped otherwise.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
PKG_ROOT = TESTS_DIR.parent
IS_PUBLIC_LAYOUT = (PKG_ROOT / "core").is_dir()
REPO_ROOT = PKG_ROOT if IS_PUBLIC_LAYOUT else PKG_ROOT.parent

UV = shutil.which("uv")

pytestmark = pytest.mark.skipif(UV is None, reason="uv not on PATH")


def _run(cmd, cwd=None, check=True):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise AssertionError(
            f"{' '.join(str(c) for c in cmd)} failed ({result.returncode}):\n"
            f"{result.stdout}\n{result.stderr}"
        )
    return result


@pytest.fixture(scope="session")
def gcontext_bin(tmp_path_factory):
    """Build the wheel from the publishable layout and install it clean."""
    base = tmp_path_factory.mktemp("packaging")

    if IS_PUBLIC_LAYOUT:
        build_dir = REPO_ROOT
    else:
        build_dir = base / "synced"
        build_dir.mkdir()
        _run(
            [sys.executable, str(REPO_ROOT / "scripts" / "publish_oss.py"), str(build_dir)]
        )

    dist = base / "dist"
    _run([UV, "build", "--wheel", "--out-dir", str(dist)], cwd=build_dir)
    wheels = list(dist.glob("gcontext_ai-*.whl"))
    assert len(wheels) == 1, f"expected one wheel, got {wheels}"

    venv = base / "venv"
    _run([UV, "venv", str(venv)])
    bin_dir = venv / ("Scripts" if os.name == "nt" else "bin")
    _run([UV, "pip", "install", "--python", str(bin_dir / "python"), str(wheels[0])])

    gcontext = bin_dir / ("gcontext.exe" if os.name == "nt" else "gcontext")
    assert gcontext.is_file(), "wheel did not install the gcontext entry point"
    return gcontext


def test_installed_cli_reports_version(gcontext_bin):
    result = _run([gcontext_bin, "--version"])
    assert result.stdout.startswith("gcontext ")


def test_installed_init_ships_package_data(gcontext_bin, tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    _run([gcontext_bin, "init"], cwd=project)

    # Seed module comes from gcontext/data/seed package data
    seed = project / "modules-repo" / "seed"
    for fname in ["module.yaml", "llms.txt", "info.md"]:
        assert (seed / fname).is_file(), f"seed module missing {fname}"

    # secrets.md ships from gcontext/data, the others from core/templates
    for fname in [
        "llms.txt",
        "system.md",
        "structure.md",
        "principles.md",
        "module_features.md",
        "secrets.md",
    ]:
        assert (project / "context" / fname).is_file(), f"context/ missing {fname}"

    assert (project / "AGENTS.md").is_file()
    assert (project / "CLAUDE.md").is_file()


def test_installed_journey_smoke(gcontext_bin, tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    _run([gcontext_bin, "init"], cwd=project)
    _run([gcontext_bin, "new", "integration", "stripe", "Stripe API"], cwd=project)
    _run([gcontext_bin, "load", "stripe"], cwd=project)

    assert (project / "context" / "stripe").is_symlink()
    assert "Stripe API" in (project / "context" / "llms.txt").read_text()

    result = _run([gcontext_bin, "validate"], cwd=project)
    assert "stripe  PASS" in result.stdout

    _run([gcontext_bin, "unload", "stripe"], cwd=project)
    assert not (project / "context" / "stripe").exists()
