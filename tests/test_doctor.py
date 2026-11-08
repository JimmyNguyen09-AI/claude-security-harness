import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("plugin_doctor", ROOT / "skills/doctor/scripts/doctor.py")
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)


@pytest.fixture
def plugin(tmp_path):
    for directory in (".claude-plugin", "skills", "agents", "docs"):
        shutil.copytree(ROOT / directory, tmp_path / directory)
    return tmp_path


def test_repository_layout():
    result = doctor.diagnose(ROOT)
    assert result["status"] == "PASS", result
    assert result["skills_checked"] == 11


def test_missing_root_is_failure(tmp_path):
    assert doctor.diagnose(tmp_path / "absent")["status"] == "FAIL"


@pytest.mark.parametrize("content", ["{", "[]", "null", '{"name":"other","version":null}'])
def test_bad_manifest_fails_closed(plugin, content):
    (plugin / ".claude-plugin/plugin.json").write_text(content, encoding="utf-8")
    assert doctor.diagnose(plugin)["status"] == "FAIL"


def test_missing_skill_and_reference_detected(plugin):
    (plugin / "skills/start/SKILL.md").unlink()
    (plugin / "skills/review/references/report-template.md").unlink()
    result = doctor.diagnose(plugin)
    assert result["status"] == "FAIL"
    assert any("skills/start/SKILL.md" in error for error in result["errors"])
    assert any("Broken local link" in error for error in result["errors"])


def test_reference_cannot_escape_root(plugin):
    path = plugin / "skills/start/SKILL.md"
    with path.open("a", encoding="utf-8") as stream:
        stream.write("\n[escape](../../../../outside.md)\n")
    result = doctor.diagnose(plugin)
    assert result["status"] == "FAIL"
    assert any("unsafe reference" in error for error in result["errors"])


def test_external_symlink_rejected(plugin, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "secret.md"
    outside.write_text("do-not-return-this-content", encoding="utf-8")
    path = plugin / "skills/start/references/linked.md"
    try:
        path.symlink_to(outside)
    except OSError:
        pytest.skip("Creating symlinks is unavailable on this host")
    result = doctor.diagnose(plugin)
    assert result["status"] == "FAIL"
    assert "do-not-return-this-content" not in json.dumps(result)


def test_wrong_marketplace_source_rejected(plugin):
    path = plugin / ".claude-plugin/marketplace.json"
    data = json.loads(path.read_text())
    data["plugins"][0]["source"] = "./missing"
    path.write_text(json.dumps(data))
    assert doctor.diagnose(plugin)["status"] == "FAIL"


def test_native_archive_works_without_repository_or_dependencies(tmp_path):
    subprocess.run([sys.executable, str(ROOT / "scripts/package_plugin.py")], check=True)
    version = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())["version"]
    with zipfile.ZipFile(ROOT / "dist" / f"security-harness-native-{version}.zip") as archive:
        archive.extractall(tmp_path)
    result = subprocess.run([sys.executable, "-I", str(tmp_path / "skills/doctor/scripts/doctor.py")],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "PASS"
    assert (tmp_path / "evals/README.md").is_file()
    assert (tmp_path / "evals/cases/guarded_service.py").is_file()
