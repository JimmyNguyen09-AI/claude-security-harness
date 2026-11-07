# Stack-specific test selection

Select only applicable layers and record exclusions; lack of a tool is blocked
coverage, not not-applicable. Reuse installed project frameworks instead of adding
a new scanner or framework by default. Define tests in the application's actual
runtime and protocols, not generic examples detached from deployment.

## Web / browser / API

Map every REST method, GraphQL resolver, WebSocket subscription and alternate API
version. Test server enforcement even when UI controls are hidden. Cover token
issuer/audience/expiry/signature, OAuth/OIDC state/nonce/redirect binding, session
rotation/revocation and reset flows as applicable. Browser tests need real origin,
cookie and navigation semantics; unit tests alone cannot establish CSRF/CORS safety.
Test bulk/list/export, field-level disclosure and schema/serializer drift.

## Multi-tenant SaaS

At least two tenants, owner/non-owner/admin/service identities and revoked users.
Trace tenant identity through DB query scopes, caches, search indexes, file keys,
background jobs and exports. Test nested resources, membership changes, delegated
operations and lifecycle deletion. Do not let privileged fixture setup credentials
leak into the request identity used for assertions.

## Distributed services and workers

Exercise missing/forged identity claims at service boundaries, event ordering,
redelivery, partial commit, timeout after external success, idempotency key scope,
consumer retries and dead-letter handling. Validate invariants under deterministic
interleavings and bounded load. Do not treat a successful upstream response as
proof of downstream authorization or exactly-once effects.

## Cloud, containers and CI/CD

Use effective configuration evidence for IAM, storage ACL, network paths, workload
identity, secret mounts, container privileges and deployment permissions. Analyze
untrusted PR/build scripts and provenance of actions/artifacts. Read-only config
review can proceed without cloud access; do not claim live permissions were tested
without an authorized environment. Do not change production IAM to test a theory.

## Native / unsafe code / parsers

Trace length/arithmetic checks, ownership and lifetime across C/C++/Rust unsafe/FFI
and serialization boundaries. Use existing sanitizer builds, bounded fuzz corpora
and minimized crash cases when available. Distinguish a crash from an exploitable
primitive and record runtime/compiler settings. Fuzzing with no crash proves only
the tested corpus/budget, not memory safety.

## AI-agent systems

Test model behavior and deterministic permission enforcement separately. Record
tool schema, broker policy, memory/retrieval tenant scope, approval binding and
actual tool events. Use mock exfiltration destinations and canaries. Multi-step
injection/memory/replay cases belong alongside authorized-task positive controls.

## Recovery and detection

Use disposable restore data to test confidentiality and tenancy after restore,
retention/deletion semantics, revoked credentials and audit continuity. Fault
injection should verify alert events and absence of sensitive payloads in logs.
Never trigger paging or real incident workflows without the agreed test scope.
