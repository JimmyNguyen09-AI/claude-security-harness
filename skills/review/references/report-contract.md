# Review artifact contract

Use the [full report template](report-template.md) for shareable reports; a short
chat review can omit empty sections. Separate severity (impact/preconditions),
confidence (evidence strength) and coverage (what was actually examined). Do not
assign a numerical security score from a checklist or count of findings.

Always identify scope/version, review mode (static/runtime), verification mode
(same-session/separate-session), coverage and unexecuted checks. Default output is
chat; write files only to the user's requested location or an already established
artifact directory. Keep findings separate from coverage gaps and suggestions.

For each finding provide:

- Stable ID, title, category, severity and evidence status.
- Affected path and line(s), with a short exact quote when helpful.
- Preconditions and attacker access; entry point through affected operation.
- Violated policy/invariant and concrete confidentiality/integrity/availability impact.
- Existing defenses checked, strongest counterevidence and remaining assumptions.
- Minimal fix; negative and positive regression cases; test execution evidence if run.

Suggested Markdown output:

```markdown
# Security review
Scope: ...
Version: HEAD ...; working tree changes ...
Verification: same-session static verification / separate session / executed tests

## Findings
### AUTHZ-001 — ...
Severity: high | Status: supported
Evidence: path/to/file:42
Preconditions and path: ...
Impact and violated rule: ...
Counterevidence checked: ...
Fix and regression tests: ...

## Coverage
Reviewed: ...
Not reviewed / unavailable tools: ...
Unresolved product-policy questions: ...
```

## Optional deterministic Python gate

This is not required for normal Claude Code review. If the user asks for machine-
readable artifacts, read the harness `schemas/review.schema.json` and
`schemas/verification.schema.json` and emit separate `review.json` and
`verification.json`. They can be supplied to `csh audit --review-json ...
--verification-json ...`; that helper never calls a model.

The optional gate reads an exact Git commit, not dirty files. Export gate artifacts
only for the same commit and exact source quotes. Working-tree reports remain
native reports until the user commits or supplies another reviewed snapshot; do
not commit on their behalf merely to satisfy the helper. Static verification must
not use a `reproduced` status in the JSON schema. Empty verdicts are valid only when
the review has no findings. Helpers validate evidence provenance, not independence
or semantic correctness of Claude's reasoning.
