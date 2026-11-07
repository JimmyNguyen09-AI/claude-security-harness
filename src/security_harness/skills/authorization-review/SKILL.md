---
name: authorization-review
description: Review object, field, function and tenant authorization against an explicit intended access policy.
---

Trace entry point, authentication, authorization, service and database controls.
Keep intended permissions separate from observed behavior. If intended policy is
missing, record that gap rather than treating existing behavior as the requirement.

For each sensitive operation compare subject, action, resource, tenant and context.
Check list/search/export/bulk endpoints, nested IDs, ownership changes, protected
fields, jobs acting for users, revoked sessions and cached permissions. Follow
actual middleware and database defenses before claiming a missing check.

Propose both a denied case and a legitimate allowed case. Assert absence of leaked
data and unauthorized state changes, not just the HTTP status. Quote exact code.
Do not mark any issue reproduced without a separate trusted runtime artifact.
