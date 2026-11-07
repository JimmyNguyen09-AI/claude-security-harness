import json
from datetime import datetime, timezone

from security_harness.models import Policy, ScannerConfig
from security_harness.runner import parse_scanner, scan
from security_harness.safety import ProcessResult


def test_osv_normalizes_package_advisories():
    data = {"results": [{"source": {"path": "package-lock.json"}, "packages": [
        {"package": {"name": "fixture-package"}, "vulnerabilities": [{"id": "TEST-2026-001"}]}]}]}
    result = parse_scanner("osv", ProcessResult(1, json.dumps(data).encode(), b""))
    assert result.signals[0]["rule"] == "TEST-2026-001"


def test_stale_osv_database_fails_closed(tmp_path):
    config = ScannerConfig(name="osv", image="example/osv@sha256:" + "a" * 64, database_date="2020-01-01")
    assert scan(config, tmp_path, Policy()).state == "incomplete"


def test_osv_uses_offline_and_trusted_config(monkeypatch, tmp_path):
    commands = []
    def fake(image, source, args, policy, rules):
        commands.append(args)
        return ProcessResult(0, b'{"results": []}', b"")
    monkeypatch.setattr("security_harness.runner.container_run", fake)
    config = ScannerConfig(name="osv", image="example/osv@sha256:" + "a" * 64,
                           database_date=datetime.now(timezone.utc).date().isoformat())
    assert scan(config, tmp_path, Policy()).state == "complete"
    assert "--offline" in commands[0] and "--config=/rules/osv.toml" in commands[0]
