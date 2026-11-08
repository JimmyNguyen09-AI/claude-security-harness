# Security review — [target]

> Template only. Replace placeholders with observations; delete unused sections.
> Do not fabricate findings or execution evidence to fill this report.

## Scope and outcome

- Source: [commit; included dirty/untracked paths; snapshot identity]
- Plugin/session: [plugin version, model if known, same/separate session]
- Goal/profile: [focused / standard / campaign / verify-fix]
- Boundaries examined: [entry points → guards → operations → sinks]
- Summary: [supported findings / unresolved candidates / scope limits]
- Execution: [static only / tests executed; environment]

## Findings

### [stable ID] — [concrete violated invariant]

- Severity: [critical/high/medium/low; impact and preconditions supporting rating]
- Evidence status: [supported statically / reproduced / inconclusive]
- Source: [file:line and relevant exact code]
- Actor and path: [attacker privileges → reachable operation → sensitive effect]
- Intended rule and impact: [what should hold; observed or inferred consequence]
- Counterevidence: [real controls checked; why they do/do not prevent the path]
- Remediation: [smallest enforcement change; compatibility constraints]
- Regression: [negative case, valid positive control, forbidden side effects]
- Observations: [executed command/results/artifact, or explicitly not run]

## Candidate dispositions

| ID | Supported / rejected / inconclusive | Evidence or missing premise |
|---|---|---|
| [ID] | [disposition] | [do not silently discard a candidate] |

## Tests and coverage

| Surface/invariant | Mode | Planned / passed / failed / blocked / not run | Evidence and limitation |
|---|---|---|---|
| [boundary] | [source/runtime] | [actual state] | [artifact or reason] |

Report test results separately from vulnerability conclusions. A failing test
may be a setup error. A denied request alone does not establish correct policy.

## Next action

[Highest-value repair or missing verification, owner if known, prerequisites.]
List excluded surfaces and unresolved policy questions. A clean result is scoped;
do not state that the application is secure or certified.
