from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Evidence(StrictModel):
    path: str = Field(min_length=1, max_length=500)
    line: int = Field(ge=1)
    quote: str = Field(min_length=1, max_length=2000)


class Finding(StrictModel):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")
    title: str = Field(min_length=1, max_length=300)
    category: Literal["authentication", "authorization", "injection", "secrets", "dependencies", "reliability", "configuration"]
    severity: Literal["low", "medium", "high", "critical"]
    status: Literal["suspected", "supported", "rejected", "inconclusive"]
    preconditions: list[str] = Field(min_length=1, max_length=20)
    impact: str = Field(min_length=1, max_length=3000)
    evidence: list[Evidence] = Field(min_length=1, max_length=20)
    counterevidence: str = Field(min_length=1, max_length=3000)
    remediation: str = Field(min_length=1, max_length=3000)
    regression_test: str = Field(min_length=1, max_length=3000)


class Review(StrictModel):
    summary: str = Field(max_length=5000)
    findings: list[Finding] = Field(max_length=100)
    coverage_gaps: list[str] = Field(max_length=100)

    @model_validator(mode="after")
    def unique_ids(self):
        ids = [f.id for f in self.findings]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate finding IDs")
        return self


class Verdict(StrictModel):
    finding_id: str
    decision: Literal["supported", "rejected", "inconclusive"]
    reason: str = Field(min_length=1, max_length=5000)
    evidence: list[Evidence] = Field(min_length=1, max_length=20)


class Verification(StrictModel):
    verdicts: list[Verdict] = Field(max_length=100)


class ScannerConfig(StrictModel):
    name: Literal["semgrep", "gitleaks", "osv"]
    image: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._/:\-]*@sha256:[a-f0-9]{64}$")
    database_date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")

    @model_validator(mode="after")
    def osv_database_provenance(self):
        if self.name == "osv":
            if self.database_date is None:
                raise ValueError("OSV requires the date of its image-baked offline database")
            from datetime import date
            date.fromisoformat(self.database_date)
        return self


class Policy(StrictModel):
    max_file_bytes: int = Field(default=100_000, ge=100, le=1_000_000)
    max_snapshot_bytes: int = Field(default=20_000_000, ge=1000, le=100_000_000)
    max_context_chars: int = Field(default=160_000, ge=1000, le=500_000)
    max_files: int = Field(default=5000, ge=1, le=20_000)
    timeout_seconds: int = Field(default=180, ge=1, le=900)
    max_output_bytes: int = Field(default=2_000_000, ge=1000, le=10_000_000)
    required_scanners: list[Literal["semgrep", "gitleaks", "osv"]] = Field(default_factory=lambda: ["semgrep", "gitleaks", "osv"])
    scanners: list[ScannerConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_scanners(self):
        names = [s.name for s in self.scanners]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate scanner definitions")
        return self


class TestSpec(StrictModel):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")
    image: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._/:\-]*@sha256:[a-f0-9]{64}$")
    argv: list[str] = Field(min_length=1, max_length=50)
    expected_exit: int = Field(default=0, ge=0, le=124)


class AuthCase(StrictModel):
    subject: str
    action: str
    resource: str
    tenant: str
    context: str
    expected: Literal["allow", "deny"]


class AuthMatrix(StrictModel):
    cases: list[AuthCase] = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def no_conflicts(self):
        seen = set()
        for c in self.cases:
            key = (c.subject, c.action, c.resource, c.tenant, c.context)
            if key in seen:
                raise ValueError("Duplicate or conflicting authorization case")
            seen.add(key)
        return self
