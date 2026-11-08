"""Package the native Claude Code plugin, without Python dependencies or credentials."""
from pathlib import Path
import json
import zipfile

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
out = root / "dist" / f"security-harness-native-{manifest['version']}.zip"
out.parent.mkdir(exist_ok=True)
files = [root / name for name in (".claude-plugin/plugin.json", "README.md", "README.vi.md",
         "LICENSE", "THIRD_PARTY_NOTICES.md", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md")]
files += sorted((root / "skills").rglob("*.md"))
files += sorted((root / "skills").rglob("*.py"))
files += sorted((root / "agents").glob("*.md"))
files += sorted((root / "schemas").glob("*.json"))
files += sorted((root / "docs").glob("*.md"))
files += [root / "evals" / name for name in ("README.md", "campaign-scenarios.json",
          "result-template.json", "expectations.json")]
for directory in ("vulnerable", "fixed", "cases"):
    files += sorted((root / "evals" / directory).glob("*.py"))
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
    for file in files:
        archive.write(file, file.relative_to(root).as_posix())
print(out)
