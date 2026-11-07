---
name: campaign
description: Coordinate a large or multi-service security audit with risk-based work packages, tester roles, coverage tracking and resumable evidence.
---

Run the requested security campaign in the existing Claude Code session: $ARGUMENTS
No API key, SDK or separate model process is required.

Read [orchestration](references/orchestration.md),
[state contract](references/state-contract.md) and the
[test catalogue](../test/references/security-catalogue.md).

1. Establish target version (commit plus dirty-content hashes when relevant),
   included services, entry points, shared dependencies and authorized test targets.
   Start source review immediately. Live test execution needs a concrete target
   and bounded execution scope; source access alone does not authorize attacking
   production or third parties. Use synthetic local fixtures by default.
2. Build the threat model and a surface-by-domain coverage matrix. Select explicit
   applicable domains; retain every omitted domain as justified not-applicable or
   unreviewed. Prioritize public entry points, privileged operations, tenant/data
   boundaries, money, secrets and newly changed shared components.
3. Split work by trust boundary and invariant, not arbitrary file counts. Assign
   architect, reviewer, tester, verifier and fixer responsibilities. Use the bundled
   specialist agents when the session supports delegation and the user/task scope
   permits it; otherwise execute roles sequentially and disclose self-verification.
   Keep a single coordinator as owner of aggregate state and gate decisions.
4. Execute bounded work packages with a target version, evidence, assumptions,
   completion criteria and budget. Load only relevant references/source. Keep
   cross-service contract checks as separate work packages; module completion
   does not imply integration completion. Testers generate and execute negative,
   positive, boundary, stateful and failure-path cases from invariants.
5. Checkpoint results to the established output location after each package and
   before context compaction. If no location is given, use a unique sibling audit
   directory outside the target repository and state that choice. Never overwrite
   previous results. Use the state contract to resume, not conversation memory alone.
6. Reconcile duplicate root causes without dropping entry points or evidence.
   Verify findings and, when fixes are requested, route patches through tester and
   verifier. Re-run impacted packages after any code/policy/config/fixture change.
7. Report blockers, unresolved hypotheses, coverage, unsupported areas, failed
   infrastructure and actual test results. Budget exhaustion is incomplete work.
   Do not claim all security aspects tested or global safety based on a checklist.

Optional: `python <this-skill-dir>/scripts/campaign_state.py init --out <new-run>
--scope <version-fingerprint> --surfaces api worker` creates a ledger. `check <run> --scope <current-fingerprint>`
validates references, evidence hashes, freshness and coverage without calling a
model. Read `--help` first. Manual JSON/Markdown tracking remains available when
Python is absent. This checker validates the ledger, not truth or independence.
