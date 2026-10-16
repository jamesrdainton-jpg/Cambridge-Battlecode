"""Helpers shared by the tools: the project root, the cambc executable, and the git commit behind a run."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def find_cambc() -> str:
    """The venv's cambc (Windows or Mac/Linux layout), else one on PATH."""
    for path in (ROOT / ".venv" / "Scripts" / "cambc.exe", ROOT / ".venv" / "bin" / "cambc"):
        if path.exists():
            return str(path)
    found = shutil.which("cambc")
    if not found:
        raise SystemExit("cambc not found: create .venv and install requirements-dev.txt")
    return found


def git_commit(*paths: str) -> str:
    """Short HEAD commit, plus "+dirty" when any of `paths` has uncommitted changes ("" outside git)."""
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=ROOT, check=False, capture_output=True, text=True).stdout.strip()
    rev = git("rev-parse", "--short", "HEAD")
    if rev and paths and git("status", "--porcelain", "--", *paths):
        rev += "+dirty"
    return rev
