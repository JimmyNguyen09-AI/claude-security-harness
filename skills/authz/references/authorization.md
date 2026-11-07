# Authorization audit

Construct a matrix from intended product rules:

`subject × action × resource × tenant × context -> allow/deny`

Include unauthenticated, owner, same-tenant non-owner, same-tenant admin,
cross-tenant member/admin, revoked/disabled account and service identity where
applicable. Tenant admin is not automatically a platform admin. Label inferred
rules rather than presenting them as product requirements.

Trace identity derivation and tenant selection: tokens, headers, URL/body fields,
session data, middleware, ORM filters and database row-level security. Never trust
a client-supplied tenant/owner/role without server-side authorization.

Check direct and indirect paths:

- Single-object reads and updates; nested resources and parent/child mismatch.
- List, search, count, export, download, bulk and GraphQL field resolvers.
- Sensitive field updates and mass assignment (role, owner, tenant, approval state).
- Jobs, webhooks, caches, subscriptions, signed URLs and delegated service calls.
- Invite acceptance, membership transfer, role changes and revocation.
- Policy changes between check and use; stale cache/session authority.

For each candidate ask whether an upstream or downstream guard actually covers
this exact path. If policy lives outside the available source, mark the finding
inconclusive or conditional. Tests should use at least two tenants and multiple
roles, check both absence of disclosure and side effects, and preserve valid
authorized behavior after remediation.
