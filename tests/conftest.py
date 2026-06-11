"""Fixtures for the CLI journey tests.

These tests live next to the CLI so the OSS sync carries them into the
public repo. They must import cleanly from both layouts:

- monorepo:  gcontext/ is here, core/ one level up at the repo root
- public repo (post-sync): core/ and gcontext/ sit side by side here
"""
import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
PKG_ROOT = TESTS_DIR.parent

sys.path.insert(0, str(PKG_ROOT))
if not (PKG_ROOT / "core").is_dir():
    sys.path.insert(0, str(PKG_ROOT.parent))

from gcontext import cli  # noqa: E402


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """Temp CWD with the CLI's import-time path globals rebound to it."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "MODULES_DIR", tmp_path / "modules-repo")
    monkeypatch.setattr(cli, "CONTEXT_DIR", tmp_path / "context")
    return tmp_path


@pytest.fixture
def run(workspace, monkeypatch, capsys):
    """Invoke `gcontext <args>` through main(); returns (exit_code, output)."""

    def _run(*argv):
        monkeypatch.setattr(sys, "argv", ["gcontext", *argv])
        try:
            cli.main()
            code = 0
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        captured = capsys.readouterr()
        return code, captured.out + captured.err

    return _run
