import importlib.util
from pathlib import Path
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_release", ROOT / "scripts/check_release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


@pytest.mark.parametrize("name", [".env", ".env.production", ".venv/lib/module.py", "artifacts/report.json", "id.key", "../../outside"])
def test_private_paths_rejected(name):
    assert release.path_issues(name)


def test_normal_source_and_environment_example_allowed():
    assert release.path_issues("src/security_harness/cli.py") == []
    assert release.path_issues(".env.example") == []


def test_token_detection_never_returns_secret_value():
    token = "gh" + "p_" + "A" * 36
    result = release.content_issues(token)
    assert result == ["github-token"]
    assert token not in repr(result)


def test_private_key_and_personal_path_detected():
    assert "private-key-block" in release.content_issues("-----BEGIN " + "PRIVATE KEY-----\nfixture")
    personal = "C:" + chr(92) + "Users" + chr(92) + "fixture" + chr(92) + "project"
    assert "personal-windows-path" in release.content_issues(personal)


def test_archive_requires_license_and_notices(tmp_path):
    archive = tmp_path / "missing.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("README.md", "fixture")
    result = release.inspect_zip(archive)
    assert "archive missing LICENSE" in result
    assert "archive missing THIRD_PARTY_NOTICES.md" in result
