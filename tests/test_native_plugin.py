import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_native_plugin_has_discoverable_commands():
    manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    assert manifest["name"] == "security-harness"
    for name in ("start", "doctor", "review", "authz", "verify", "fix", "campaign", "test", "threat-model", "agent-security", "resume"):
        path = ROOT / "skills" / name / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        header = yaml.safe_load(text.split("---", 2)[1])
        assert header["name"] == name
        assert header["description"]
        # Never silently auto-approve execution or override the user's model.
        assert "allowed-tools" not in header and "model" not in header


@pytest.mark.parametrize("path", list((ROOT / "skills").rglob("*.md")))
def test_native_reference_links_resolve(path):
    for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        if "://" not in link:
            assert (path.parent / link).resolve().is_file(), (path, link)


def test_role_tool_boundaries():
    for name in ("security-architect", "security-reviewer", "security-tester", "security-verifier", "security-fixer"):
        text = (ROOT / "agents" / f"{name}.md").read_text(encoding="utf-8")
        header = yaml.safe_load(text.split("---", 2)[1])
        assert header["name"] == name and "model" not in header
        tools = {v.strip() for v in header["tools"].split(",")}
        assert "Agent" not in tools
        if name in {"security-architect", "security-reviewer", "security-verifier"}:
            assert tools == {"Read", "Glob", "Grep"}
        else:
            assert header["permissionMode"] == "default"


def test_helper_does_not_import_model_sdk():
    import subprocess
    import sys
    result = subprocess.run([sys.executable, "-c",
        "import sys; import security_harness.cli; assert not any(n.startswith(('claude_agent_sdk', 'anthropic')) for n in sys.modules)"],
        capture_output=True)
    assert result.returncode == 0, result.stderr.decode()
