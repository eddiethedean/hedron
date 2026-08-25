# Release acceptance: 0.64 Hedron HTMX interaction extension

**Status:** 0.64.0 bounded release slice — Required gates verified; broader phase capabilities explicitly deferred
**Implementation:** [HTMX_HEDRON_EXTENSION_064](../implementation/HTMX_HEDRON_EXTENSION_064.md)  
**RFC:** [RFC-0091](../rfcs/RFC-0091-HTMX-HEDRON-EXTENSION.md)
**Execution:** [EXECUTION_0_64](../implementation/EXECUTION_0_64.md)

**Issue inventory:** 22 phase-owned `enhancement` issues are tracked in the
[phase 0.64 roadmap inventory](../ROADMAP.md#phase-064-enhancement-inventory): 18 are implemented
and closed, while 4 remain open for deferred follow-up. This includes 0.62 carry-forward work;
issue #86 remains owned by phase 0.21.

## 0.64.0 release boundary

The `v0.64.0` cut is the bounded presentation/lifecycle slice implemented in the repository:
finite semantic presentation tokens, responsive scoped-style recipes, a stable parts/state
manifest, lifecycle facts and transitions, opt-in local `htmx-ext-hedron` asset injection, and
their package/docs/security contracts. The release does not claim completion of the entire
22-issue phase inventory. The eight broader capabilities listed as `Deferred` below remain owned
follow-up work and are not Required for this cut.

The executable evidence command is:

```bash
python scripts/check_064.py --verify
```

The strict release checker requires every Required row to be `Verified` and every Deferred row to
name its rationale and destination:

```bash
python scripts/check_release_gate.py 0.64.0
```

## Planned contract artifacts

- `htmx-hedron-extension-contract-064.toml`
- `htmx-hedron-extension-assets-064.toml`
- `htmx-hedron-extension-hosts-064.toml`
- `htmx-hedron-extension-a11y-064.toml`
- `htmx-hedron-extension-trace-064.toml`
- `htmx-hedron-extension-browser-064.toml`
- `htmx-hedron-extension-upgrade-fixtures-064.md`
- `theme-platform-contract-064.toml`
- `theme-platform-issue-dispositions-064.toml`
- `theme-platform-inventory-064.toml`
- `component-state-matrix-064.json`
- `scoped-style-dsl-064.toml`
- `theme-platform-upgrade-fixtures-064.md`

Names and schemas become authoritative only after Stage 0 acceptance.

## Planned gates

| Gate | Requirement | Minimum evidence | Status |
|---|---|---|---|
| `THEME-064` | Finite 0.64 presentation tokens resolve deterministically from a theme. | Contract digest, token export, and theme override checks | Verified |
| `MANIFEST-064` | The shipped parts/state manifest is stable, non-empty, and digestable. | Manifest lock and repeatability check | Verified |
| `TYPOGEOM-064` | The shipped typography, spacing, and geometry vocabulary is finite and safe. | Scale lock and unsafe-value check | Verified |
| `RESPONSIVE-064` | Shipped viewport/container/direction/writing-mode conditions compile deterministically. | Responsive recipe and fallback-condition check | Verified |
| `CONTROLS-064` | Full native-control appearance and state contract across first-party controls. | Deferred from 0.64.0; no Required claim | Deferred |
| `MOTION-064` | Full named motion-recipe, reduced-motion, print, and browser packet. | Deferred from 0.64.0; token foundation remains available | Deferred |
| `VISUAL-064` | Portable component state-matrix and cross-engine visual conformance. | Deferred from 0.64.0 | Deferred |
| `CUSTOM-064` | Application-defined components use the bounded scoped-style DSL. | Allowlist, cascade-layer, digest, and rejection checks | Verified |
| `CONTRACT-064` | Extension schemas, markers, policies, and maturity are frozen for the shipped slice. | Machine-readable contract and attribute checks | Verified |
| `ASSET-064` | `htmx-ext-hedron` is local, digest-checked, ordered after HTMX core, and opt-in. | Asset digest, static path, and load-order checks | Verified |
| `STATE-064` | Lifecycle facts and generation transitions reject older responses. | Pending/success/stale transition checks | Verified |
| `A11Y-064` | Shipped lifecycle hosts expose bounded busy/state semantics and validated focus/announcement settings. | Attribute and asset semantics checks | Verified |
| `RACE-064` | Full stale/cancelled/superseded browser race corpus. | Deferred from 0.64.0 | Deferred |
| `LIFE-064` | Full first-party module registry initialization/teardown and leak evidence. | Deferred from 0.64.0 | Deferred |
| `TRACE-064` | Cross-surface browser, Explorer, and redacted trace parity. | Deferred from 0.64.0 | Deferred |
| `INTEGRATE-064` | Page extension planning, local asset injection, and opt-in fallback agree. | Integration and load-order checks | Verified |
| `CSP-064` | The shipped asset has no dynamic code execution or network escape hatch. | Static CSP/safety checks | Verified |
| `SECURITY-064` | Shipped style values and asset boundaries reject unsafe inputs. | Adversarial value and asset checks | Verified |
| `BROWSER-064` | Full 0.64 Chromium/Firefox/WebKit journey matrix. | Deferred from 0.64.0; existing repository browser suite remains separate | Deferred |
| `PERF-064` | Dedicated extension overhead and retained-registration benchmark. | Deferred from 0.64.0 | Deferred |
| `UPGRADE-064` | Feature-absent pages retain their pre-extension output. | Opt-out/no-injection check | Verified |
| `DOCS-064` | Live docs, inventory, links, generated pages, and strict build agree. | Full docs gate | Verified |
| `PKG-064` | Coordinated package metadata and local asset packaging agree. | Package metadata and build checks | Verified |

## Issue-to-gate map

| Issues | Primary gates |
|---|---|
| #680, #681, #682, #686, #687 | `THEME-064`, `MANIFEST-064` |
| #677, #678, #690, #692, #697 | `TYPOGEOM-064`, `MOTION-064`, `MANIFEST-064` |
| #679, #695, #696, #698 | `RESPONSIVE-064`, `CONTROLS-064`, `A11Y-064` |
| #685, #688, #689, #693, #694 | `MANIFEST-064`, `CONTROLS-064`, `VISUAL-064` |
| #699 | `CUSTOM-064` |

## Release decision

Release requires every Required row Verified, zero Deferred Required capabilities, the extension
absent-path fallback passing, no client-side authority or inline-script escape hatch, and signed-off
asset, compatibility, accessibility, browser, performance, and rollback evidence. Progressive and
Experimental consumers retain their labels in docs, Explorer, metadata, and package manifests.
