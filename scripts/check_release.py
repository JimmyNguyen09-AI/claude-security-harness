"""Check tracked source and the native ZIP for accidental private content.

This is a small release-hygiene check, not a comprehensive secret scanner.
It reports filenames/rule names, never matching secret values.
"""
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "github-token": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})"),
    "anthropic-token": re.compile(r"sk-ant-[A-Za-z0-9_-]{30,}"),
    "openai-token": re.compile(r"sk-proj-[A-Za-z0-9_-]{30,}"),
    "aws-access-id": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "slack-token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    "private-key-block": re.compile(r"^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.M),
    "personal-windows-path": re.compile(r"[A-Za-z]:[/\\]Users[/\\][^\s/\\]+[/\\]"),
}
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", "build", "dist", "artifacts", "node_modules"}


def path_issues(name):
    path = PurePosixPath(name)
    problems = []
    if path.is_absolute() or ".." in path.parts or "\\" in name:
        problems.append("unsafe-path")
    if any(p in EXCLUDED_PARTS or p.startswith(".venv") or p.endswith(".egg-info") for p in path.parts):
        problems.append("local-generated-content")
    if path.name.startswith(".env") and path.name != ".env.example":
        problems.append("environment-file")
    if path.suffix.lower() in {".pem", ".key", ".p12", ".pfx", ".log"}:
        problems.append("credential-or-log-file")
    return problems


def content_issues(text):
    return [name for name, pattern in PATTERNS.items() if pattern.search(text)]


def inspect_zip(file):
    issues = []
    with zipfile.ZipFile(file) as archive:
        names = archive.namelist()
        for required in ("LICENSE", "README.md", "README.vi.md", "SECURITY.md", "THIRD_PARTY_NOTICES.md",
                         ".claude-plugin/plugin.json", "skills/campaign/scripts/campaign_state.py"):
            if required not in names:
                issues.append(f"archive missing {required}")
        if len(names) != len(set(names)):
            issues.append("archive duplicate entries")
        for name in names:
            issues.extend(f"archive {name}: {rule}" for rule in path_issues(name))
            try:
                text = archive.read(name).decode("utf-8")
            except UnicodeDecodeError:
                continue
            issues.extend(f"archive {name}: {rule}" for rule in content_issues(text))
    return issues


def main():
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    names = [p for p in raw.decode("utf-8").split("\0") if p]
    if not names:
        print("No tracked source files; stage or check out the project first.")
        return 1
    issues = []
    for name in names:
        issues.extend(f"source {name}: {rule}" for rule in path_issues(name))
        path = ROOT / name
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            issues.append(f"source {name}: symlink/outside-root")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        issues.extend(f"source {name}: {rule}" for rule in content_issues(text))
    manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    if manifest.get("license") != "MIT":
        issues.append("plugin license metadata mismatch")
    archive = ROOT / "dist" / f"security-harness-native-{manifest['version']}.zip"
    if not archive.is_file():
        issues.append("native archive missing: run scripts/package_plugin.py")
    else:
        issues.extend(inspect_zip(archive))
    if issues:
        print("\n".join(issues))
        return 1
    print(f"Checked {len(names)} tracked files and native ZIP: no configured release-hygiene patterns detected.")
    print("This does not replace a comprehensive secret scan or a license audit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
