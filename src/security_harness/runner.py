import json
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from .models import Policy, ScannerConfig, TestSpec
from .safety import HarnessError, ProcessResult, execute, redact


def docker_argv(image: str, source: Path, name: str, argv: list[str], rules: Path | None = None) -> list[str]:
    from .models import ScannerConfig
    # Validate digest even for direct API callers, not just CLI config.
    ScannerConfig(name="semgrep", image=image)
    mounts = [(source, "/src")]
    if rules:
        mounts.append((rules, "/rules"))
    command = ["docker", "run", "--rm", "--pull=never", "--name", name,
               "--network=none", "--read-only", "--cap-drop=ALL",
               "--security-opt=no-new-privileges", "--pids-limit=64",
               "--memory=1g", "--cpus=1", "--user=65534:65534",
               "--log-driver=none", "--tmpfs", "/tmp:rw,nosuid,nodev,size=128m",
               "--env", "HOME=/tmp", "--workdir", "/src"]
    for host, guest in mounts:
        resolved = str(host.resolve())
        if any(c in resolved for c in [",", "\n", "\r"]):
            raise HarnessError("Unsupported bind-mount path")
        command += ["--mount", f"type=bind,src={resolved},dst={guest},readonly"]
    return command + [image, *argv]


def container_run(image: str, source: Path, argv: list[str], policy: Policy, rules: Path | None = None) -> ProcessResult:
    name = "csh-" + uuid.uuid4().hex
    command = docker_argv(image, source, name, argv, rules)
    try:
        return execute(command, timeout=policy.timeout_seconds, limit=policy.max_output_bytes)
    finally:
        # Killing the Docker client does not kill its container. Always clean it up.
        try:
            execute(["docker", "rm", "-f", name], timeout=15, limit=100_000)
        except HarnessError:
            pass


@dataclass
class ScanResult:
    name: str
    state: str
    signals: list[dict]
    detail: str = ""


def parse_scanner(name: str, result: ProcessResult) -> ScanResult:
    if result.code not in {0, 1}:
        raise HarnessError(f"{name} failed with exit {result.code}")
    try:
        payload = json.loads(result.stdout)
        if name == "semgrep":
            if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
                raise ValueError("Malformed Semgrep result")
            if payload.get("errors"):
                raise ValueError("Semgrep reported scan errors")
            signals = [{"rule": r["check_id"], "path": r["path"], "line": r["start"]["line"],
                        "message": r["extra"]["message"]} for r in payload["results"]]
        elif name == "gitleaks":
            if not isinstance(payload, list):
                raise ValueError("Malformed Gitleaks result")
            # Deliberately omit Secret/Match/Line and raw scanner diagnostics.
            signals = [{"rule": r["RuleID"], "path": r["File"], "line": r["StartLine"],
                        "message": "Potential secret (value withheld)"} for r in payload]
        elif name == "osv":
            if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
                raise ValueError("Malformed OSV result")
            signals = []
            for result_group in payload["results"]:
                for package in result_group["packages"]:
                    for vulnerability in package.get("vulnerabilities", []):
                        signals.append({"rule": vulnerability["id"], "path": result_group["source"]["path"],
                                        "package": package["package"]["name"], "message": "Known dependency vulnerability"})
        else:
            raise ValueError("Unknown scanner")
        if result.code == 1 and not signals:
            raise ValueError("Nonzero exit without findings")
    except (ValueError, KeyError, TypeError) as exc:
        raise HarnessError(f"{name} returned invalid or incomplete output") from exc
    signals = [{k: redact(v) if isinstance(v, str) else v for k, v in s.items()} for s in signals]
    return ScanResult(name, "complete", signals)


def scan(config: ScannerConfig, source: Path, policy: Policy) -> ScanResult:
    if config.name == "semgrep":
        args = ["semgrep", "scan", "--config=/rules/security.yml", "--json", "--metrics=off",
                "--disable-version-check", "--no-git-ignore", "--nosem", "/src"]
        rules = Path(__file__).parent / "rules"
    elif config.name == "gitleaks":
        args = ["dir", "/src", "--config=/rules/gitleaks.toml", "--report-format=json", "--report-path=/dev/stdout",
                "--redact=100", "--no-banner", "--ignore-gitleaks-allow"]
        rules = Path(__file__).parent / "rules"
    else:
        age = (datetime.now(timezone.utc).date() - date.fromisoformat(config.database_date)).days
        if age < 0 or age > 7:
            return ScanResult("osv", "incomplete", [], "Offline vulnerability database is future-dated or older than 7 days")
        args = ["scan", "source", "--offline", "--recursive", "--format=json",
                "--config=/rules/osv.toml", "/src"]
        rules = Path(__file__).parent / "rules"
    try:
        return parse_scanner(config.name, container_run(config.image, source, args, policy, rules))
    except HarnessError as exc:
        return ScanResult(config.name, "incomplete", [], str(exc))


def run_test(spec: TestSpec, source: Path, policy: Policy) -> dict:
    result = container_run(spec.image, source, spec.argv, policy)
    return {"id": spec.id, "image": spec.image, "argv": spec.argv,
            "exit": result.code, "expected_exit": spec.expected_exit,
            "state": "passed" if result.code == spec.expected_exit else "failed",
            "stdout": redact(result.stdout.decode(errors="replace")),
            "stderr": redact(result.stderr.decode(errors="replace")),
            "note": "Command outcome only; does not independently prove a vulnerability or fix."}
