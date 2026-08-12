# Hedron `v0.32` production-grade MCP acceptance

Phase 0.32 graduates **`hedron-mcp`** under the ROADMAP 0.26+ production-grade
contract as a **deny-by-default, authenticated MCP projection** for an explicitly
bounded Supported inventory. Install and mount grant no ambient authority.
Baseline: Published **`v0.31.0`**. Evidence is indexed by
[`release-gate-0.32.toml`](release-gate-0.32.toml).
**Zero Deferred:** every 0.32-owned gate row must be Verified at cut.

Owning decision: [D-060](../DECISIONS.md). RFC:
[RFC-0065](../rfcs/RFC-0065-PRODUCTION-GRADE-MCP.md) (graduation).
Alpha product contract remains [RFC-0043](../rfcs/RFC-0043-MCP-PROJECTION.md)
(phase 0.17; not reopened).
Tracking: [#89](https://github.com/eddiethedean/hedron/issues/89).
Packet SSOT:
[production-grade-inventory-032.toml](production-grade-inventory-032.toml).
Security review brief:
[security-review-032/BRIEF.md](security-review-032/BRIEF.md).

**Version policy at cut:** independent satellite **`hedron-mcp` `0.2.0` Beta**
(pin `>=0.2.0,<0.3`); Alpha `0.1.x` is the upgrade source. Coordinated with
Hedron train `v0.32.0`; package version is not train-locked `0.32.0` and is not
`1.0.0`.

## Entry criteria

- [x] Tip/SSOT honesty for Published `0.31.0`
- [x] Owning RFC-0065 / D-060 Accepted
- [x] Machine-readable inventory draft (Supported / Experimental / excluded)
- [x] Tracking issue #89 bound to phase 0.32 / `*-032` gates
- [x] Per-gate checker scripts implemented (`scripts/check_*_032.py`)
- [x] Upgrade-fixture plan from Alpha `0.1.x` consumers
- [x] Independent security review packet completed (`REVIEW-032`)

## Spec packet

- [x] ROADMAP §0.32 scope; D-060 / RFC-0065 recorded
- [x] `release-gate-0.32.toml` Verified evidence rows present
- [x] Gate checker recognizes `0.32` evidence manifest
- [x] Per-gate checkers Verified at cut
- [x] `REGRESS-032` / `PKG-032` at cut

## Out of 0.32

- Default-public tools or ambient authority from install/mount
- Identity provider, secrets broker, approval system, or tenant model
- Arbitrary Python/shell/URL/filesystem execution from model input
- Treating MCP protocol conformance as application tool safety
- Gradio MCP substitute / auto-composing Gradio tools (phase 0.34 under D-061)
- Scheduling Hedron `1.0` / SLA / certification
- Claiming every MCP symbol is Supported (mutations/vendor extensions may remain
  Experimental)

## Cut verify

During packet refine (living tip still `0.31.x`; checkers may be absent):

```bash
uv run python scripts/verify_pkg_32.py --allow-planned
```

At `v0.32.0` cut (`hedron-mcp` `0.2.0` Beta; every evidence row Verified):

```bash
uv run python scripts/verify_pkg_32.py
uv run python scripts/check_release_gate.py 0.32.0 --execute-verified
```

## Exit

- [x] Every 0.32-owned release-gate row is `Verified`
- [x] Production-grade / Beta maturity labels used only for declared Supported inventory
- [ ] Close #89 (after tagged `hedron-mcp` `0.2.0` / `v0.32.0` publish)
