---
name: failure-path-review
description: Inspect security-relevant error handling, transaction boundaries, retries and concurrent state changes.
---

State the invariant first: what must remain true when a dependency fails, a request
is retried, a timeout occurs or two operations overlap? Trace side effects in order.
Look for fail-open authorization, partial writes, swallowed exceptions, missing
rollback, duplicate external effects and stale check-before-use decisions.

Distinguish an operational inconvenience from a confidentiality, integrity or
availability impact. Explain the required interleaving or failure point. Propose
fault injection or deterministic concurrency tests. Missing tests are a coverage
gap, not evidence of a defect. Never invent runtime results.
