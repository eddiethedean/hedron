# Hedron `v0.30` dual-package Workbench extraction acceptance

Phase 0.30 ships **production-grade `fastapi-workbench` `1.0.0`** for plain FastAPI
Workbench deployment and **`hedron-workbench` `0.30.0`** as a thin Hedron specialization
that delegates generic resolver, middleware, and runner behavior.
The Supported surface spans both packages under the declared inventories.
Baseline: Published **`v0.29.0`**. Evidence is indexed by
[`release-gate-0.30.toml`](release-gate-0.30.toml).
**Zero Deferred:** every 0.30-owned gate row must be Verified at cut.

Owning decision: [D-058](../DECISIONS.md). RFC:
[RFC-0063](../rfcs/RFC-0063-FASTAPI-WORKBENCH-EXTRACTION.md).
Tracking: [#135](https://github.com/eddiethedean/hedron/issues/135).
Packet SSOT:
[production-grade-inventory-030.toml](production-grade-inventory-030.toml) ·
[upgrade-fixtures-030.md](upgrade-fixtures-030.md) ·
[fastapi-workbench-provenance-030.toml](fastapi-workbench-provenance-030.toml) ·
[security-review-030/](security-review-030/).

## Entry criteria

- [x] Tip/SSOT honesty for Published `0.29.0`
- [x] Owning RFC-0063 / D-058 Accepted
- [x] Machine-readable inventory draft (Supported / Experimental / excluded) for both packages
- [x] Tracking issue #135
- [x] Upgrade-fixture plan sketched (`upgrade-fixtures-030.md`)

## Spec packet

- [x] ROADMAP §0.30 scope; D-058 / RFC-0063 recorded
- [x] Gate checker recognizes `0.30` evidence manifest
- [x] Per-gate checkers Verified at cut
- [x] `REALWB-030` redacted RESULT.log against pinned `posit/workbench` image
- [x] `REGRESS-030` / `PKG-030` at cut

## Out of 0.30

- Flask / Django / WSGI support in `fastapi-workbench`
- Vendoring or duplicating generic Workbench implementation inside `hedron-workbench`
- Auto-activation on install, import, or `RS_SERVER_URL`
- Bundling `rserver-url`
- Posit Connect publishing/operations as Supported
- Treating Workbench auth as Hedron identity
- Scheduling Hedron `1.0` / SLA / certification
- Treating `fastapi-workbench` `1.0.0` as Hedron `1.0`

## Exit

- [x] Every 0.30-owned release-gate row is `Verified`
- [x] Production-grade label used only for declared Supported inventory per package
- [x] Workbench trust-boundary review + disposition ledger attached
- [ ] Close #135 (after tag)
