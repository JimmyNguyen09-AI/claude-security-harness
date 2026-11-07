import pytest
from pydantic import ValidationError

from security_harness.gate import gate, valid_evidence
from security_harness.models import Evidence, Review, Verification, Verdict

FILES = {"service.py": "def read_invoice(user, invoice):\n    return invoice\n"}


def assess(finding, decision="supported", gaps=None):
    review = Review(summary="fixture", findings=[finding], coverage_gaps=[])
    verification = Verification(verdicts=[Verdict(finding_id=finding.id, decision=decision,
                                                reason="Checked fixture", evidence=finding.evidence)])
    return gate(review, verification, FILES, gaps or [])


def test_supported_high_blocks_even_with_incomplete_coverage(finding):
    result = assess(finding, gaps=["missing dependency"])
    assert result["state"] == "BLOCK" and not result["complete"]


def test_supported_medium_is_reported_without_block(finding):
    finding.severity = "medium"
    assert assess(finding)["state"] == "PASS"


def test_inconclusive_requires_review(finding):
    assert assess(finding, "inconclusive")["state"] == "REVIEW"


def test_missing_claude_never_passes():
    assert gate(None, None, FILES, [])["state"] == "INCOMPLETE"


def test_fabricated_quote_cannot_block_or_pass(finding):
    finding.evidence[0].quote = "made up source"
    assert assess(finding)["state"] == "INCOMPLETE"


def test_quote_on_wrong_line_is_invalid():
    assert not valid_evidence([Evidence(path="service.py", line=1, quote="return invoice")], FILES)


def test_duplicate_or_omitted_verdicts_fail_closed(finding):
    review = Review(summary="", findings=[finding], coverage_gaps=[])
    assert gate(review, Verification(verdicts=[]), FILES, [])["state"] == "INCOMPLETE"
    verdict = Verdict(finding_id=finding.id, decision="rejected", reason="fixture", evidence=finding.evidence)
    assert gate(review, Verification(verdicts=[verdict, verdict]), FILES, [])["state"] == "INCOMPLETE"


def test_model_cannot_claim_runtime_reproduction(finding):
    data = finding.model_dump()
    data["status"] = "reproduced"
    with pytest.raises(ValidationError):
        type(finding).model_validate(data)


def test_unknown_fields_rejected(finding):
    data = finding.model_dump()
    data["approve_merge"] = True
    with pytest.raises(ValidationError):
        type(finding).model_validate(data)
