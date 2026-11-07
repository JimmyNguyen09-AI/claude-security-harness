import subprocess

import pytest


@pytest.fixture
def repo(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    def git(*args):
        return subprocess.check_output(["git", "-c", "user.name=Harness Test", "-c", "user.email=test@example.invalid",
                                        "-C", str(target), *args], stderr=subprocess.DEVNULL).decode().strip()
    git("init", "-q")
    (target / "service.py").write_text("def read_invoice(user, invoice):\n    return invoice\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-qm", "fixture")
    return target, git


@pytest.fixture
def finding():
    from security_harness.models import Finding
    return Finding(id="AUTHZ-1", title="Missing ownership guard", category="authorization", severity="high",
                   status="suspected", preconditions=["Authenticated non-owner"], impact="Reads another user's invoice",
                   evidence=[{"path": "service.py", "line": 2, "quote": "return invoice"}],
                   counterevidence="No guard in fixture", remediation="Enforce owner and tenant policy",
                   regression_test="Cross-tenant denied; owner allowed")
