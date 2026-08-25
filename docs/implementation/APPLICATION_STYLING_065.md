# Phase 0.65 implementation — integrated styling platform and application CSS

Status: **Implemented; release readiness validated for v0.65.0**. Runtime, build, CLI, issue
slices, tests, evidence checks, and coordinated package metadata are complete. Publication remains
owned by the release workflow.

- Authority: [RFC-0092](../rfcs/RFC-0092-INTEGRATED-STYLING-PLATFORM.md)
- Accepted decisions: D-109 (phase scope), D-110 (Stage 0 contract refinement)
- Predecessor: published/in-tree `v0.64.1` (`v0.64.0` remains the public PyPI baseline)
- Target: `v0.65.0`
- Acceptance: [RELEASE_0_65](../acceptance/RELEASE_0_65.md)
- Refined scope: [application-styling-scope-065](../acceptance/application-styling-scope-065.md)
- Execution: [EXECUTION_0_65](EXECUTION_0_65.md)

## Outcome

Hedron owns one inspectable styling system that works for built-in presentation and ordinary
application CSS. A user can start with semantic props and themes, add a registered local
stylesheet, target stable public parts and states, define namespaced application tokens, inspect
the resulting cascade, and eject generated CSS without losing provenance. Private generated class
names, inline response CSS, remote assets, and a second CSS-in-Python runtime remain outside the
contract.

## Architecture

### One styling authority

The existing theme, recipe, scoped-style, CSS compiler, asset graph, cascade, marker, CSP, and
diagnostic authorities remain canonical. Phase 0.65 adds adapters and metadata to those authorities;
it does not introduce a parallel stylesheet registry or client styling runtime.

### Authoring ladder

The documented ladder is progressive and reversible:

1. semantic component props and built-in appearance;
2. theme tokens and bounded presentation recipes;
3. registered application CSS using public component hooks;
4. explicitly scoped ordinary CSS, with an explicit global option;
5. provenance-preserving ejection for teams that need owned CSS.

Every lane must lower to the same stylesheet manifest, layer order, source map, token provenance,
and diagnostics. A stronger lane cannot silently change behavior, state, security, or semantics.

### Required contracts

| Workstream | Required result | Gate |
|---|---|---|
| `CONTRACT-065` | Stage 0 freezes schemas, precedence, compatibility, and non-goals | `CONTRACT-065` |
| `ASSET-065` | Local app stylesheets are declared assets with fingerprint, CSP, preload, HTMX, and no-JS behavior | `ASSET-065` |
| `LAYER-065` | `application` is explicit between `components` and `utilities`; ordering is inspectable | `LAYER-065` |
| `TOKEN-065` | Application tokens are namespaced, typed, theme-aware, provenance-preserving, and exportable | `TOKEN-065` |
| `HOOKS-065` | Stable component/part/state hooks are manifest-backed; private classes are never public API | `HOOKS-065` |
| `CSS-065` | Scoped and explicit-global ordinary CSS have deterministic source maps and rejection rules | `CSS-065` |
| `INSPECT-065` | `style explain`, `style inspect`, and `style check --custom-css` expose the winning declarations and source | `INSPECT-065` |
| `EJECT-065` | Ejected CSS retains source, token, hook, and generated-block provenance; diff/update are safe | `EJECT-065` |
| `MOTION-065` | Named motion recipes have reduced-motion fallbacks and no mandatory animation | `MOTION-065` |
| `CONTROLS-065` | Native form controls have an appearance/state contract with usable fallback | `CONTROLS-065` |
| `DATA-065` | Tables/data views have semantic chrome tokens and overflow/empty/loading/error states | `DATA-065` |

### Presentation coverage

The required cross-cutting matrix applies to every surface touched by the four issue slices: focus-
visible and disabled/busy/invalid states; forced-colors/high contrast; reduced motion and print;
responsive behavior, RTL/logical properties, touch targets, semantic/no-JS fallback, and readable
overflow. The broader catalog—new navigation, tabs, overlays, container/density/touch scales,
typography, media, icons, visualization chrome, export themes, and full preference-mode expansion—
is Progressive unless a touched surface needs it to satisfy its fallback contract. Each Progressive
row has an owner and fallback; none becomes Supported by inclusion in a roadmap table.

## Workstreams

| ID | Work | Deliverable |
|---|---|---|
| W0 | Entry and contract freeze | predecessor audit, issue disposition, exact schemas, compatibility and budget locks |
| W1 | Asset graph | application stylesheet registration, manifests, fingerprints, CSP and HTMX/head integration |
| W2 | Public hooks | component/part/state/slot inventory, emitted attributes, stability policy, selector helpers |
| W3 | Token bridge | application namespace, theme patch integration, provenance, export and collision checks |
| W4 | Cascade and scope | `application` layer, scoped/global policy, source maps, specificity and reset protections |
| W5 | Diagnostics | deterministic explain/inspect/check findings and redacted output |
| W6 | Ejection | named generated blocks, provenance markers, diff/update/check, rollback fixture |
| W7 | Open issue verticals | six motion presets; five public-part/state slices; data-view chrome; native controls, with fallbacks and browser evidence |
| W8 | Cross-cutting fallbacks and Progressive catalog | required focus/preference/print/RTL/no-JS checks on touched surfaces; explicitly owned Progressive breadth |
| W9 | Fleet and packages | flagship app, starters, adapters, component packages, asset/CSP/package ownership |
| W10 | Hardening | security, accessibility, no-JS, browser matrix, performance, regression and upgrade fixtures |
| W11 | Documentation and release | API, guides, migration, examples, acceptance evidence, release and rollback handoff |

## Safety and compatibility

Unregistered stylesheet paths, private selectors, unsafe at-rules, remote imports, token collisions,
unsupported browser features without a fallback, and attempts to style behavior-owned state are
rejected with actionable diagnostics. Application CSS is inert data at render time; it cannot add
scripts, alter routes, bypass CSP, or replace server-authoritative interaction state.

The upgrade fixture keeps existing 0.64 output valid when the feature is unused. Removing an app
stylesheet, changing a public hook, or changing an exported token requires a manifest diff and an
explicit compatibility disposition. All budgets are reject-not-slice: a build fails instead of
silently omitting styles.

## Progressive and excluded work

Typed selector helpers, Explorer computed-cascade views, token package exchange, CSS anchor
positioning, visual regression tooling, and recipe suggestions are Progressive. Third-party package
styling contracts, Houdini, external design-token synchronization, telemetry, a browser style
editor, arbitrary private selectors, and behavior-changing CSS are Deferred or excluded as recorded
in the RFC and acceptance inventory.

The Stage 1 implementation prerequisites are satisfied: D-110 is accepted, all four issue slices have a named owner
and issue-to-gate mapping, the [refined scope](../acceptance/application-styling-scope-065.md)
checklist is complete, and the packet is evaluated without inventing unspecified runtime behavior.
