# Hedron `v0.27` production-grade satellites acceptance

Phase 0.27 graduates `hedron-data`, `hedron-flask`, `hedron-django`,
`hedron-jinja`, and `hedron-extras` to **production-grade for the declared
Supported inventories** under the 0.26+ package contract. Baseline: Published
**`v0.26.0`**. Evidence is indexed by
[`release-gate-0.27.toml`](release-gate-0.27.toml).
**Zero Deferred:** every 0.27-owned gate row must be Verified at cut.

Owning decision: [D-055](../DECISIONS.md). RFC:
[RFC-0058](../rfcs/RFC-0058-PRODUCTION-GRADE-SATELLITES.md).
Packet SSOT:
[production-grade-inventory-027.toml](production-grade-inventory-027.toml) ·
[upgrade-fixtures-027.md](upgrade-fixtures-027.md).

## Entry criteria

- [x] Tip/SSOT honesty for Published `0.26.0`
- [x] Owning RFC-0058 / D-055 Accepted
- [x] Machine-readable inventory draft (Supported / Experimental / excluded)
- [x] Upgrade-fixture plan sketched (`upgrade-fixtures-027.md`)

## Spec packet

- [x] ROADMAP §0.27 scope; D-055 / RFC-0058 recorded
- [x] Gate checker recognizes `0.27` evidence manifest:
  `python scripts/check_release_gate.py 0.26.1 --evidence-manifest docs/acceptance/release-gate-0.27.toml --allow-planned`
  (or `python scripts/verify_pkg_27.py --allow-planned`)
- [ ] Per-gate checkers Verified at cut (Planned until implementation):
  `check_data_027.py`, `check_flask_027.py`, `check_django_027.py`,
  `check_hdj_027.py`, `check_extras_027.py`, `check_parity_027.py`,
  `verify_pkg_27.py`
- [ ] `DATA-027` / `FLASK-027` / `DJANGO-027` / `HDJ-027` / `EXTRAS-027` /
  `PARITY-027` Verified
- [ ] `REGRESS-027` / `PKG-027` at cut

## Out of 0.27

- Promoting SSE / WebSocket / streaming / preload
- Graduating `experimental-ui`, CodeEditor runtime, specialty bridges
- Making Explorer audit durable (`REV-026-003`)
- Graduating charts / native / MCP / Gradio / conformance tooling
- `1.0` / SLA / certification

## Exit

- [ ] Every 0.27-owned release-gate row is `Verified`
- [ ] Production-grade label used only for declared Supported inventory
- [ ] Satellite trust-boundary review + disposition ledger attached
