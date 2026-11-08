"""Read-only plugin layout checks; no network, target execution or dependencies."""
import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

EXPECTED = {"start", "doctor", "review", "authz", "verify", "fix", "campaign",
            "test", "threat-model", "agent-security", "resume"}
ROLES = {"security-architect", "security-reviewer", "security-verifier",
         "security-tester", "security-fixer"}


def diagnose(root):
    root = Path(root).resolve()
    errors = []
    warnings = []

    def safe(path):
        resolved = path.resolve()
        if not resolved.is_relative_to(root):
            raise ValueError("path escapes plugin root")
        return resolved

    def read(path):
        return safe(path).read_text(encoding="utf-8")

    def document(path):
        try:
            value = json.loads(read(path))
            if not isinstance(value, dict):
                raise ValueError("expected JSON object")
            return value
        except (OSError, ValueError, RuntimeError):
            errors.append(f"Invalid or missing JSON: {path.relative_to(root).as_posix()}")
            return {}

    manifest = document(root / ".claude-plugin/plugin.json")
    if manifest.get("name") != "security-harness":
        errors.append("Plugin name must be security-harness")
    version = manifest.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append("Plugin version must be a release version: major.minor.patch")

    marketplace_path = root / ".claude-plugin/marketplace.json"
    if marketplace_path.exists():
        marketplace = document(marketplace_path)
        if marketplace.get("name") != "claude-security-harness":
            errors.append("Marketplace name must be claude-security-harness")
        entries = marketplace.get("plugins")
        if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
            errors.append("Marketplace must list exactly this plugin")
        elif entries[0].get("name") != manifest.get("name") or entries[0].get("source") != "./":
            errors.append("Marketplace entry must reference security-harness at ./")
    else:
        warnings.append("No marketplace manifest; normal for a standalone native ZIP")

    for directory, names in (("skills", EXPECTED), ("agents", ROLES)):
        for name in sorted(names):
            path = root / directory / name / "SKILL.md" if directory == "skills" else root / directory / f"{name}.md"
            label = path.relative_to(root).as_posix()
            try:
                content = read(path)
                parts = content.split("---", 2)
                if len(parts) != 3 or parts[0].strip():
                    raise ValueError("missing frontmatter")
                header = parts[1]
                if not re.search(rf"^name:\s*{re.escape(name)}\s*$", header, re.M):
                    raise ValueError("name mismatch")
                if not re.search(r"^description:\s*\S.+$", header, re.M):
                    raise ValueError("missing description")
                if re.search(r"^(model|allowed-tools):", header, re.M):
                    raise ValueError("unexpected model or permission override")
            except (OSError, ValueError, RuntimeError) as exc:
                errors.append(f"Invalid component {label}: {type(exc).__name__}")

    # Verify links in every instruction/reference, including paths crossing skills.
    # Reject external symlink targets before reading. URL links are not fetched.
    for directory in (root / "skills", root / "agents"):
        try:
            safe(directory)
            paths = sorted(directory.rglob("*.md"))
        except (OSError, ValueError, RuntimeError):
            errors.append(f"Unsafe component directory: {directory.name}")
            continue
        for path in paths:
            label = path.relative_to(root).as_posix()
            try:
                content = read(path)
                for link in re.findall(r"\]\(([^)]+)\)", content):
                    if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", link) or link.startswith("#"):
                        continue
                    target = unquote(link.split("#", 1)[0])
                    if not safe(path.parent / target).is_file():
                        errors.append(f"Broken local link in {label}")
            except (OSError, ValueError, RuntimeError):
                errors.append(f"Unreadable or unsafe reference: {label}")

    return {"status": "FAIL" if errors else "PASS", "plugin": manifest.get("name"),
            "version": version, "skills_checked": len(EXPECTED), "roles_checked": len(ROLES),
            "errors": errors, "warnings": warnings,
            "limits": "Layout only; does not establish session loading or security-review effectiveness."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args(argv)
    result = diagnose(args.root)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
