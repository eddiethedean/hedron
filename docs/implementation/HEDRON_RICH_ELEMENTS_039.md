# Phase 0.39 implementation plan: rich data and visualization elements

**Status:** Historical implementation plan; the `v0.39.0` cut is published. This file records
the accepted target and work slicing, not the exact current runtime surface. Use
[DATA.md](../api/DATA.md) and [What’s new in 0.39](../guides/whats-new-0.39.md) for adopter
contracts.

This plan turned [RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) / D-067 into reviewable
work. Tracking [#94](https://github.com/eddiethedean/hedron/issues/94) closed. Authoritative
optimistic contract: [WEB_COMPONENT_INTERACTION_CONTRACTS.md](WEB_COMPONENT_INTERACTION_CONTRACTS.md)
§3. Surface catalog: [RICH_SURFACE_039.md](RICH_SURFACE_039.md).

## Outcome

Publish Hedron `v0.39.0` where first-party rich browser surfaces share the element ABI (or an
owned Experimental exception), `OptimisticMutation` is proven on bounded DataEditor/collection
edits, and DataTable/DataEditor composition consumes the Published 0.38 `hedron-chart` contract
without a parallel renderer.

Completion requires every row in
[`release-gate-0.39.toml`](../acceptance/release-gate-0.39.toml) Verified — **done**.

## Locked architecture

| Layer | Contract |
|---|---|
| Data surfaces | DataTable/DataEditor share ABI config, typed edit/selection/events, validation, virtualization, saved-view, fallback, disposal |
| Optimism | Typed `OptimisticMutation` with base revision, patches/refetch, idempotency, confirm/rollback/conflict/reconnect; deny-by-default risk exclusions |
| Charts | Cross-filter and composition consume Published `hedron-chart` / `ChartSpec` only |
| Rich inventory | Map/media/code-editor/specialty surfaces inventoried; Experimental exceptions owned |
| Workers | Workers/WASM/object URLs/streams/observers/buffers/origins bounded; cleanup on disconnect |
| Evidence | Named large-scenario PERF/A11Y budgets; scoped AT; 27-issue REGRESS packet |

## Work breakdown

### Stage 0 — contract and evidence packet (complete)

- Accept D-067 / RFC-0060 Resolved questions (D-067).
- Add this plan, release packet, gate manifest, inventories, upgrade fixtures, review brief,
  [RICH_SURFACE_039.md](RICH_SURFACE_039.md), and scoped [AT-039](../acceptance/human-at/039/PROTOCOL.md).
- Bind tracking [#94](https://github.com/eddiethedean/hedron/issues/94) and medium/low remediations.
- Exit: `python scripts/verify_pkg_39.py --allow-planned`.

### Stage 1+ — implementation and cut (complete)

- DATA-039: migrate DataTable/DataEditor browser hosts to shared ABI suites.
- OPTIMISTIC-039: implement typed revision machine on bounded collection edits.
- CHARTLINK-039: cross-filter / composition against Published `hedron-chart`.
- RICH-039 / WORKER-039: inventory exceptions and bound workers/streams/origins.
- PERF-039 / A11Y-039: named large scenarios + scoped AT evidence.
- REGRESS-039 / PKG-039: upgrade fixtures, close 27 issues, cut `v0.39.0`.

## Cut commands

```bash
python scripts/verify_pkg_39.py
uv run python scripts/check_release_gate.py 0.39.0
```

At the `v0.39.0` cut:

```bash
python scripts/verify_pkg_39.py
python scripts/check_release_gate.py 0.39.0 --execute-verified
```
