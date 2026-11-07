import argparse
import dataclasses
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from . import __version__
from .gate import gate
from .models import AuthMatrix, Policy, Review, TestSpec, Verification
from .runner import run_test, scan
from .safety import HarnessError, execute, outside_target, redact
from .snapshot import context_bundle, snapshot


EXIT = {"PASS": 0, "BLOCK": 2, "INCOMPLETE": 3, "REVIEW": 4}


def load_external(path: str, target: Path, kind):
    file = outside_target(Path(path), target)
    if file.stat().st_size > 2_000_000:
        raise HarnessError("Configuration exceeds size limit")
    return kind.model_validate_json(file.read_text(encoding="utf-8"))


def save(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def render(report: dict) -> str:
    def cell(value):
        # Prevent source/LLM strings from generating active Markdown links or HTML.
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("[", "&#91;").replace("]", "&#93;").replace("`", "&#96;").replace("|", "\\|").replace("\n", " ")
    result = report["gate"]
    lines = ["# Security review", "", f"Decision: **{result['state']}**", "",
             f"Commit: `{report['commit']}`", "", result["meaning"], "",
             "## Coverage gaps", ""]
    lines.extend(f"- {cell(g)}" for g in result["coverage_gaps"])
    if not result["coverage_gaps"]:
        lines.append("No recorded gaps in the configured scope.")
    lines += ["", "## Findings", "", "| ID | Severity | Verification | Finding |", "|---|---|---|---|"]
    verdicts = {v["finding_id"]: v["decision"] for v in (report.get("verification") or {}).get("verdicts", [])}
    for f in (report.get("review") or {}).get("findings", []):
        lines.append(f"| {cell(f['id'])} | {cell(f['severity'])} | {cell(verdicts.get(f['id'], 'unverified'))} | {cell(f['title'])} |")
    lines += ["", "Full evidence and source manifest are in report.json. Static support is not runtime reproduction.", ""]
    return "\n".join(lines)


def audit(args) -> int:
    target = Path(args.repo).resolve(strict=True)
    policy = load_external(args.policy, target, Policy) if args.policy else Policy()
    out = outside_target(Path(args.out), target)
    out.mkdir(parents=True, exist_ok=False)
    snap = snapshot(target, args.ref, policy, args.base)
    files, gaps = context_bundle(snap, policy)
    matrix = load_external(args.auth_matrix, target, AuthMatrix).model_dump() if args.auth_matrix else None
    if matrix is None:
        gaps.append("Intended authorization matrix was not supplied")
    scanners = []
    configs = {c.name: c for c in policy.scanners}
    with tempfile.TemporaryDirectory(prefix="csh-snapshot-") as tmp:
        source = Path(tmp) / "source"
        snap.materialize(source)
        # Repository-owned ignore controls cannot suppress trusted scanner rules.
        for path in source.rglob(".semgrepignore"):
            path.unlink()
        for path in source.rglob(".gitleaksignore"):
            path.unlink()
        for name in sorted(set(policy.required_scanners) | configs.keys()):
            if name not in configs:
                gaps.append(f"Required scanner not configured: {name}")
                continue
            result = scan(configs[name], source, policy)
            scanners.append(dataclasses.asdict(result))
            if result.state != "complete":
                gaps.append(f"Scanner incomplete: {name}: {result.detail}")
    review = verification = None
    if args.review_json:
        review = load_external(args.review_json, target, Review)
    if args.verification_json:
        verification = load_external(args.verification_json, target, Verification)
    if review is None or verification is None:
        gaps.append("Provide review/verification JSON written by your Claude Code session for a complete evidence check")
    # A scanner signal cannot disappear merely because an LLM omitted it.
    signal_count = sum(len(s["signals"]) for s in scanners)
    if signal_count:
        gaps.append(f"Scanner signals require explicit human triage: {signal_count}; helper does not auto-dismiss them")
    decision = gate(review, verification, files, gaps)
    report = {"harness_version": __version__, "created_at": datetime.now(timezone.utc).isoformat(),
              "commit": snap.commit, "base": snap.base, "review_origin": "user-supplied Claude Code artifacts",
              "verification_independence": "not established by this helper",
              "scope": "bounded static source review; no runtime or deployment assurance",
              "policy": policy.model_dump(),
              "policy_sha256": hashlib.sha256(policy.model_dump_json().encode()).hexdigest(),
              "manifest": snap.manifest(), "context_paths": sorted(files),
              "scanners": scanners, "review": review.model_dump() if review else None,
              "verification": verification.model_dump() if verification else None, "gate": decision}
    # Redact string values individually, preserving valid JSON.
    report = redact_values(report)
    save(out / "report.json", report)
    (out / "report.md").write_text(render(report), encoding="utf-8")
    print(f"{decision['state']}: {out / 'report.md'}")
    return EXIT[decision["state"]]


def redact_values(value):
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, list):
        return [redact_values(v) for v in value]
    if isinstance(value, dict):
        return {k: redact_values(v) for k, v in value.items()}
    return value


