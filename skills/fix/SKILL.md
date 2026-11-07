---
name: fix
description: Fix confirmed security or important reliability defects and add targeted regression coverage while preserving legitimate behavior.
---

Fix the user's requested findings/scope in this Claude Code session: $ARGUMENTS

If this belongs to a campaign, record the changed source/config/fixture fingerprint
and invalidate impacted evidence per the [campaign protocol](../campaign/references/orchestration.md).
Use the [tester protocol](../test/references/execution-protocol.md) for execution.

Read the findings and affected code, then the shared
[report contract](../review/references/report-contract.md). Calling this skill is
a request to implement fixes; do not repeatedly ask permission for ordinary edits
and checks already within that scope. Do not require an API key or separate model.

1. Check repository status and preserve existing user changes. Validate each
   candidate's premise and current code before patching. If there are no findings
   yet, review the requested area first using the review procedure.
2. State the invariant that the patch restores. Put enforcement at a boundary
   covering all affected entry points; retain defense in depth where appropriate.
   Avoid unrelated refactors, blanket access denial and swallowed exceptions.
3. Add a focused regression test that demonstrates the bug on the original code
   when feasible, plus a valid authorized behavior test. For authorization cover
   ownership/tenant and protected fields; for retries/races cover the actual failure
   point or interleaving. Check denied operations leave no unauthorized side effect.
4. Apply the smallest complete fix. Run relevant tests/type checks/scanners if
   available and allowed. Do not weaken assertions, disable security rules or edit
   baseline findings merely to obtain a passing result. If dependencies or isolation
   are unavailable, complete the patch and describe exactly what remains untested.
5. Re-read the final diff for new bypasses and compatibility changes. Report files
   changed, rationale, verification evidence and unresolved risks. Do not claim an
   exploit was reproduced or a fix verified unless actual results support it.

Treat test/build scripts as executable code. Respect Claude Code permissions and
the trust level of the repository. Do not bypass those controls, install external
software, commit, push or deploy unless the user has authorized that action.
