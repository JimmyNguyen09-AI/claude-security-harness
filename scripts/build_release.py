"""Build optional Python helpers from a fresh staging tree, excluding stale output."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="security-harness-release-") as tmp:
    staging = Path(tmp) / "source"
    shutil.copytree(root, staging, ignore=shutil.ignore_patterns(
        ".venv*", "build", "dist", "artifacts", "__pycache__", ".pytest_cache", "*.egg-info", ".git"))
    subprocess.run([sys.executable, "-m", "build", "--outdir", str(root / "dist"), str(staging)], check=True)
