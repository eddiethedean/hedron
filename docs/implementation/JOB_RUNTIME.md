# Job interaction implementation

## Ownership

Hedron defines status and interaction protocols; applications select and operate the durable
backend. A built-in in-memory object is a conformance test double only and is never advertised as a
multi-worker durable backend.

## State and security

Status records contain opaque identity, state, bounded progress/message metadata, timestamps,
expiry, attempts, and redacted terminal result/error references. Authorization and tenant scope are
checked on submission and every status/cancellation read. Idempotency is explicit and scoped.

## Interaction

HTTP 202 returns the authorized status URL, `Retry-After`, and a bounded-polling component. Polling
stops on terminal/expired states, backs off within documented limits, and preserves ordinary HTML,
focus, live-region, cache, and CSRF behavior. Optional SSE is a replaceable observation transport,
not a different job state model.

## Verification

Run protocol, state-machine, replay, forged-ID, cross-tenant, retry, expiry, cancellation-request,
backend-degradation, accessibility, and adapter HTTP tests against the test double and at least one
external conformance implementation.
