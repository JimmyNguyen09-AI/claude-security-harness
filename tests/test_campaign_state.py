import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/campaign/scripts/campaign_state.py"
spec = importlib.util.spec_from_file_location("campaign_state", SCRIPT)
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


@pytest.fixture
def run(tmp_path):
    (tmp_path / "evidence").mkdir()
    artifact = tmp_path / "evidence/observations.txt"
    artifact.write_text("Synthetic positive and negative control observations\n")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    state = {"schema_version": 1, "scope": "commit-fixture-config-v1", "surfaces": ["api"],
             "domains": ["authorization"], "required_modes": ["static", "dynamic"],
             "evidence": [{"id": "E1", "scope": "commit-fixture-config-v1", "path": "evidence/observations.txt", "sha256": digest}],
             "tests": [], "findings": [], "coverage": []}
    for name, control in [("T1", "positive"), ("T2", "negative")]:
        state["tests"].append({"id": name, "scope": state["scope"], "status": "passed", "control": control,
                               "command": "synthetic fixture", "expected": "invariant holds", "actual": "observed invariant",
                               "evidence": ["E1"]})
    state["coverage"].append({"surface": "api", "domain": "authorization", "scope": state["scope"],
                              "status": "complete", "reason": "", "modes": ["static", "dynamic"],
                              "evidence": ["E1"], "tests": ["T1", "T2"]})
    return state, tmp_path


def check(run):
    state, root = run
    return ledger.validate(state, root, state["scope"])


def test_valid_structural_ledger_passes(run):
    assert check(run)["state"] == "PASS"


def test_empty_initialized_campaign_is_incomplete(tmp_path):
    target = tmp_path / "new-run"
    ledger.initialize(target, "scope", ["api", "worker"])
    data = json.loads((target / "campaign.json").read_text())
    assert len(data["coverage"]) == 36
    assert ledger.validate(data, target, "scope")["state"] == "INCOMPLETE"
    with pytest.raises(FileExistsError):
        ledger.initialize(target, "scope", ["api"])


@pytest.mark.parametrize("collection", ["evidence", "tests", "coverage"])
def test_stale_records_rejected(run, collection):
    run[0][collection][0]["scope"] = "old-version"
    with pytest.raises(ValueError, match="Stale"):
        check(run)


def test_current_scope_must_match(run):
    with pytest.raises(ValueError, match="stale"):
        ledger.validate(run[0], run[1], "changed-source")


def test_artifact_tampering_detected(run):
    (run[1] / "evidence/observations.txt").write_text("changed result")
    with pytest.raises(ValueError, match="hash"):
        check(run)


@pytest.mark.parametrize("path", ["../outside", "/tmp/external", "C:/secrets", "a\\b"])
def test_artifacts_cannot_escape_run(run, path):
    run[0]["evidence"][0]["path"] = path
    with pytest.raises(ValueError):
        check(run)


def test_missing_cell_and_duplicate_cell_rejected(run):
    state, _ = run
    original = state["coverage"][0]
    state["coverage"] = []
    with pytest.raises(ValueError, match="Missing"):
        check(run)
    state["coverage"] = [original, original]
    with pytest.raises(ValueError, match="Duplicate"):
        check(run)


def test_no_positive_control_cannot_clear_dynamic_coverage(run):
    run[0]["coverage"][0]["tests"] = ["T2"]
    with pytest.raises(ValueError, match="controls"):
        check(run)


def test_claimed_dynamic_mode_requires_controls_even_in_static_campaign(run):
    run[0]["required_modes"] = ["static"]
    run[0]["coverage"][0]["tests"] = []
    with pytest.raises(ValueError, match="controls"):
        check(run)


def test_planned_test_cannot_be_reported_as_executed(run):
    run[0]["tests"][0]["status"] = "planned"
    with pytest.raises(ValueError, match="controls"):
        check(run)


def test_empty_observation_rejected(run):
    run[0]["tests"][0]["actual"] = ""
    with pytest.raises(ValueError, match="observation"):
        check(run)


def test_na_needs_rationale_and_cannot_clear_everything(run):
    cell = run[0]["coverage"][0]
    cell["status"] = "not_applicable"
    with pytest.raises(ValueError, match="rationale"):
        check(run)
    cell["reason"] = "Fixture-specific exclusion"
    assert check(run)["state"] == "INCOMPLETE"


def test_high_finding_blocks_even_with_pending_work(run):
    state, _ = run
    state["coverage"][0]["status"] = "in_progress"
    state["findings"] = [{"id": "F1", "scope": state["scope"], "severity": "high",
                           "status": "supported", "evidence": ["E1"], "tests": []}]
    assert check(run)["state"] == "BLOCK"


def test_fixed_finding_requires_regression_controls(run):
    state, _ = run
    state["findings"] = [{"id": "F1", "scope": state["scope"], "severity": "high",
                           "status": "fixed", "evidence": ["E1"], "tests": ["T1"]}]
    with pytest.raises(ValueError, match="regression"):
        check(run)


def test_reproduction_is_not_merely_a_passing_test(run):
    state, _ = run
    state["findings"] = [{"id": "F1", "scope": state["scope"], "severity": "high",
                           "status": "reproduced", "evidence": ["E1"], "tests": ["T1", "T2"]}]
    with pytest.raises(ValueError, match="Reproduction"):
        check(run)


def test_failed_test_forces_review_in_static_scope(run):
    state, _ = run
    state["required_modes"] = ["static"]
    state["coverage"][0]["modes"] = ["static"]
    state["tests"][1]["status"] = "failed"
    assert check(run)["state"] == "REVIEW"


def test_malformed_ledger_returns_nonzero(tmp_path, capsys):
    (tmp_path / "campaign.json").write_text('{"secret":')
    assert ledger.main(["check", str(tmp_path), "--scope", "test"]) == 3
    output = json.loads(capsys.readouterr().out)
    assert output["state"] == "INCOMPLETE"
