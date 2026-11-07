# Security policy

## Supported scope

Security fixes are considered for the latest `main` branch and latest 0.3.x version.
This experimental project has no guaranteed response or remediation SLA. Skills
are instructions, not an OS sandbox. Unit tests and ledger validation do not prove
security, exhaustive attack coverage or model behavior.

## Reporting a vulnerability

Use this repository's **Security -> Advisories -> Report a vulnerability** option
when private vulnerability reporting is enabled:

https://github.com/JimmyNguyen09-AI/claude-security-harness/security/advisories

If that option is unavailable, open a minimal issue asking the maintainer for a
private reporting channel. Do not include exploit details, private source, tokens,
customer data or confidential reports in a public issue while awaiting a channel.

Include the affected version, environment, impact, preconditions, a minimal
synthetic reproduction and suggested remediation if known. Redact all credentials
and identifying information. Explain whether observations came from live execution,
static review, a model response or a hypothetical scenario.

Potential issues include escaping helper file boundaries, incorrect passing gates,
unsafe execution defaults, permission escalation or accidental sensitive-data
disclosure. False-positive/false-negative skill behavior can also be reported;
describe the actual trust boundary and impact rather than claiming a sandbox escape
based only on model text.

## Authorized testing

Test only systems you own or have explicit authorization to assess. Use disposable
local environments, synthetic identities/data and bounded workloads. This project's
license grants rights to its code; it does not authorize testing third-party systems.
Do not validate a discovered real credential against a live service.

## Dependencies and releases

Scanner containers are optional, must be reviewed and pinned by digest, and remain
subject to their own licenses. Users should inspect skills, agents, helper commands
and permissions before enabling them. The project does not automatically install
tools, grant bypass permissions or publish model outputs to third parties.
