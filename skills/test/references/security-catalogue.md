# Security coverage catalogue

This is a broad routing catalogue, not a guarantee of exhaustive tests. For every
surface, record applicable/not-applicable/unknown for each domain and why. Choose
test depth from exposure, privilege, data impact and change history. WSTG and ASVS
provide external requirement references; map to a pinned version when claiming a
specific control, and never invent compliance IDs.

| Domain ID | Threats / cases | Primary oracle |
|---|---|---|
| authentication | Login/reset/MFA/session lifecycle, replay, logout, revocation | Identity cannot be forged or retained after revocation |
| authorization | Object/field/function permissions, IDOR, mass assignment, bulk/export | Unauthorized data and side effects absent; legitimate access works |
| tenant-isolation | Cross-tenant IDs, queries, cache keys, files, events, indexes | No cross-tenant read/write/inference under relevant roles |
| injection | SQL/NoSQL/command/template/code, deserialization | Untrusted data never changes query/code semantics |
| browser | XSS, CSRF, CORS, clickjacking, cookies, DOM sinks | Origins and output encoding enforce intended boundary |
| network | SSRF, redirects, DNS rebinding, proxy trust, egress | Approved destination/identity after every resolution/redirect |
| files | Traversal, archive extraction, symlinks, upload content/type/size | Access stays within authorized namespace; no executable upload path |
| crypto-secrets | Token signing/claims, randomness, key rotation, TLS, secrets | Correct authenticity/confidentiality; secret values not exposed |
| data-privacy | Response/log/export minimization, deletion, retention, backups | Intended data visibility and lifecycle across storage layers |
| business-logic | Workflow bypass, replay, price/quantity/state manipulation | Business invariants preserved across multi-step sequences |
| concurrency | Check/use races, double spend, duplicate delivery, retries | Atomicity/idempotency under controlled interleavings |
| resilience | Partial failures, timeouts, fail-open, rollback, resource bounds | Safe failure and recovery without privilege/data-integrity loss |
| api-protocols | REST/GraphQL/WebSocket/RPC, parsing ambiguity, schema drift | Authentication/authorization across all methods and transports |
| infrastructure | Cloud IAM, storage ACL, container/K8s config, CI/CD privileges | Least privilege and boundary configuration match intended deployment |
| supply-chain | Lockfiles, advisories, build scripts, artifact integrity, updates | Reviewed provenance and dependency risk; no untrusted execution |
| detection-response | Audit events, sensitive log redaction, alert delivery, tampering | Critical events observable with safe, attributable evidence |
| agent-security | Prompt injection, tool escalation, poisoned memory/RAG, exfiltration | Untrusted content cannot authorize tools/data access or change policy |
| memory-safety | Buffer bounds, use-after-free, integer overflow, unsafe/FFI boundaries | No memory corruption or invalid ownership across adversarial inputs |

## Test layers

- Static: trace code/configuration and effective controls, including infrastructure
  evidence where available. Never infer runtime exposure solely from a source default.
- Unit/property: ownership/tenant combinations, parsers, boundary values, invariant
  preservation and mutation controls. Prefer property-based testing when installed.
- Integration/contract: gateway -> service -> DB; service -> queue -> consumer;
  cloud/storage identity and tenancy. Include revoked identity and stale contracts.
- End-to-end: legitimate and denied flows across UI/API/worker effects.
- Stateful/fault/concurrency: bounded seeded sequences and deterministic schedules.
- Dynamic scanner/fuzzing: local or authorized staging with resource limits,
  reproducible seeds, minimized cases and independently checked findings.
- Post-fix: original failure case plus valid workflows and adjacent variants.

Plan for multiple identities/tenants, empty/malformed/oversize inputs, repeated and
out-of-order requests, race timing and dependency faults. Distinguish a crafted
test input from evidence of a remotely exploitable defect. Do not fuzz an unknown
public host or use real leaked secrets as test credentials.
