# Hedron `v0.26` production-grade core / FastAPI / Explorer acceptance

Phase 0.26 graduates `hedron-core`, `hedron`, and `hedron-explorer` to
**production-grade for the declared Supported CRUD/admin surface** under the
0.26+ package contract. Baseline: Published **`v0.25.2`**. Evidence is indexed by
[`release-gate-0.26.toml`](release-gate-0.26.toml).
**Zero Deferred:** every 0.26-owned gate row must be Verified at cut.

Owning decision: [D-054](../DECISIONS.md). RFC:
[RFC-0057](../rfcs/RFC-0057-PRODUCTION-GRADE-CORE.md).
Packet SSOT:
[production-grade-inventory-026.toml](production-grade-inventory-026.toml) ·
[upgrade-fixtures-026.md](upgrade-fixtures-026.md) ·
[security-review-026/](security-review-026/).

## Entry criteria

- [x] Tip/SSOT honesty for Published `0.25.2`
- [x] Owning RFC-0057 / D-054 Accepted
- [x] Machine-readable inventory draft (Supported / Experimental / excluded)
- [x] Upgrade-fixture plan sketched (`upgrade-fixtures-026.md`)

## Spec packet

- [x] ROADMAP §0.26 scope; D-054 / RFC-0057 recorded
- [x] Gate checker recognizes `0.26` evidence manifest:
  `python scripts/check_release_gate.py 0.26.0`
  (or `python scripts/verify_pkg_26.py`)
- [x] Per-gate checkers Verified at cut:
  `check_contract_026.py`, `check_core_026.py`, `check_fastapi_026.py`,
  `check_explorer_026.py`, `check_review_026.py`, `verify_pkg_26.py`
- [x] `CONTRACT-026` / `CORE-026` / `FASTAPI-026` / `EXPLORER-026` / `REVIEW-026` Verified
- [x] `REGRESS-026` / `PKG-026` at cut

## Out of 0.26

- Promoting SSE / WebSocket / streaming / preload
- Graduating every Beta/experimental core symbol
- Public-by-default Explorer
- `1.0` / SLA / certification
- Production-grade claims for data / Flask / Django / charts / MCP / Gradio (later phases)

## Exit

- [x] Every 0.26-owned release-gate row is `Verified`
- [x] Production-grade label used only for declared Supported inventory
- [x] Redacted security review + disposition ledger attached
