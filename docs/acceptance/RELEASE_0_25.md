# Hedron `v0.25` production archetype and landmine quarantine acceptance

Phase 0.25 hardens a reference production archetype, adds load/perf budget evidence for
critical paths, quarantines specialty extras landmines, documents the
Matplotlib charts default / Plotly–Altair graduation path, and requires SBOM/evidence
attach on train tags. Evidence is indexed by
[`release-gate-0.25.toml`](release-gate-0.25.toml).
**Zero Deferred:** every 0.25-owned gate row must be Verified at cut.

Owning decision: [D-053](../DECISIONS.md). RFC:
[RFC-0056](../rfcs/RFC-0056-PRODUCTION-QUALITY.md).
Program summary: [production-quality guide](../guides/production-quality.md).
Packet SSOT: [PRODUCTION_ARCHETYPE.md](../api/PRODUCTION_ARCHETYPE.md) ·
[extras-quarantine-025.toml](extras-quarantine-025.toml).

## Spec packet

- [x] ROADMAP §0.25 scope accepted; D-053 / RFC-0056 recorded.
- [x] Packet refine: locked Verified criteria; extras XOR contract; distinct gate commands.
- [x] Gate checker recognizes `0.25` evidence manifest against the living train:
  `python scripts/check_release_gate.py 0.25.0`
  (or `python scripts/verify_pkg_25.py`).
- [x] Per-gate checkers (cut):
  `python scripts/check_archetype_025.py`,
  `python scripts/check_budget_025.py`,
  `python scripts/check_extras_025.py`,
  `python scripts/check_charts_025.py`,
  `python scripts/check_supply_025.py`,
  `python scripts/verify_pkg_25.py`.
- [x] `ARCHETYPE-025` / `BUDGET-025` / `EXTRAS-025` / `CHARTS-025` / `SUPPLY-025` Verified.
- [x] `REGRESS-025` / `PKG-025` at cut
  (`bash scripts/ci_checks.sh test --python 3.12`,
  `python scripts/verify_pkg_25.py`).

## Out of 0.25

- Hosted SaaS / managed IdP; SLSA commercial attestation
- Finishing every specialty widget when quarantine wins
- D-053 P3 external security review / undated `1.0` DoD
- Human AT sessions (`SR-021` / …) remain Planned
- Alpha notebook / MCP / Gradio / `hedron-native` maturity
- Re-litigating live SSE/WS Supported claim (closed in 0.24)

## Exit

- [x] Every 0.25-owned release-gate row is `Verified`.
- [x] Production-quality and production-readiness guides link the archetype.
- [x] Extras XOR is `quarantine` (not `undecided`).
