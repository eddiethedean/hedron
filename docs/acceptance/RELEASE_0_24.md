# Hedron `v0.24` live-transport production disposition acceptance

Phase 0.24 ends the permanent experimental-live fog: either prove multi-engine browser
and load/proxy backpressure evidence so SSE/WebSocket can graduate under documented ops
constraints, **or** formally document polling-only as the Supported production story.
Evidence is indexed by [`release-gate-0.24.toml`](release-gate-0.24.toml).
**Zero Deferred:** every 0.24-owned gate row must be Verified at cut.
Exactly one disposition may be Accepted — do not half-verify both.

Owning decision: [D-053](../DECISIONS.md). RFC:
[RFC-0056](../rfcs/RFC-0056-PRODUCTION-QUALITY.md).
Prior Deferred IDs in scope: `BROWSER-10-001`, `PERF-10-001`, `LIVE-011-BROWSER`.

## Spec packet

- [x] ROADMAP §0.24 scope accepted; D-053 / RFC-0056 recorded.
- [x] Gate checker recognizes `0.24`
  (`python scripts/check_release_gate.py 0.24.0 --allow-planned`).
- [ ] `DECIDE-024` disposition written and mirrored in What’s ready / STABILITY.
- [ ] `BROWSER-024` / `PERF-024` / `DOCS-024` Verified for the chosen disposition.
- [ ] `REGRESS-024` / `PKG-024` at cut.

## Exit

- [ ] Every 0.24-owned release-gate row is `Verified`.
- [ ] Prior Deferred live-ops IDs have a terminal owner note.
