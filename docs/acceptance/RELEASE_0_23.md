# Hedron `v0.23` stable-tier expansion acceptance

Phase 0.23 expands the compatibility-protected `stable` API tier for a **narrow
curated** Supported CRUD/admin happy path (beginner facade, regions/`swap`,
Poll/job helpers, security profile ergonomics / `CsrfField`+`Form`+`Hx`, testing
helpers) without promoting Alpha extras, `hedron[data]`, or experimental live
transports. Evidence is indexed by [`release-gate-0.23.toml`](release-gate-0.23.toml).
**Zero Deferred:** every 0.23-owned gate row must be Verified at cut.

Owning decision: [D-053](../DECISIONS.md). RFC:
[RFC-0056](../rfcs/RFC-0056-PRODUCTION-QUALITY.md).
Program summary: [production-quality guide](../guides/production-quality.md).

**Locked allowlist:** [ROADMAP §0.23](../ROADMAP.md) ·
[STABLE_FACADE.md](../api/STABLE_FACADE.md) ·
[STABILITY expanded tier](../api/STABILITY.md#expanded-stable-tier-023).

## Spec packet

- [x] ROADMAP §0.23 scope accepted; D-053 / RFC-0056 recorded.
- [x] Packet refine: locked promotion + exclude tables; distinct gate commands.
- [x] Gate checker recognizes `0.23` evidence manifest; pre-cut packet verify:
  `python scripts/verify_pkg_23.py --allow-planned`.
- [x] Facade inventory + checkers:
  `python scripts/check_stable_facade.py`,
  `python scripts/check_stable_tier_023.py`.
- [ ] `STABLE-023` / `FACADE-023` / `INVENTORY-023` **Verified** (promote symbols in
  STABILITY package tables; flip gate states).
- [ ] `REGRESS-023` / `PKG-023` at cut
  (`bash scripts/ci_checks.sh test --python 3.12`,
  `python scripts/verify_pkg_23.py` without `--allow-planned` after version bump).

## Out of 0.23

- Live SSE/WS/stream/preload (`job_status_sse_response`, …) → **0.24**
- Alpha charts/notebook/MCP/Gradio/native; `hedron[data]` / dashboards / inference
- Package GA / scheduled `1.0`; human AT as stability evidence

## Exit

- [ ] Every 0.23-owned release-gate row is `Verified`.
- [ ] What’s ready, STABILITY, STABLE_FACADE, and production-quality docs agree on the
  expanded tier.
