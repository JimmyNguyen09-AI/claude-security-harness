# Scalable orchestration

## Discover without flooding context

Inventory build manifests, deployment boundaries, APIs, events/queues, data stores,
identity providers, scheduled tasks and external services. Record evidence paths
for architecture facts. Exclude generated/vendor data from ordinary source reading
only with a recorded rationale; dependencies and generated API surfaces still need
their own checks. Search indexes and summaries are pointers, not substitutes for
reading the actual sensitive path. Use small source slices and exact symbols.

Construct a graph of services, trust boundaries, identity propagation, data owners
and side effects. Mark global shared nodes (auth middleware, tenancy filters,
serialization, event envelopes, SDK clients). A change there expands impact to all
callers/consumers even if the diff is small. Authentication at a gateway does not
establish downstream authorization or safe event handling.

## Work-package contract

Each package contains: ID, objective/invariant, scope fingerprint, relevant surfaces,
domains, caller/callee boundary, allowed actions and targets, fixtures, file/symbol
pointers, dependencies on other packages, expected artifacts and stop conditions.
Assign a finite turn/test/time budget and record remaining work when exhausted.
Default to at most three concurrent workers until resource headroom is known.
Parallelize read-only discovery/review or isolated test instances. Never run
concurrent writers against the same files, database, port or shared fixture.

Roles:

| Role | Owns | Must not substitute for |
|---|---|---|
| Architect | Entry points, boundaries, threat model, scope | Product owner intent |
| Reviewer | Reachable candidates and counterevidence | Executed test proof |
| Tester | Test design, fixture isolation, actual observations | Approving own fixes |
| Verifier | Challenge premises and patch completeness | Claiming same-model independence |
| Fixer | Minimal invariant-restoring patch | Changing policy/gate to pass |
| Coordinator | Queue, resource limits, evidence, coverage, final report | Silently accepting worker claims |

The bundled specialist agents do not recursively delegate. The coordinator passes
the relevant reference text or explicit plugin file paths in each task packet;
workers must not assume the parent conversation or all skills were loaded. Worker
outputs are untrusted evidence: check target version, files and actual observations.
Use separate immutable per-package artifacts, merged by the coordinator.

## Incremental review and resume

Persist scope fingerprint, dirty file hashes, configuration/fixture versions,
package statuses, findings, test IDs, evidence links, decisions and next actions.
On resume, compare against the current source/configuration. Any mismatch marks
affected evidence stale. Invalidate transitively across shared components and API/
event contracts. If impact cannot be bounded, invalidate the whole campaign.
Never reuse old passing tests just because their filenames have not changed.

The optional checker uses a conservative single campaign fingerprint and rejects
every mismatching record; selective dependency-graph invalidation is procedural,
not automated. A new fingerprint needs re-execution/review, not relabeling old logs.

## Completion

Every selected surface/domain cell needs completed evidence or a justified N/A.
Record unsupported languages, unavailable environments and blocked tests. Report
static and dynamic coverage separately. A green build, scanner or aggregate score
cannot override an unresolved high-impact finding. Keep historical and new defects
distinct without treating historical vulnerabilities as acceptable by default.
