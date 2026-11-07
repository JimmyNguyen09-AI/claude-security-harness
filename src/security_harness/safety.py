import re
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


class HarnessError(Exception):
    pass


def safe_relative(name: str) -> str:
    path = PurePosixPath(name)
    if not name or path.is_absolute() or "\\" in name or ":" in name or any(ord(c) < 32 for c in name):
        raise HarnessError("Unsafe source path")
    if any(p in {".", "..", ""} or p.endswith((".", " ")) for p in name.split("/")):
        raise HarnessError("Unsafe source path component")
    for part in path.parts:
        if part.casefold() == ".git":
            raise HarnessError("Git metadata paths cannot be materialized")
        stem = part.split(".")[0].upper()
        if stem in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(10)), *(f"LPT{i}" for i in range(10))}:
            raise HarnessError("Reserved source path")
    return name


def outside_target(path: Path, target: Path) -> Path:
    resolved = path.resolve()
    if resolved == target.resolve() or resolved.is_relative_to(target.resolve()):
        raise HarnessError("Policy/output must be outside the audited repository")
    return resolved


def redact(text: str) -> str:
    # Best effort, not a DLP guarantee. Keep line counts for source evidence.
    patterns = [
        r"(?i)(?:sk-ant-|sk-proj-|ghp_|github_pat_|AKIA)[A-Za-z0-9_-]{12,}",
        r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*['\"][^'\"\r\n]{4,}['\"]",
        r"-----BEGIN [^-]*PRIVATE KEY-----[\s\S]*?-----END [^-]*PRIVATE KEY-----",
    ]
    for pattern in patterns:
        text = re.sub(pattern, lambda m: "[REDACTED]" + "\n" * m.group(0).count("\n"), text)
    return text


@dataclass
class ProcessResult:
    code: int
    stdout: bytes
    stderr: bytes


def execute(argv: list[str], *, timeout: int = 30, limit: int = 2_000_000, cwd=None, env=None) -> ProcessResult:
    """No shell; concurrently drain bounded output and kill on overflow/timeout."""
    try:
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as exc:
        raise HarnessError(f"Cannot start {Path(argv[0]).name}: {type(exc).__name__}") from exc
    buffers = [bytearray(), bytearray()]
    overflow = threading.Event()
    lock = threading.Lock()

    def drain(stream, index):
        while chunk := stream.read(8192):
            with lock:
                if sum(map(len, buffers)) + len(chunk) > limit:
                    overflow.set()
                    proc.kill()
                    break
                buffers[index].extend(chunk)
        stream.close()

    threads = [threading.Thread(target=drain, args=(stream, i), daemon=True)
               for i, stream in enumerate((proc.stdout, proc.stderr))]
    for t in threads:
        t.start()
    timed_out = False
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        proc.wait()
    for t in threads:
        t.join(timeout=3)
    if timed_out:
        raise HarnessError("Process timeout")
    if overflow.is_set() or any(t.is_alive() for t in threads):
        raise HarnessError("Process output limit exceeded or pipe remained open")
    return ProcessResult(proc.returncode, bytes(buffers[0]), bytes(buffers[1]))