def test_command(args):
    target = Path(args.repo).resolve(strict=True)
    policy = load_external(args.policy, target, Policy) if args.policy else Policy()
    spec = load_external(args.spec, target, TestSpec)
    out = outside_target(Path(args.out), target)
    out.mkdir(parents=True, exist_ok=False)
    snap = snapshot(target, args.ref, policy)
    if snap.gaps:
        raise HarnessError("Cannot execute tests on an incomplete snapshot")
    with tempfile.TemporaryDirectory(prefix="csh-test-") as tmp:
        source = Path(tmp) / "source"
        snap.materialize(source)
        result = run_test(spec, source, policy)
    result["commit"] = snap.commit
    result["manifest"] = snap.manifest()
    save(out / "test.json", redact_values(result))
    print(f"{result['state']}: {out / 'test.json'}")
    return 0 if result["state"] == "passed" else 2


def doctor():
    result = {"python": sys.version.split()[0], "git": bool(shutil.which("git")),
              "docker_client": bool(shutil.which("docker")), "docker_engine": False}
    result["mode"] = "local helpers only; use the native plugin in your existing Claude Code session"
    if result["docker_client"]:
        try:
            check = execute(["docker", "info", "--format", "{{.OSType}}"], timeout=10)
            result["docker_engine"] = check.code == 0 and check.stdout.strip() == b"linux"
        except HarnessError:
            pass
    print(json.dumps(result, indent=2))
    return 0 if result["git"] else 3


def main(argv=None):
    parser = argparse.ArgumentParser(description="Evidence-oriented Claude security harness")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Check prerequisites without reading credentials")
    schema = commands.add_parser("schema", help="Print a JSON schema")
    schema.add_argument("kind", choices=["review", "verification", "policy", "test", "auth-matrix"])
    for name in ("audit", "test"):
        p = commands.add_parser(name)
        p.add_argument("repo")
        p.add_argument("--ref", default="HEAD")
        p.add_argument("--policy", help="Trusted JSON outside audited repository")
        p.add_argument("--out", required=True, help="New artifact directory outside audited repository")
        if name == "audit":
            p.add_argument("--base")
            p.add_argument("--auth-matrix")
            p.add_argument("--review-json", help="Review JSON from Claude Code; outside target")
            p.add_argument("--verification-json", help="Verification JSON from Claude Code; outside target")
        else:
            p.add_argument("--spec", required=True, help="Trusted test command/image specification outside target")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            return doctor()
        if args.command == "schema":
            model = {"review": Review, "verification": Verification, "policy": Policy,
                     "test": TestSpec, "auth-matrix": AuthMatrix}[args.kind]
            print(json.dumps(model.model_json_schema(), indent=2))
            return 0
        return audit(args) if args.command == "audit" else test_command(args)
    except (HarnessError, OSError, UnicodeError, ValidationError, ValueError) as exc:
        # Validation errors can echo untrusted config values. Print only safe messages.
        message = str(exc) if isinstance(exc, HarnessError) else type(exc).__name__
        print(f"INCOMPLETE: {message}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
