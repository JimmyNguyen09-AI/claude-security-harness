---
name: authz
description: Audit authentication and authorization paths, especially ownership, field permissions, tenant boundaries and revoked access.
---

Audit the requested scope in this Claude Code session: $ARGUMENTS

Read [authorization checks](references/authorization.md) and the shared
[report contract](../review/references/report-contract.md). Use existing tools and
session authentication; no SDK, API key or Docker prerequisite for source analysis.

Map subject, action, resource, tenant and context. Separate intended policy from
current behavior. Trace all enforcement layers and alternative paths before
claiming bypass. Include at least one legitimate allow case and relevant denial
cases per sensitive operation. Check data returned and state changes, not just
HTTP codes. Review-only by default; follow existing authorization if fixes are
already requested. Record unavailable tests/tooling instead of inventing results.
