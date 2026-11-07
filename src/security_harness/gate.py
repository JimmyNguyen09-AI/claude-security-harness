from .models import Evidence, Review, Verification


def valid_evidence(items: list[Evidence], files: dict[str, str]) -> bool:
    for evidence in items:
        text = files.get(evidence.path)
        if text is None:
            return False
        lines = text.splitlines()
        if evidence.line > len(lines):
            return False
        tail = "\n".join(lines[evidence.line - 1:])
        # Quote must begin on the cited line, not merely appear somewhere later.
        offset = tail.find(evidence.quote)
        if offset < 0 or offset > len(lines[evidence.line - 1]) or "\n" in tail[:offset]:
            return False
    return bool(items)


def gate(review: Review | None, verification: Verification | None, files: dict[str, str], gaps: list[str]) -> dict:
    reasons = list(gaps)
    blocked = []
    unresolved = []
    if review is None or verification is None:
        reasons.append("Review and verification artifacts not supplied")
    else:
        reasons.extend(review.coverage_gaps)
        ids = [v.finding_id for v in verification.verdicts]
        if len(ids) != len(set(ids)) or set(ids) != {f.id for f in review.findings}:
            reasons.append("Verifier IDs do not match candidates exactly")
        verdicts = {v.finding_id: v for v in verification.verdicts}
        for finding in review.findings:
            verdict = verdicts.get(finding.id)
            if not valid_evidence(finding.evidence, files) or verdict is None or not valid_evidence(verdict.evidence, files):
                reasons.append(f"Invalid or missing evidence: {finding.id}")
                continue
            if verdict.decision == "supported" and finding.severity in {"high", "critical"}:
                blocked.append(finding.id)
            elif verdict.decision == "inconclusive":
                unresolved.append(finding.id)
    # A known blocker remains a blocker even when coverage is incomplete.
    state = "BLOCK" if blocked else "INCOMPLETE" if reasons else "REVIEW" if unresolved else "PASS"
    return {"state": state, "complete": not reasons, "blockers": blocked,
            "unresolved": unresolved, "coverage_gaps": sorted(set(reasons)),
            "meaning": "Decision for this commit and configured scope; not proof of security."}
