# Engagement profiles

Infer the smallest profile that covers the user's actual request. Profiles control
work size, not severity thresholds. The user can override scope at any time.

| Profile | Entry condition | Required output | Stop condition |
|---|---|---|---|
| Focused | PR, diff, named bug or module | Changed-boundary map, traced findings, counterevidence, regression suggestions | Requested paths and affected protections examined; name remaining uncertainty |
| Standard | First repository review | Inventory, prioritized sensitive flows, source evidence, coverage gaps | First meaningful group of risk boundaries reviewed; propose concrete continuation |
| Campaign | Monorepo, multiple services, repeated sessions | Work packages, cross-service contracts, ledger/checkpoints, evidence freshness | Only completed when scoped packages and applicable checks have evidence; otherwise incomplete |
| Verify/fix | Existing candidates or repair request | One disposition per candidate, minimal patches if authorized, test evidence | Every candidate accounted for; distinguish implemented from behaviorally verified |

## Scope card

Keep this short enough to fit in a progress update:

- Target: repository and version; dirty/untracked paths included.
- Goal: user intent and selected profile.
- Priority: first entry point, sensitive asset and invariant.
- Execution: source-only / local tests authorized / remote scope recorded.
- Budget: requested time or work-package limit, if any; remaining work tracked.
- Output: chat by default; agreed artifact directory for persistent campaigns.

## Managing large projects

Create a component inventory before launching detailed review. Group by trust
boundary rather than file count. Include shared identity libraries, gateways,
queues, data stores, admin tools and integration contracts. Keep a risk queue with
reason, evidence needed, owner and state. Process highest-impact reachable flows
first. Do not read every generated file or load every reference into context.

After changing a shared dependency, invalidate evidence for its consumers. Before
ending a session save source identity, decisions, rejected hypotheses, open work,
test limitations and exact next step. Do not start new work packages when the
remaining budget cannot support verification and checkpointing. Report incomplete
coverage explicitly; do not convert budget exhaustion to a clean audit.

A standard review is not a release certification. The campaign ledger remains
the machine-readable contract when requested; this scope card does not replace it.
