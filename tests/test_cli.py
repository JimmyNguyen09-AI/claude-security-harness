import json

from security_harness.cli import main
from security_harness.models import AuthMatrix, Review, Verification, Verdict


def test_offline_audit_writes_honest_report(repo, tmp_path):
    target, _ = repo
    output = tmp_path / "report"
    assert main(["audit", str(target), "--out", str(output)]) == 3
    report = json.loads((output / "report.json").read_text())
    assert report["gate"]["state"] == "INCOMPLETE"
    assert "service.py" in report["manifest"]
    assert (output / "report.md").exists()
    assert report["review"] is None


def test_output_inside_target_denied(repo):
    target, _ = repo
    assert main(["audit", str(target), "--out", str(target / "artifacts")]) == 3
    assert not (target / "artifacts").exists()


def test_existing_artifacts_not_overwritten(repo, tmp_path):
    target, _ = repo
    output = tmp_path / "existing"
    output.mkdir()
    (output / "report.json").write_text("keep")
    assert main(["audit", str(target), "--out", str(output)]) == 3
    assert (output / "report.json").read_text() == "keep"


def test_native_findings_are_checked_without_sdk(repo, tmp_path, finding):
    target, _ = repo
    output = tmp_path / "native-report"
    review = Review(summary="Native review", findings=[finding], coverage_gaps=[])
    verification = Verification(verdicts=[Verdict(finding_id=finding.id, decision="supported", reason="Source supports missing guard", evidence=finding.evidence)])
    review_path, verify_path = tmp_path / "review.json", tmp_path / "verify.json"
    review_path.write_text(review.model_dump_json())
    verify_path.write_text(verification.model_dump_json())
    assert main(["audit", str(target), "--out", str(output), "--review-json", str(review_path),
                 "--verification-json", str(verify_path)]) == 2
    report = json.loads((output / "report.json").read_text())
    assert report["gate"]["blockers"] == [finding.id]
    assert report["verification_independence"] == "not established by this helper"


def test_authorization_matrix_rejects_conflicts():
    from pydantic import ValidationError
    import pytest
    c = {"subject": "member", "action": "read", "resource": "invoice", "tenant": "A", "context": "active", "expected": "deny"}
    with pytest.raises(ValidationError):
        AuthMatrix(cases=[c, {**c, "expected": "allow"}])
