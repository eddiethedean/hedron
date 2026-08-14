# Phase 0.39 implementation plan: rich data and visualization elements

This plan turns [RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) / D-067 into reviewable
work. The living published tip is `v0.38.0`. Stage 0 (including this contract refine) adds
contracts only and does not change runtime behavior or versions. Tracking
[#94](https://github.com/eddiethedean/hedron/issues/94). Authoritative optimistic contract:
[WEB_COMPONENT_INTERACTION_CONTRACTS.md](WEB_COMPONENT_INTERACTION_CONTRACTS.md) §3. Surface
catalog: [RICH_SURFACE_039.md](RICH_SURFACE_039.md).

## Outcome

Publish Hedron `v0.39.0` where first-party rich browser surfaces share the element ABI (or an
owned Experimental exception), `OptimisticMutation` is proven on bounded DataEditor/collection
edits, and DataTable/DataEditor composition consumes the Published 0.38 `hedron-chart` contract
without a parallel renderer.

Completion requires every row in
[`release-gate-0.39.toml`](../acceptance/release-gate-0.39.toml) Verified.

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
- Bind tracking [#94](https://github.com/eddiethedean/hedron/issues/94) and medium/low remediations
  #73/#84/#102/#104/#105/#107/#113/#115–#121/#176/#188–#194/#221/#240/#241/#247/#248.
- Rebaseline living published tip acknowledgment to `v0.38.0`.
- Add lenient packet verification to CI.
- Do not modify DataEditor/OptimisticMutation runtime, package versions, living pins, or release
  status.

**Explicitly forbidden until Stage 1+:** ABI migration code, OptimisticMutation runtime,
chartlink wiring, worker enforcement, workspace or tip bump, flipping any 0.39 gate to Verified,
adopter-facing “0.39 Published” claims.

Exit: `python scripts/verify_pkg_39.py --allow-planned`.

### Stage 1+ (sketched only)

- DATA-039: migrate DataTable/DataEditor browser hosts to shared ABI suites.
- OPTIMISTIC-039: implement typed revision machine on bounded collection edits.
- CHARTLINK-039: cross-filter / composition against Published `hedron-chart`.
- RICH-039 / WORKER-039: inventory exceptions and bound workers/streams/origins.
- PERF-039 / A11Y-039: named large scenarios + scoped AT evidence.
- REGRESS-039 / PKG-039: upgrade fixtures, close 27 issues, cut `v0.39.0`.

## Cut commands

During planning and implementation:

```bash
python scripts/verify_pkg_39.py --allow-planned
```

At the `v0.39.0` cut:

```bash
python scripts/verify_pkg_39.py
python scripts/check_release_gate.py 0.39.0 --execute-verified
```
