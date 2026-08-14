# Upgrade fixtures — phase 0.39 rich data and visualization elements

Published cut: Hedron **`v0.39.0`**. Stage 0 was refined against living Published `v0.38.0`.
Tracking [#94](https://github.com/eddiethedean/hedron/issues/94) closed.

## Required upgrade corpus

- DataTable/DataEditor markup and Python call shapes from `v0.38.0` retain source compatibility or
  emit named remediation diagnostics; ABI migration must not silently change edit/authz semantics.
- Bounded DataEditor/collection edit fixtures map to typed `OptimisticMutation` states
  (proposed/submitted/confirmed) with base revision, idempotency, rollback, conflict, and reconnect.
- Chart cross-filter and rich-surface composition fixtures consume Published `hedron-chart` /
  `ChartSpec` / `ChartPlan` only; no second interactive chart renderer appears.
- Map/media/code-editor/specialty hosts either share the public element ABI or publish an owned
  Experimental exception with destination phase.
- Worker/WASM/object-URL/stream/observer fixtures prove disconnect cleanup and payload/origin bounds.
- JavaScript-off/static-only deployments retain useful table/summary/form/media-link/export
  fallbacks.
- HTMX inner/outer/OOB lifecycle fixtures for DataTable/DataEditor remain green under the ABI
  migration.
- The locked 27-issue remediation corpus under #94 is closed at `REGRESS-039` Verified.

## Pin migration at cut

| Surface | Before (0.38 tip) | At Published 0.39 |
|---|---|---|
| Hedron train | `hedron>=0.38.0,<0.39` | `hedron>=0.39.0,<0.40` |
| Charts | `hedron-charts>=0.2.0,<0.3` | `hedron-charts>=0.2.0,<0.3` (consume 0.38 contract) |
| DataTable / DataEditor | 0.38 call shapes | ABI-shared Supported path (`hedron-data-editor`) |
| OptimisticMutation | Not Supported | Bounded DataEditor/collection proof |
| Map / media / editors | Mixed / Experimental | ABI or owned Experimental exception |

## Rollback

Rollback pins `hedron>=0.38.0,<0.39`, removes 0.39-only optimistic/ABI assets, and verifies no
stale custom-element definition, worker, object URL, or cached optimistic revision remains.
Browser-local pending edits are disposable and are not migrated as server authority.

## Required artifacts

- before/after markup, optimistic revision traces, accessibility tree, and fallback goldens;
- schema upgrade and unknown-version negative fixtures;
- three-browser persisted-cache/version-skew and rollback tests;
- clean wheelhouse install for 0.38 → 0.39 and 0.39 → 0.38 rollback documentation;
- remediation fixtures proving silent authz/edit/conflict regressions cannot ship.
