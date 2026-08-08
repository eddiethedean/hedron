# Hedron `v0.25` production archetype and landmine quarantine acceptance

Phase 0.25 hardens a reference production archetype, adds load/perf budget evidence for
critical paths, quarantines or finishes specialty extras landmines, documents the
Matplotlib charts default / Plotly–Altair graduation path, and requires SBOM/evidence
attach on train tags. Evidence is indexed by
[`release-gate-0.25.toml`](release-gate-0.25.toml).
**Zero Deferred:** every 0.25-owned gate row must be Verified at cut.

Owning decision: [D-053](../DECISIONS.md). RFC:
[RFC-0056](../rfcs/RFC-0056-PRODUCTION-QUALITY.md).
Program summary: [production-quality guide](../guides/production-quality.md).

## Spec packet

- [x] ROADMAP §0.25 scope accepted; D-053 / RFC-0056 recorded.
- [x] Gate checker recognizes `0.25`
  (`python scripts/check_release_gate.py 0.25.0 --allow-planned`).
- [ ] `ARCHETYPE-025` / `BUDGET-025` / `EXTRAS-025` / `CHARTS-025` / `SUPPLY-025` Verified.
- [ ] `REGRESS-025` / `PKG-025` at cut.

## Exit

- [ ] Every 0.25-owned release-gate row is `Verified`.
- [ ] Production-quality and production-readiness guides link the archetype.
