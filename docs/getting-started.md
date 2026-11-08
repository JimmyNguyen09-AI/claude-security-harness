# First useful review

Install **security-harness** from the `JimmyNguyen09-AI/claude-security-harness`
marketplace using the GUI steps in the README. Open the project you want to audit
in Claude Code, then enter this in the **chat box**, not a shell:

```text
/security-harness:start review this project, prioritizing permissions and data exposure
```

The workflow inspects the project, states its scope and starts tracing sensitive
flows. You do not need to learn every command or install scanners first. It uses
your existing Claude Code account; native review requires no Python or Docker.

## Choose by outcome

| What you need | Message in Claude Code |
|---|---|
| Review a change | `/security-harness:review compare with main, prioritize changed trust boundaries and affected callers` |
| Large repository | `/security-harness:campaign audit API, workers and shared auth; save checkpoints outside the repo` |
| Multi-tenant checks | `/security-harness:authz trace tenant isolation through DB, cache, jobs and exports` |
| Test coverage | `/security-harness:test write and run local tests for confirmed defects, including valid-user controls` |
| AI-agent safety | `/security-harness:agent-security inspect tool authorization, approval binding and retrieval isolation` |
| Reduce false positives | `/security-harness:verify challenge this report against the actual enforcement layers` |
| Repair | `/security-harness:fix fix AUTHZ-001, preserving valid owner access and existing edits` |
| Installation trouble | `/security-harness:doctor diagnose missing commands without modifying settings` |

Use your preferred language. Narrow a request by naming the service, comparison
branch, risk or finding. Say "review and fix" if you want implementation too.

## What a useful result looks like

A review identifies the actual source version and scope, gives reachable paths
and code evidence for findings, checks counterevidence and lists unreviewed areas.
"No supported findings in this scope" is valid; it does not mean the entire
application is secure. Findings are separate from hardening suggestions.

An implemented fix is not automatically a verified fix. Expect an observed denial
case, legitimate positive control, side-effect assertions and actual test results.
If tests cannot run, expect a blocker and a concrete next step, not a green label.
See the [report template](../skills/review/references/report-template.md).

## Working with a team

Keep application code and review artifacts separate. Share a redacted report with
source revision, scope, assumptions and reproduction steps. Do not commit customer
data or credentials in reports. A project-scoped plugin install can be shared with
collaborators; do not silently alter their settings. For reproducibility record
the plugin version and model/session conditions; updates can change behavior.

Use [evaluation exercises](../evals/README.md) before treating the harness as a
team quality gate. A human owner decides whether unresolved risks are acceptable.
No automated prompt checklist certifies security or compliance.
