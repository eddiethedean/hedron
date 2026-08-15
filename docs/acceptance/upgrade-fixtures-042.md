# Upgrade fixtures — phase 0.42 production-grade Web Component platform

**Status:** Verified at cut. Baseline Published `v0.41.0`; target `v0.42.0`.

## Required matrix

- 0.41 pages and Supported 0.36–0.41 first-party elements behave identically on 0.42 assets when
  within the declared Supported inventory.
- Mixed 0.36–0.41 server/module combinations with 0.42 peers fail visibly per element and preserve
  SSR, links, forms, and full-fragment navigation.
- Unknown or incompatible ABI/tag/event/form versions fail closed; no implicit downgrade accepts
  data or silently promotes Experimental surfaces.
- Experimental elements/adapters remain absent from production defaults and retain owner +
  destination/terminal disposition.
- CDN refusal, offline wheel/npm installs, package removal of `hedron-elements`, and unsupported-
  feature fallback preserve ordinary form/link/full-fragment flows.
- Upgrade and rollback leave no stale graph registrations, storage entries, listeners, observers,
  timers, workers, object URLs, or trace buffers from graduated surfaces.

## Pin migration

| Package | From (living tip) | To (cut target) |
|---|---|---|
| `hedron` / train-aligned fleet | `>=0.41.0,<0.42` | `>=0.42.0,<0.43` |
| `hedron-elements` | Alpha incubator `>=0.41.0,<0.42` | Beta Supported-inventory `>=0.42.0,<0.43` |
| `hedron-charts` | `>=0.2.0,<0.3` (unchanged) | `>=0.2.0,<0.3` (cross-reference only) |

## Rollback

Pin the coordinated train to `hedron>=0.41.0,<0.42` and `hedron-elements>=0.41.0,<0.42`, remove any
0.42-only inventory claims, and verify ordinary form/link/full-fragment flows. Disposable browser
state (draft transfer, local UI) is never migrated into server state or previous-train storage.

## Evidence artifacts at cut

- before/after/mixed-version HTML and registry fixtures across 0.36–0.41 baselines;
- three-engine compatibility, CDN-refusal, offline-install, and package-removal recordings;
- Supported inventory vs Experimental exclusion assertions;
- AT-042 disposition ledger (not SR-021);
- performance budget recordings on `examples/reference-app`; and
- exact 32-issue regression fixtures linked from `REGRESS-042`.
