import json
import sys

import pytest
from pydantic import ValidationError

from security_harness.runner import container_run, docker_argv, parse_scanner
from security_harness.models import Policy
from security_harness.safety import HarnessError, ProcessResult, execute, redact

IMAGE = "example/scanner@sha256:" + "a" * 64


def test_container_has_no_host_credentials_or_network(tmp_path):
    argv = docker_argv(IMAGE, tmp_path, "test", ["python", "test.py"])
    for flag in ["--network=none", "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges", "--pull=never", "--user=65534:65534"]:
        assert flag in argv
    assert len([a for a in argv if a.startswith("type=bind")]) == 1
    assert argv[-3:] == [IMAGE, "python", "test.py"]
    assert not any("docker.sock" in a for a in argv)


def test_unpinned_image_rejected(tmp_path):
    with pytest.raises(ValidationError):
        docker_argv("python:latest", tmp_path, "test", [])


def test_container_cleanup_on_timeout(monkeypatch, tmp_path):
    calls = []
    def fake(argv, **kwargs):
        calls.append(argv)
        if argv[1] == "run":
            raise HarnessError("Process timeout")
        return ProcessResult(0, b"", b"")
    monkeypatch.setattr("security_harness.runner.execute", fake)
    with pytest.raises(HarnessError):
        container_run(IMAGE, tmp_path, [], Policy())
    assert calls[-1][:3] == ["docker", "rm", "-f"]
    assert calls[-1][-1] == calls[0][calls[0].index("--name") + 1]


def test_process_output_bounded():
    with pytest.raises(HarnessError, match="output"):
        execute([sys.executable, "-c", "print('x' * 100000)"], limit=1000)


def test_process_timeout():
    with pytest.raises(HarnessError, match="timeout"):
        execute([sys.executable, "-c", "import time; time.sleep(5)"], timeout=1)


@pytest.mark.parametrize("payload,code", [(b"garbage", 0), (b'{}', 0), (b'{"results":[],"errors":[{}]}', 0), (b'{"results":[]}', 2)])
def test_bad_scanner_output_never_clean(payload, code):
    with pytest.raises(HarnessError):
        parse_scanner("semgrep", ProcessResult(code, payload, b""))


def test_gitleaks_raw_secret_never_published():
    payload = [{"RuleID": "token", "File": "a.py", "StartLine": 1,
                "Secret": "extremely-sensitive", "Match": "extremely-sensitive"}]
    result = parse_scanner("gitleaks", ProcessResult(1, json.dumps(payload).encode(), b""))
    assert "extremely-sensitive" not in repr(result)
    assert len(result.signals) == 1


def test_redaction_preserves_line_numbers():
    text = "-----BEGIN PRIVATE KEY-----\nabcdef\n-----END PRIVATE KEY-----\nend"
    result = redact(text)
    assert "abcdef" not in result
    assert text.count("\n") == result.count("\n")
