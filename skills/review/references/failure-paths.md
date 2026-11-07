# Security-relevant failure paths

Start with an invariant and a concrete failure/interleaving. Check:

| Trigger | Invariant to verify |
|---|---|
| Auth service/DB/cache timeout | Access is not granted on error |
| External request succeeds but local commit fails | Retry cannot duplicate the effect |
| Two requests read the same state | Quota, balance and ownership cannot be bypassed |
| Worker retries or message redelivery | Processing is idempotent across consumers |
| Transaction partially fails | Protected state is rolled back or compensated |
| Session/role revoked | Cache and queued work do not preserve unintended authority |
| Exception returned/logged | No secrets, tokens or sensitive payloads leak |
| Long/unbounded input | Time, memory, query count and request size are bounded |

Trace actual ordering and isolation level. Avoid declaring a race merely because
there are multiple statements: database constraints, locks or idempotency keys may
already enforce the invariant. Propose deterministic scheduling/fault injection.
For denied operations, assert absence of side effects in addition to status codes.
