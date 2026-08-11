# Hedron `v0.28` production-grade charts and native acceptance

Phase 0.28 graduates `hedron-charts` and `hedron-native` to **production-grade
for the declared Supported inventories** under the 0.26+ package contract.
Baseline: Published **`v0.27.0`**. Evidence is indexed by
[`release-gate-0.28.toml`](release-gate-0.28.toml).
**Zero Deferred:** every 0.28-owned gate row must be Verified at cut.

Owning decision: [D-056](../DECISIONS.md). RFC:
[RFC-0059](../rfcs/RFC-0059-PRODUCTION-GRADE-CHARTS-NATIVE.md).
Packet SSOT:
[production-grade-inventory-028.toml](production-grade-inventory-028.toml) ·
[upgrade-fixtures-028.md](upgrade-fixtures-028.md) ·
[security-review-028/](security-review-028/).

## Entry criteria

- [x] Tip/SSOT honesty for Published `0.27.0`
- [x] Owning RFC-0059 / D-056 Accepted
- [x] Machine-readable inventory draft (Supported / Experimental / excluded)
- [x] Upgrade-fixture plan sketched (`upgrade-fixtures-028.md`)

## Spec packet

- [x] ROADMAP §0.28 scope; D-056 / RFC-0059 recorded
- [x] Gate checker recognizes `0.28` evidence manifest:
  `python scripts/check_release_gate.py 0.28.0`
  (or `python scripts/verify_pkg_28.py`)
- [x] Per-gate checkers Verified at cut:
  `check_charts_028.py`, `check_interactive_028.py`, `check_native_028.py`,
  `check_supply_028.py`, `check_contract_028.py`, `verify_pkg_28.py`
- [x] `CHARTS-028` / `INTERACTIVE-028` / `NATIVE-028` / `SUPPLY-028` Verified
- [x] `REGRESS-028` / `PKG-028` at cut

## Out of 0.28

- Declaring all visualization backends Supported as a group
- Graduating Plotly / Altair / optional adapters to Supported
- Making native acceleration required for correctness
- CDN-loaded Supported chart runtimes
- MCP / Gradio / conformance tooling graduation
- `1.0` / SLA / certification

## Exit

- [x] Every 0.28-owned release-gate row is `Verified`
- [x] Production-grade label used only for declared Supported inventory
- [x] Charts/native trust-boundary review + disposition ledger attached
