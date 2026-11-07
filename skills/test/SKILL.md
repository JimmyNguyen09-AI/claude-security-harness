---
name: test
description: Design and run security regression, abuse-case, boundary, integration and adversarial tests with controlled fixtures and evidence.
---

Act as the security tester for: $ARGUMENTS
Use the current Claude Code login/tools; do not start an SDK or request an API key.
Read [the test catalogue](references/security-catalogue.md) and
[execution protocol](references/execution-protocol.md). For AI-agent targets read
[agent attack surfaces](../agent-security/references/agent-threats.md).
Select relevant layers from [stack profiles](references/stack-profiles.md).

Derive tests from intended invariants and the threat model, not only implementation.
Create a plan mapping surface/domain/threat -> case -> oracle -> artifact. For each
applicable boundary include denial and legitimate allow controls. Include malformed,
boundary-size, replay, stateful/multi-step, concurrency and dependency-failure cases
where relevant. Explain N/A cases; do not imply exhaustive coverage.

Inspect test harness/scripts, confirm fixtures and execution scope, then implement
and run safe local tests already authorized by the request. A request to test
permits relevant test additions, not unrelated production changes. Respect existing
user edits. For remote systems, destructive cases or stress tests, use existing
authorization specifying target, environment and limits; request only missing scope.
Continue planning/static work while execution is blocked.

Record command, tested version, fixture seed, environment, expected/actual result,
positive/negative controls and artifact. Setup failure is blocked, not passed or a
product vulnerability. A red test must fail for the intended invariant. Reproduce
against known-bad and fixed versions where available without resetting user work.
Check response data, durable state, messages, external effects and logs—not only
HTTP status. Do not swallow errors or weaken assertions to make the suite green.

Return executed/not-executed cases, findings, coverage and next actions. Hand
confirmed defects to fix; re-test changed behavior and legitimate workflows after
patching. Never label test design alone as execution or reproduction.
