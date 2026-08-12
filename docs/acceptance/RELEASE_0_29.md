# Hedron `v0.29` production-grade Workbench adapter acceptance

Phase 0.29 ships **production-grade `hedron-workbench`** for the declared
Supported inventory under the 0.26+ package contract.
The Supported surface includes `HedronWorkbench`, inactive Hedron parity,
resolved launcher handoff, and exactly-one normalization.
Baseline: Published **`v0.28.2`**. Evidence is indexed by
[`release-gate-0.29.toml`](release-gate-0.29.toml).
**Zero Deferred:** every 0.29-owned gate row must be Verified at cut.

Owning decision: [D-057](../DECISIONS.md). RFC:
[RFC-0062](../rfcs/RFC-0062-POSIT-WORKBENCH-ADAPTER.md).
Tracking: [#134](https://github.com/eddiethedean/hedron/issues/134).
Packet SSOT:
[production-grade-inventory-029.toml](production-grade-inventory-029.toml) ·
[upgrade-fixtures-029.md](upgrade-fixtures-029.md) ·
[fastapi-workbench-provenance-029.toml](fastapi-workbench-provenance-029.toml) ·
[security-review-029/](security-review-029/).

## Entry criteria

- [x] Tip/SSOT honesty for Published `0.28.2`
- [x] Owning RFC-0062 / D-057 Accepted
- [x] Machine-readable inventory draft (Supported / Experimental / excluded)
- [x] Tracking issue #134
- [x] Upgrade-fixture plan sketched (`upgrade-fixtures-029.md`)

## Spec packet

- [x] ROADMAP §0.29 scope; D-057 / RFC-0062 recorded
- [x] Gate checker recognizes `0.29` evidence manifest
- [x] Per-gate checkers Verified at cut
- [x] `REALWB-029` redacted RESULT.log against pinned `posit/workbench` image
- [x] `REGRESS-029` / `PKG-029` at cut

## Out of 0.29

- Flask / Django / WSGI support
- Vendoring or depending on `fastapi-workbench`
- Auto-activation on install, import, or `RS_SERVER_URL`
- Bundling `rserver-url`
- Posit Connect publishing/operations as Supported
- Treating Workbench auth as Hedron identity
- Scheduling `1.0` / SLA / certification

## Exit

- [x] Every 0.29-owned release-gate row is `Verified`
- [x] Production-grade label used only for declared Supported inventory
- [x] Workbench trust-boundary review + disposition ledger attached
- [ ] Close #134 (after tag)
