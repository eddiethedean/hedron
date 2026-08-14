# Hedron `v0.39` rich data and visualization elements acceptance

**Status:** Published as Hedron **`v0.39.0`** (in-tree cut; tag/PyPI deferred). Stage 0 baseline was Published **`v0.38.0`**. All owned gates Verified.

Phase 0.39 converges first-party rich browser surfaces (DataTable/DataEditor, maps, media,
editors, and eligible specialty hosts) onto the shared element ABI, proves typed
`OptimisticMutation` on bounded collection edits, and integrates the Published 0.38
`hedron-chart` contract without creating a parallel renderer. Evidence is indexed by
[`release-gate-0.39.toml`](release-gate-0.39.toml). **Zero Deferred:** every 0.39-owned row must be
Verified at cut.

Owning decision: [D-067](../DECISIONS.md). Design:
[RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) (**Accepted**). Implementation:
[HEDRON_RICH_ELEMENTS_039](../implementation/HEDRON_RICH_ELEMENTS_039.md). Catalogs:
[WEB_COMPONENT_INTERACTION_CONTRACTS.md](../implementation/WEB_COMPONENT_INTERACTION_CONTRACTS.md) §3 ·
[RICH_SURFACE_039.md](../implementation/RICH_SURFACE_039.md). Capability inventory:
[`rich-surface-inventory-039.toml`](rich-surface-inventory-039.toml). Tracking:
[#94](https://github.com/eddiethedean/hedron/issues/94). Medium/low remediations (issue bodies
remain normative; `REGRESS-039` Verified only when closed):
[#73](https://github.com/eddiethedean/hedron/issues/73),
[#84](https://github.com/eddiethedean/hedron/issues/84),
[#102](https://github.com/eddiethedean/hedron/issues/102),
[#104](https://github.com/eddiethedean/hedron/issues/104),
[#105](https://github.com/eddiethedean/hedron/issues/105),
[#107](https://github.com/eddiethedean/hedron/issues/107),
[#113](https://github.com/eddiethedean/hedron/issues/113),
[#115](https://github.com/eddiethedean/hedron/issues/115),
[#116](https://github.com/eddiethedean/hedron/issues/116),
[#117](https://github.com/eddiethedean/hedron/issues/117),
[#118](https://github.com/eddiethedean/hedron/issues/118),
[#119](https://github.com/eddiethedean/hedron/issues/119),
[#120](https://github.com/eddiethedean/hedron/issues/120),
[#121](https://github.com/eddiethedean/hedron/issues/121),
[#176](https://github.com/eddiethedean/hedron/issues/176),
[#188](https://github.com/eddiethedean/hedron/issues/188),
[#189](https://github.com/eddiethedean/hedron/issues/189),
[#190](https://github.com/eddiethedean/hedron/issues/190),
[#191](https://github.com/eddiethedean/hedron/issues/191),
[#192](https://github.com/eddiethedean/hedron/issues/192),
[#193](https://github.com/eddiethedean/hedron/issues/193),
[#194](https://github.com/eddiethedean/hedron/issues/194),
[#221](https://github.com/eddiethedean/hedron/issues/221),
[#240](https://github.com/eddiethedean/hedron/issues/240),
[#241](https://github.com/eddiethedean/hedron/issues/241),
[#247](https://github.com/eddiethedean/hedron/issues/247),
[#248](https://github.com/eddiethedean/hedron/issues/248).

`A11Y-039` includes three-engine automated a11y plus a **scoped** keyboard/AT packet
([human-at/039](human-at/039/PROTOCOL.md)). It does **not** claim Supported human AT
([#86](https://github.com/eddiethedean/hedron/issues/86) / `SR-021`).

## Release contract at cut

- Coordinated Hedron train: `v0.39.0`.
- First-party DataTable/DataEditor browser behavior shares the public element ABI.
- `OptimisticMutation` is proven on bounded DataEditor/collection edits with typed revision,
  idempotency, confirm/rollback/refetch/conflict/reconnect contracts.
- Chart cross-filter and rich-surface composition consume Published `hedron-chart` only.
- Map/media/editor/specialty surfaces either share the ABI or publish an owned Experimental
  exception; workers/WASM/streams/origins are inventoried and bounded.
- Browser evidence: Chromium, Firefox, and WebKit on recorded exact versions.
- Rich adapters remain optional and non-transitive; useful SSR tables/summaries/forms/media links
  survive absent or failed JavaScript.

## Exact cut matrix

| Lane | Required proof | Command |
|---|---|---|
| Data grid/editor ABI | Edits, state, virtualization, validation, fallback, authz, teardown | `check_data_039.py` |
| Optimistic mutation | Typed revision/idempotency/confirm/rollback/refetch/conflict/reconnect | `check_optimistic_039.py` |
| Chart link | Cross-filter / composition on 0.38 chart contract | `check_chartlink_039.py` |
| Rich surfaces | Map/media/editor inventory + owned Experimental exceptions | `check_rich_039.py` |
| Worker bounds | Workers/WASM/streams/buffers/origins cleanup and limits | `check_worker_039.py` |
| Performance | Named large scenarios, memory, long tasks, CLS | `check_perf_039.py` |
| Accessibility | SSR fallback + upgraded-state budgets; scoped AT | `check_a11y_039.py` |
| Regression | Upgrades from `v0.38.0`, browsers/hosts, 27-issue packet | `check_regress_039.py` |
| Packaging | Inventory, docs, supply, release rehearsal | `verify_pkg_39.py` |

## Stage 0 entry/exit

- [x] D-067 Accepted and RFC-0060 Accepted (Resolved questions (D-067) present)
- [x] Gate manifest, implementation plan, capability inventory, upgrade fixture, review brief,
  production-grade inventory, rich-surface catalogs, and scoped AT-039 skeleton exist
- [x] Tracking issue [#94](https://github.com/eddiethedean/hedron/issues/94) is bound to every
  0.39 gate and the locked 27-issue remediation set
- [x] `v0.39.0` is Published; living baseline for this refine is `v0.39.0`
- [x] Stage 0 / contract refine makes no runtime/version/living-tip claim

## Verification

During planning:

```bash
python scripts/verify_pkg_39.py --allow-planned
```

At cut:

```bash
python scripts/verify_pkg_39.py
python scripts/check_release_gate.py 0.39.0 --execute-verified
```
