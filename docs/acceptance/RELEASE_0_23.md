# Hedron `v0.23` stable-tier expansion acceptance

Phase 0.23 expands the compatibility-protected `stable` API tier for the Supported
CRUD/admin happy path (beginner facade, regions/`swap`, Poll/job helpers, security
profile names) without promoting Alpha extras or experimental live transports.
Evidence is indexed by [`release-gate-0.23.toml`](release-gate-0.23.toml).
**Zero Deferred:** every 0.23-owned gate row must be Verified at cut.

Owning decision: [D-053](../DECISIONS.md). RFC:
[RFC-0056](../rfcs/RFC-0056-PRODUCTION-QUALITY.md).
Program summary: [production-quality guide](../guides/production-quality.md).

## Spec packet

- [x] ROADMAP §0.23 scope accepted; D-053 / RFC-0056 recorded.
- [x] Gate checker recognizes `0.23`
  (`python scripts/check_release_gate.py 0.23.0 --allow-planned`).
- [ ] `STABLE-023` / `FACADE-023` / `INVENTORY-023` Verified.
- [ ] `REGRESS-023` / `PKG-023` at cut.

## Exit

- [ ] Every 0.23-owned release-gate row is `Verified`.
- [ ] What’s ready, STABILITY, and production-quality docs agree on the expanded tier.
