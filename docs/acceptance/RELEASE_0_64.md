# Release acceptance: 0.64 Hedron HTMX interaction extension

**Status:** Proposed / Planned gates  
**Implementation:** [HTMX_HEDRON_EXTENSION_064](../implementation/HTMX_HEDRON_EXTENSION_064.md)  
**RFC:** [RFC-0091](../rfcs/RFC-0091-HTMX-HEDRON-EXTENSION.md)

**Issue inventory:** 22 phase-owned open `enhancement` issues are tracked in the
[phase 0.64 roadmap inventory](../ROADMAP.md#phase-064-open-enhancement-inventory), including
0.62 carry-forward work. Issue #86 remains owned by phase 0.21.

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
| `THEME-064` | Semantic palette derivation, theme export, inspection, and conformance remain deterministic and explainable. | Theme contract, CSS/token export, diagnostics, and standalone conformance fixtures | Planned |
| `MANIFEST-064` | Parts, states, slots, bundles, and component metadata form one public manifest. | Manifest lock, slot/recipe fixtures, bundle identity, and package parity | Planned |
| `TYPOGEOM-064` | Typography, spacing, geometry, identity, and global theme hooks use finite semantic roles. | Scale lock, component role coverage, compatibility fixtures, and preference fallbacks | Planned |
| `RESPONSIVE-064` | Viewport/container conditions and direction/writing-mode policies are bounded and accessible. | Responsive/direction lock, nested-scope fixtures, RTL/bidi matrix, and no-JS fallback | Planned |
| `CONTROLS-064` | Native controls, data views, visualizations, glass surfaces, and identity states have theme contracts. | Form/data/visual vertical slices, forced-colors/high-contrast evidence, and fallback matrix | Planned |
| `MOTION-064` | Named motion recipes have deterministic reduced-motion, print, and busy-state behavior. | Motion lock, browser matrix, and performance evidence | Planned |
| `VISUAL-064` | Component state-matrix and visual conformance evidence covers the new presentation surfaces. | Portable state-matrix command, redacted reports, and Chromium/Firefox/WebKit results | Planned |
| `CUSTOM-064` | Application-defined components can use a scoped style DSL without arbitrary CSS or selector escape hatches. | DSL schema, value/token allowlists, cascade-layer/digest tests, and rejection corpus | Planned |
| `CONTRACT-064` | Extension id, markers, events, state projection, response facts, and maturity are frozen. | Machine-readable contract locks and schema validation | Planned |
| `ASSET-064` | `htmx-ext-hedron` is pinned, local, digest-checked, licensed, ordered after HTMX core, and demand-loaded. | Asset manifest, CSP/load-order tests, opt-out byte check | Planned |
| `STATE-064` | Browser projection consumes 0.61 lifecycle and operation identity without becoming authoritative. | Native/HTMX/element golden fixtures and spoofing cases | Planned |
| `A11Y-064` | Busy, disabled, announcements, validation focus, keyboard behavior, reduced motion, and no-JS fallback are consistent. | Semantic, keyboard, screen-reader-oriented, and browser evidence | Planned |
| `RACE-064` | Stale, cancelled, superseded, duplicate, removed-target, and reordered responses cannot corrupt current presentation. | Deterministic race corpus across fragment and navigation journeys | Planned |
| `LIFE-064` | Registered modules initialize and teardown exactly once across load, swap, cleanup, OOB, history, and failure paths. | Chart/map/grid/element lifecycle fixtures and leak checks | Planned |
| `TRACE-064` | Browser events, Explorer output, and tests project one bounded redacted trace. | Golden trace parity, truncation, malformed-input, and redaction tests | Planned |
| `INTEGRATE-064` | Hedron page planning, component markers, route metadata, simulator, and package exports agree. | Cross-package render/simulation/integration suite | Planned |
| `CSP-064` | Strict CSP works without inline handlers or response scripts; registry is explicit and scoped. | CSP browser matrix and negative executable-content tests | Planned |
| `BROWSER-064` | Core journeys pass in Chromium, Firefox, and WebKit. | Form, refresh, polling, navigation, focus, OOB, cleanup, and history matrix | Planned |
| `PERF-064` | Extension overhead, metadata, event count, and retained registrations stay within frozen budgets. | Reproducible browser/resource benchmark | Planned |
| `UPGRADE-064` | Pages without the declaration retain pre-extension behavior and rollback is documented. | Before/after fixtures, absent-asset tests, migration/rollback docs | Planned |
| `DOCS-064` | API, recipes, security model, fallback behavior, diagnostics, and extension declaration are accurate. | Docs link/API/example checks and rendered guide | Planned |
| `PKG-064` | Clean packages expose identical extension metadata and locally serve the asset. | Build/install/package identity and production-like smoke | Planned |

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
