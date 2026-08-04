---
status: implemented
---

# Job interaction contracts


!!! note "Stability (0.8 freeze)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Target:** phase 0.7E.

`JobBackend` is a protocol over application-operated durable work. Hedron does not ship a queue,
worker fleet, scheduler, result database, or retry service.

## Contract

A backend declares capabilities and supports explicit submission, status lookup, result/error
metadata, retention/expiry, and cancellation requests where available. Submission carries an
application-defined task description, authorization/tenant scope, and optional idempotency key.
Job identifiers are opaque, bounded, and safe for addressable status URLs.

The portable state model distinguishes queued, running, succeeded, failed, cancellation-requested,
cancelled, and expired outcomes. Retry ownership, maximum attempts, result serialization, cleanup,
and backend-unavailable behavior are explicit backend/application policies.

## HTTP and HTMX behavior

Accepted work returns HTTP 202 with an addressable authorized status resource and `Retry-After`.
The default component uses bounded polling, accessible status announcements, terminal stop behavior,
and a useful ordinary-HTML fallback. An optional SSE transport may observe the same status contract
only after its independent asset/security/conformance gate; polling remains the required baseline.

Host-framework background helpers are limited to small post-response work and do not implement the
durable protocol.
