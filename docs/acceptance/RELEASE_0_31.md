# Hedron `v0.31` tooling + Streamlit migrator acceptance

Phase 0.31 ships **production-grade developer and portable conformance tooling**
(`hedron-conformance`, `hedron-sample-kit`, `hedron-sim`, `hedron-notebook`,
Node/Java evaluators) and the flagship CLI assistant
**`hedron migrate streamlit`**.
Tooling-grade does not convert these into application production servers.
Baseline: Published **`v0.30.0`**. Evidence is indexed by
[`release-gate-0.31.toml`](release-gate-0.31.toml).
**Zero Deferred:** every 0.31-owned gate row must be Verified at cut.

Owning decision: [D-059](../DECISIONS.md). RFCs:
[RFC-0064](../rfcs/RFC-0064-PRODUCTION-GRADE-TOOLING.md) (tooling) ·
[RFC-0061](../rfcs/RFC-0061-STREAMLIT-AST-MIGRATOR.md) (migrator).
Tracking: [#87](https://github.com/eddiethedean/hedron/issues/87) (tooling),
[#88](https://github.com/eddiethedean/hedron/issues/88) (`MIGRATE-031`).
Packet SSOT:
[production-grade-inventory-031.toml](production-grade-inventory-031.toml).

## Entry criteria

- [x] Tip/SSOT honesty for Published `0.30.0`
- [x] Owning RFC-0064 / RFC-0061 / D-059 Accepted
- [x] Machine-readable inventory draft (Supported / Experimental / excluded)
- [x] Tracking issues #87 and #88 renumbered to phase 0.31 / `*-031` gates
- [ ] Per-gate checker scripts implemented (`scripts/check_*_031.py`)
- [ ] Upgrade-fixture plan for tooling + migrator corpus

## Spec packet

- [x] ROADMAP §0.31 scope; D-059 / RFCs recorded
- [x] Gate checker recognizes `0.31` evidence manifest
- [ ] Per-gate checkers Verified at cut
- [ ] `MIGRATE-031` no-drop mapping corpus + security/a11y/perf/adversarial evidence
- [ ] `REGRESS-031` / `PKG-031` at cut

## Out of 0.31

- Hosted multi-user notebook service
- Node/Java evaluators as full Hedron ports or application servers
- Claiming `hedron-sim` emulates all browser/HTMX behavior
- Making sample-kit a required runtime dependency
- Streamlit call-for-call parity, executing source apps by default, silent state copy
- Treating generated migrator output as production-ready without review/cutover evidence
- Graduating MCP or Gradio
- Scheduling Hedron `1.0` / SLA / certification

## Cut verify

During packet refine (living tip still `0.30.x`):

```bash
uv run python scripts/verify_pkg_31.py --allow-planned
```

At `v0.31.0` cut (packages on the 0.31 train; every evidence row Verified):

```bash
uv run python scripts/verify_pkg_31.py
uv run python scripts/check_release_gate.py 0.31.0 --execute-verified
```

## Exit

- [ ] Every 0.31-owned release-gate row is `Verified`
- [ ] Production-grade / tooling-grade labels used only for declared Supported inventory
- [ ] Close #87 and #88 (after tag)
