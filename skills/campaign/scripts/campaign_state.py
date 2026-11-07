"""Optional local campaign-ledger checks. Python stdlib only; no model or test execution."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path, PurePosixPath
import re
import sys

DOMAINS = ["authentication", "authorization", "tenant-isolation", "injection", "browser",
           "network", "files", "crypto-secrets", "data-privacy", "business-logic",
           "concurrency", "resilience", "api-protocols", "infrastructure", "supply-chain",
           "detection-response", "agent-security", "memory-safety"]
EXIT = {"PASS": 0, "BLOCK": 2, "INCOMPLETE": 3, "REVIEW": 4}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def unique_strings(values):
    return (isinstance(values, list) and bool(values) and all(nonempty(v) for v in values)
            and len(values) == len(set(values)))


def indexed(records, scope, label):
    require(isinstance(records, list) and len(records) <= 10000, f"Invalid {label} records")
    out = {}
    for record in records:
        require(isinstance(record, dict), f"Invalid {label} record")
        name = record.get("id")
        require(isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,100}", name), f"Invalid {label} ID")
        require(name not in out, f"Duplicate {label} ID")
        require(record.get("scope") == scope, f"Stale {label} record")
        out[name] = record
    return out


def references(record, field, known, needed=False):
    refs = record.get(field)
    require(isinstance(refs, list) and all(isinstance(v, str) for v in refs), f"Invalid {field} references")
    require(len(refs) == len(set(refs)), f"Duplicate {field} references")
    require(all(v in known for v in refs), f"Unknown {field} reference")
    require(bool(refs) or not needed, f"Missing {field} references")
    return [known[v] for v in refs]


def controls(records, negative_status="passed"):
    return (any(t["control"] == "positive" and t["status"] == "passed" for t in records)
            and any(t["control"] == "negative" and t["status"] == negative_status for t in records))


def validate(state, root, expected_scope):
    require(isinstance(state, dict) and state.get("schema_version") == 1, "Unsupported ledger schema")
    scope = state.get("scope")
    require(nonempty(scope) and scope == expected_scope, "Campaign scope is stale")
    surfaces, domains, modes = (state.get(k) for k in ("surfaces", "domains", "required_modes"))
    require(unique_strings(surfaces) and len(surfaces) <= 200, "Invalid surfaces")
    require(unique_strings(domains) and set(domains) <= set(DOMAINS), "Invalid domains")
    require(unique_strings(modes) and set(modes) <= {"static", "dynamic"}, "Invalid required modes")
    evidence = indexed(state.get("evidence"), scope, "evidence")
    tests = indexed(state.get("tests"), scope, "test")
    findings = indexed(state.get("findings"), scope, "finding")
    root = Path(root).resolve()
    total_bytes = 0
    for artifact in evidence.values():
        name = artifact.get("path")
        require(isinstance(name, str) and bool(name), "Invalid artifact path")
        parts = PurePosixPath(name).parts
        require(not PurePosixPath(name).is_absolute() and not any(c in name for c in "\\:\x00")
                and all(p not in {".", ".."} for p in parts), "Unsafe artifact path")
        path = root.joinpath(*parts)
        current = root
        for part in parts:
            current = current / part
            require(not current.is_symlink(), "Symlink artifact rejected")
        require(path.resolve().is_relative_to(root) and path.is_file(), "Missing/outside artifact")
        size = path.stat().st_size
        total_bytes += size
        require(size <= 5_000_000 and total_bytes <= 50_000_000, "Artifact size limit")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == artifact.get("sha256"), "Artifact hash mismatch")
    for test in tests.values():
        require(test.get("status") in {"planned", "passed", "failed", "blocked"}, "Unknown test status")
        require(test.get("control") in {"positive", "negative"}, "Unknown test control")
        executed = test["status"] in {"passed", "failed"}
        references(test, "evidence", evidence, executed)
        if executed:
            require(all(nonempty(test.get(k)) for k in ("command", "expected", "actual")), "Test observation missing")
    coverage = state.get("coverage")
    require(isinstance(coverage, list) and len(coverage) <= 200 * len(DOMAINS), "Invalid coverage")
    expected = set(itertools.product(surfaces, domains))
    seen, gaps = set(), []
    complete = 0
    for cell in coverage:
        require(isinstance(cell, dict), "Invalid coverage cell")
        coordinate = (cell.get("surface"), cell.get("domain"))
        require(all(isinstance(v, str) for v in coordinate), "Invalid coverage coordinate")
        require(coordinate in expected and coordinate not in seen, "Duplicate/unknown coverage cell")
        seen.add(coordinate)
        require(cell.get("scope") == scope, "Stale coverage cell")
        status = cell.get("status")
        require(status in {"planned", "in_progress", "blocked", "complete", "not_applicable"}, "Unknown coverage status")
        references(cell, "evidence", evidence, status in {"complete", "not_applicable"})
        linked = references(cell, "tests", tests)
        require(isinstance(cell.get("modes"), list) and all(v in {"static", "dynamic"} for v in cell["modes"]), "Invalid coverage modes")
        if status == "not_applicable":
            require(nonempty(cell.get("reason")), "N/A needs rationale")
        elif status == "complete":
            require(set(modes) <= set(cell["modes"]), "Required coverage mode missing")
            if "dynamic" in cell["modes"]:
                require(controls(linked) and all(t["status"] == "passed" for t in linked), "Dynamic coverage lacks passing controls")
            complete += 1
        else:
            gaps.append(f"{coordinate[0]}/{coordinate[1]}: {status}")
    require(seen == expected, "Missing surface/domain coverage cells")
    if not complete:
        gaps.append("No completed applicable coverage")
    blockers, unresolved = [], []
    for finding in findings.values():
        status = finding.get("status")
        require(status in {"suspected", "supported", "reproduced", "rejected", "fixed"}, "Unknown finding status")
        require(finding.get("severity") in {"low", "medium", "high", "critical"}, "Unknown finding severity")
        references(finding, "evidence", evidence, status != "suspected")
        linked = references(finding, "tests", tests)
        if status == "fixed":
            require(controls(linked) and all(t["status"] == "passed" for t in linked), "Fix lacks passing regression controls")
        if status == "reproduced":
            require(controls(linked, "failed"), "Reproduction lacks failing negative and passing positive control")
        if status in {"supported", "reproduced"} and finding["severity"] in {"high", "critical"}:
            blockers.append(finding["id"])
        elif status not in {"fixed", "rejected"}:
            unresolved.append(finding["id"])
    if any(t["status"] in {"planned", "blocked"} for t in tests.values()):
        gaps.append("Planned or blocked tests remain")
    failed = [t["id"] for t in tests.values() if t["status"] == "failed"]
    verdict = "BLOCK" if blockers else "INCOMPLETE" if gaps else "REVIEW" if unresolved or failed else "PASS"
    return {"state": verdict, "scope": scope, "complete_cells": complete, "total_cells": len(expected),
            "gaps": gaps, "blockers": blockers, "unresolved": unresolved, "failed_tests": failed,
            "meaning": "Ledger validity for selected scope/modes; not proof of exhaustive or truthful security testing."}


def initialize(out, scope, surfaces):
    require(nonempty(scope) and unique_strings(surfaces), "Scope and unique surfaces required")
    require(len(surfaces) <= 200, "Too many surfaces")
    path = Path(out)
    path.mkdir(parents=True, exist_ok=False)
    (path / "evidence").mkdir()
    state = {"schema_version": 1, "scope": scope, "surfaces": surfaces, "domains": DOMAINS,
             "required_modes": ["static", "dynamic"], "evidence": [], "tests": [], "findings": [],
             "coverage": [{"surface": s, "domain": d, "scope": scope, "status": "planned",
                           "reason": "", "modes": [], "evidence": [], "tests": []}
                          for s, d in itertools.product(surfaces, DOMAINS)]}
    (path / "campaign.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--out", required=True)
    init.add_argument("--scope", required=True)
    init.add_argument("--surfaces", nargs="+", required=True)
    check = sub.add_parser("check")
    check.add_argument("run")
    check.add_argument("--scope", required=True, help="Fingerprint of current source/configuration/fixtures")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            print(initialize(args.out, args.scope, args.surfaces))
            return 0
        root = Path(args.run)
        file = root / "campaign.json"
        require(file.stat().st_size <= 5_000_000, "Ledger size limit")
        report = validate(json.loads(file.read_text(encoding="utf-8")), root, args.scope)
        print(json.dumps(report, indent=2))
        return EXIT[report["state"]]
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({"state": "INCOMPLETE", "error": str(exc) if isinstance(exc, ValueError) and not isinstance(exc, json.JSONDecodeError) else type(exc).__name__}))
        return 3


if __name__ == "__main__":
    sys.exit(main())
