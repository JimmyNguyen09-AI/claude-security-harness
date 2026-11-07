# Campaign state contract

Use a unique output directory outside the target. Suggested layout:

```text
run/
  campaign.json
  threat-model.md
  work-packages.md
  findings.md
  evidence/<package>/<immutable-artifact>
  checkpoint.md
```

The coordinator is the sole writer of campaign.json. Workers return per-package
artifacts; never share mutable test databases or ledger writes. Preserve previous
runs. At a checkpoint record completed packages, next actions, assumptions, source/
config/fixture fingerprint, budgets and unresolved issues. Read it before resuming.

## Optional stdlib helper

`scripts/campaign_state.py` belongs to this skill. It uses Python's standard library
only, never calls a model and never executes tests. Normal native workflows can
maintain these artifacts manually without Python.

```text
python campaign_state.py init --out <new-run> --scope <fingerprint> --surfaces api worker
python campaign_state.py check <run> --scope <current-fingerprint>
```

Fingerprint: commit plus hashes of dirty source, test fixtures and effective
security configuration. Compute from actual inputs; do not overwrite an old record's
fingerprint merely to make it current. `check --scope` is required so a stale ledger
cannot silently use its own claimed version as current truth. The helper does not
compute repository fingerprints or prove they were derived honestly.

## JSON records

- `schema_version`: 1; `scope`: fingerprint; `surfaces`: unique IDs;
  `domains`: selected catalogue IDs; `required_modes`: static and/or dynamic.
  Init includes all 18 domains and both modes. Choose applicability explicitly.
- `coverage`: exactly one record per surface/domain, with `surface`, `domain`,
  `scope`, `status` (planned/in_progress/blocked/complete/not_applicable), `reason`,
  `modes`, `evidence` (IDs), `tests` (IDs). N/A needs a rationale and evidence.
- `evidence`: records with `id`, `scope`, `path` relative to run, `sha256` (content
  hash). Use bounded regular files inside run; no symlinks or external references.
  Artifacts must be redacted before hashing. The checker verifies hashes/paths,
  not semantic meaning, authorship, timestamps or independence.
- `tests`: records with `id`, `scope`, `status` (planned/passed/failed/blocked),
  `control` (positive/negative), `command`, `expected`, `actual`, `evidence` IDs.
  Passed/failed records require observation evidence and all three text fields.
- `findings`: records with `id`, `scope`, `severity` (low/medium/high/critical),
  `status` (suspected/supported/reproduced/rejected/fixed), `evidence` IDs,
  `tests` IDs. Fixed requires passing positive and negative controls; rejected and
  supported claims require evidence. Reproduced additionally needs a failing
  negative control and passing positive control. These are structural checks.

Completed coverage needs evidence and every required mode. Dynamic completion
needs linked passing positive and negative controls; domain-specific additional
cases remain the tester's responsibility. Each link must resolve. Stale records,
unknown states, missing cells/evidence, or fabricated artifact hashes -> INCOMPLETE.
An open supported/reproduced high/critical finding -> BLOCK, even with gaps.
Other open findings or failed tests -> REVIEW. At least one cell must be complete;
a matrix entirely marked N/A cannot pass. PASS means complete ledger for the selected
scope/modes, not exhaustive security or proof that reports are true.

Exit codes: PASS=0, BLOCK=2, INCOMPLETE=3, REVIEW=4. No waiver/auto-suppression exists.
Manual JSON can be edited; a hostile writer can fabricate evidence. Use trusted CI
and retained immutable artifacts if a stronger provenance boundary is required.
