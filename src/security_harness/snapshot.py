import hashlib
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from .models import Policy
from .safety import HarnessError, execute, redact, safe_relative


@dataclass
class Snapshot:
    commit: str
    files: dict[str, bytes] = field(default_factory=dict)
    gaps: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    base: str | None = None

    def manifest(self):
        return {p: hashlib.sha256(b).hexdigest() for p, b in self.files.items()}

    def materialize(self, destination: Path):
        destination.mkdir(parents=True, exist_ok=False)
        for name, data in self.files.items():
            file = destination / safe_relative(name)
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(data)


def git(repo: Path, *args: str, limit=20_000_000) -> bytes:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT="0", GIT_NO_REPLACE_OBJECTS="1")
    result = execute(["git", "--no-pager", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=" + os.devnull,
                      "-C", str(repo), *args], env=env, limit=limit)
    if result.code:
        raise HarnessError("Git snapshot failed; check repository and commit reference")
    return result.stdout


def resolve_commit(repo: Path, ref: str) -> str:
    sha = git(repo, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode().strip()
    if not re.fullmatch(r"[a-f0-9]{40,64}", sha):
        raise HarnessError("Invalid commit object")
    return sha


def snapshot(repo: Path, ref: str, policy: Policy, base: str | None = None) -> Snapshot:
    snap = Snapshot(resolve_commit(repo, ref))
    tree = git(repo, "ls-tree", "-rz", "--long", snap.commit)
    total = 0
    folded = set()
    for entry in tree.split(b"\0"):
        if not entry:
            continue
        meta, raw_name = entry.split(b"\t", 1)
        mode, kind, oid, size = meta.split()
        name = raw_name.decode("utf-8", errors="strict")
        safe_relative(name)
        if name.casefold() in folded:
            raise HarnessError("Case-colliding source paths")
        folded.add(name.casefold())
        if mode not in {b"100644", b"100755"} or kind != b"blob":
            snap.gaps.append(f"Skipped non-regular Git entry: {name}")
            continue
        if len(snap.files) >= policy.max_files or int(size) > policy.max_file_bytes or total + int(size) > policy.max_snapshot_bytes:
            snap.gaps.append(f"Snapshot limit: {name}")
            continue
        # Never check out files or apply filters, hooks, LFS, or submodules.
        data = git(repo, "cat-file", "blob", oid.decode(), limit=policy.max_file_bytes + 1024)
        if data.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
            snap.gaps.append(f"LFS payload not available in Git blob: {name}")
        snap.files[name] = data
        total += len(data)
    if base:
        snap.base = resolve_commit(repo, base)
        snap.changed = git(repo, "diff", "--no-ext-diff", "--no-textconv", "--name-only", "-z", snap.base, snap.commit).decode().split("\0")
        snap.changed = [p for p in snap.changed if p]
    if not snap.files:
        snap.gaps.append("No regular source files")
    return snap


def context_bundle(snap: Snapshot, policy: Policy) -> tuple[dict[str, str], list[str]]:
    files = {}
    gaps = list(snap.gaps)
    used = 0
    priority = lambda p: (p not in snap.changed, not bool(re.search(r"auth|permission|tenant|policy|session|payment", p, re.I)), p)
    for path in sorted(snap.files, key=priority):
        data = snap.files[path]
        if Path(path).name.startswith(".env") or Path(path).suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
            gaps.append(f"Sensitive file withheld from model: {path}")
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            gaps.append(f"Non-UTF8 file omitted from model: {path}")
            continue
        if "\0" in text:
            gaps.append(f"Binary file omitted from model: {path}")
            continue
        text = redact(text)
        if used + len(text) + len(path) > policy.max_context_chars:
            gaps.append(f"Context limit: {path}")
            continue
        files[path] = text
        used += len(text) + len(path)
    return files, gaps
