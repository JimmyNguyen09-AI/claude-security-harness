# Starting traces by project type

These are investigation recipes, not framework-specific vulnerability claims.
Confirm the actual stack from manifests and source. Read current primary framework
documentation when behavior depends on version. Authentication, validation and
authorization are separate controls; follow each to its enforcement point.

| Project | First end-to-end traces | Counterevidence to seek | Behavioral checks when authorized |
|---|---|---|---|
| Web frontend + API | Browser request → server route/action → service → storage → serializer | Server-side enforcement, output encoding, middleware matching, safe redirect/origin rules | Direct calls bypassing UI, owner/non-owner, protected fields, cookie/origin behavior |
| Multi-tenant SaaS | Session → tenant membership → object lookup → export/cache/worker | Tenant-scoped DB policy, object ownership, membership revocation, role hierarchy | Tenant A/B, same-tenant non-owner, valid admin, cache warm-up across identities |
| Python/Java/Go/.NET backend | Router → auth filter/dependency → handler → transaction | Alternate routes and methods, parameter binding, DB constraints and central policy | Missing credentials, invalid types, direct service calls, rollback and valid writes |
| Queue/event system | Producer identity → message → consumer → external effect → acknowledgement | Consumer authorization, deduplication key scope, retry policy, transactional outbox | Redelivery, stale membership, timeout after success, forged tenant, deterministic races |
| Payments/business workflows | User intent → price/entitlement calculation → provider → webhook → ledger | Server-derived values, signature verification, event/order binding, uniqueness | Duplicate/reordered events, cancelled/refunded state, authorized ordinary payment using stubs |
| File/network processing | User-controlled path/URL → normalization → resolver/open → output | Canonical path checks, redirects, address validation, archive boundaries, sandbox policy | Traversal variants, symlink/redirect changes, oversized input within agreed limits |
| AI agents/MCP/RAG | Untrusted content → model → proposed tool → policy broker → effect/memory | Deterministic permission enforcement, approval bound to final args, retrieval tenant filters | Canary leakage to mock sink, altered tool args, cross-tenant memory, authorized task control |
| CI/cloud/IaC | PR/source → build → credentials → artifact → deploy role | Trust separation, effective IAM, immutable dependencies, secret scoping | Static policy inspection first; live checks only with explicit target/limits |

For native/unsafe code and browser-dependent behavior, use the relevant
[test stack profiles](../../test/references/stack-profiles.md). Unit tests do not
establish browser or deployed IAM semantics. When a framework or stack is
unsupported, state the limitation and review its concrete boundaries; never
invent a scanner command or report a skipped test as passed.

## Find the shared cause

Trace alternate methods, bulk/list/export endpoints, workers and caches sharing
the same policy. Consolidate a root cause but preserve every confirmed affected
path. After repair, test both the original bypass and the alternate paths. Avoid
counting several symptoms of one missing guard as unrelated vulnerabilities.
