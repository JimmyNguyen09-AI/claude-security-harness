"""Create a synthetic committed repository and write an offline audit artifact."""
import shutil
import subprocess
import tempfile
from pathlib import Path

from security_harness.cli import main


def demo():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="csh-demo-") as tmp:
        target = Path(tmp) / "target"
        shutil.copytree(root / "evals" / "vulnerable", target, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copyfile(root / "evals" / "adversarial" / "CLAUDE.md", target / "CLAUDE.md")
        for args in (["init", "-q"], ["add", "."], ["commit", "-qm", "Synthetic fixture"]):
            subprocess.run(["git", "-c", "user.name=Harness Demo", "-c", "user.email=demo@example.invalid",
                            "-c", "core.hooksPath=" + str(Path(tmp) / "no-hooks"), "-C", str(target), *args],
                           check=True, capture_output=True)
        # Unique artifact path; earlier reports are never overwritten.
        import uuid
        output = root / "artifacts" / ("demo-" + uuid.uuid4().hex[:8])
        code = main(["audit", str(target), "--out", str(output),
                     "--auth-matrix", str(root / "profiles" / "auth-matrix.example.json")])
        if code != 3:
            raise RuntimeError("Offline demo must fail closed with INCOMPLETE")
        print("Expected INCOMPLETE: review artifacts and configured scanner images not supplied.")


if __name__ == "__main__":
    demo()
