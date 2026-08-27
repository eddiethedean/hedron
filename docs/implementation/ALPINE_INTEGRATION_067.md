# Phase 0.67 implementation plan: Alpine browser-local enhancement

**Status:** Proposed  
**Authority:** [RFC-0095](../rfcs/RFC-0095-ALPINE-BROWSER-ENHANCEMENT.md) / D-113 / D-115 / D-116  
**Baseline:** `v0.66.2`  
**Target:** `v0.67.0`  
**Capability and widget audit:** [ALPINE_CAPABILITY_AUDIT_067](ALPINE_CAPABILITY_AUDIT_067.md)  
**Acceptance:** [RELEASE_0_67](../acceptance/RELEASE_0_67.md)  
**Contract freeze:** [contract-freeze-067.toml](../acceptance/contract-freeze-067.toml)  
**Compatibility BOM:** [compatibility-bom-067.toml](../acceptance/compatibility-bom-067.toml)  
**HTMX/Alpine boundary:**
[HTMX_ALPINE_BOUNDARY_1_0](../api/HTMX_ALPINE_BOUNDARY_1_0.md)  
**Component engine dispositions:**
[COMPONENT_ENGINE_DISPOSITIONS_067_1_0](COMPONENT_ENGINE_DISPOSITIONS_067_1_0.md)  
**1.0 interface audit:**  
[HEDRON_1_0_EDRON_INTERFACE_AUDIT](HEDRON_1_0_EDRON_INTERFACE_AUDIT.md)

## Objective

Add one demand-driven Alpine path through Hedron's existing browser, asset, security, component,
HDJ, HTMX lifecycle, diagnostics, and conformance authorities. The implementation must round out
browser-local interactions without creating a second request, rendering, domain-state, or package
runtime.

```text
Python component / HDJ
        -> normalized browser feature + Alpine directive plan
        -> registry / local assets / CSP / manifests
        -> semantic HTML + x-* projection
        -> Alpine local state
              ↕ explicit lifecycle bridge
           HTMX swaps and Hedron interaction state
```

## Work packages

| ID | Work package | Outcome | Gates |
|---|---|---|---|
| W0 | Contract freeze and upstream probes | accepted task graph, exact 1.0-compatible signatures/returns, closed interaction/outcome algebra, warning registry, compatibility BOM, reproducible CSP core/plugins/`@alpinejs/ui`, provenance/digests, expression corpus | `FREEZE-067`, `SUPPLY-067`, `CSP-067` |
| W1 | Unified document browser plan | component/interaction demands, initial + reachable-fragment closure, plan fingerprint, subset enforcement, ordered Alpine/HTMX assets | `PLAN-067`, `CLOSURE-067`, `ASSET-067` |
| W2 | Typed directive model | normalized sink-specific attributes, state, expressions, modifiers, trust boundary | `DIRECTIVE-067`, `SECURITY-067` |
| W3 | Core parity | all documented core directives/magics/globals dispositioned and tested | `CORE-067` |
| W4 | Official extension parity | official plugin catalog plus `@alpinejs/ui` candidate, demand-driven with bounded dispositions | `PLUGIN-067`, `UI-067` |
| W5 | Unified interaction preview | one discriminated `Interaction` with closed local/request/combined effects lowering to Alpine, HTMX, and native handles; role-indexed closed `Outcome` values; normative ownership and non-interference contract | `INTERACTION-067` |
| W6 | HTMX lifecycle | init/cleanup/swap/OOB/history/generated-content integration | `HTMX-067` |
| W7 | State transfer and optional Morph | Supported replacement/reset plus explicit preserve contract; Progressive Morph only if full evidence passes | `MORPH-067`, `STATE-067` |
| W8 | Authoring consumers | Python, HDJ, registry, Explorer, checks, testing helpers | `AUTHOR-067`, `HDJ-067`, `TOOLING-067` |
| W9 | Component-engine and accessible-widget program | audit Web Components/controllers/Alpine modules in both directions; migrate lightweight common wrappers to native/Alpine, retain or promote specialist Web Components, and cover disclosure, overlays, menus, tabs, choices, notifications, tooltip, carousel, listbox, combobox, field helpers, and sortable patterns without restricted Alpine UI source | `ENGINE-067`, `WIDGET-067`, `A11Y-067` |
| W10 | Failure, performance, and cleanup | script/plugin/CSP/integrity failure-safe semantics, feature-off zero cost, asset/DOM/observer/swap/leak budgets | `FAILURE-067`, `PERF-067` |
| W11 | 1.0 migration lane | frozen subset enforcement, complete public removal inventory, deprecation warnings, conservative check/migrate tooling, dual-version corpus/BOM | `COMPAT-067`, `DEPRECATE-067`, `BOM-067` |
| W12 | Fleet/docs/package | adapters, examples, manifests, notices, packaging and regression | `DOCS-067`, `REGRESS-067`, `PKG-067` |

## Stage 0 probes before API freeze

`FREEZE-067` is the W0 exit and W1 entry gate. It must freeze the public 1.0-compatible contract;
artifact probes may continue afterward, but cannot create another canonical spelling or handler
return shape.

1. Reproduce Alpine `3.16.3` `@alpinejs/csp`, all nine official plugin artifacts, and the compatible
   `@alpinejs/ui` candidate. Record independent package versions, transitive dependencies, license,
   raw/gzip size, SHA-256, and build provenance.
2. Run a generated expression matrix in Chromium, Firefox, and WebKit. Include assignment,
   member assignment, calls, async values, getters, arrays/objects, comparisons, boolean
   short-circuiting, magic values, errors, and prohibited global/HTML injection cases.
3. Exercise HTMX inner/outer/OOB/delete/history swaps against Alpine roots both inside and outside
   the target. Measure initialization count, cleanup count, focus, local state, and observers.
4. Compare normal replacement, Alpine Morph, the community `alpine-morph` HTMX path, and a small
   Hedron lifecycle adapter. Keep normal replacement/reset Supported. Admit at most one Morph path
   as Progressive if it passes; a failed Morph probe does not block the base release.
5. Prototype the normalized Python and HDJ syntax against counter, disclosure, local filter,
   masked field, modal, and an HTMX-updated fragment. Freeze one long-form representation.
6. Inventory the current `Page.scripts`, `Page.htmx_extensions`, application assets, browser-module
   registry, Web Components, inline-attribute policy, and render-time requirement collectors. Define
   one normalization graph, initial/reachable-fragment feature closure, plan fingerprint, and subset
   failure behavior plus the 1.0 disposition of each compatibility entry point.
7. Prototype one discriminated interaction declaration for local-only, server-only, and combined
   effects plus role-indexed outcomes. Prove invalid combinations fail and valid values lower to the
   existing Alpine, HTMX, handle, security, and fallback authorities.
8. Exercise the removal inventory through runtime calls, build/HDJ/config checks, CLI invocations,
   imports, and generated code so every 1.0 removal has an observable 0.67 deprecation path.
9. Prototype the function-only `page` / `view` / `action` authoring spine, explicit `hedron.ui`
   return trees, one `Outcome`, one `Interaction`, and one `app.include(...)` path. Class-based
   route authoring and Edron-style implicit output collection are excluded.
10. Inventory current Hedron components against the W3C APG pattern index and the public widget
    needs identified by the Alpine ecosystem. For each, choose enhance/consolidate/add/defer;
    record semantics, keyboard, focus, no-JS, plugin, HTMX, and provenance requirements. Restricted
    Alpine UI source, screencasts, subscriber material, and copied markup are forbidden inputs.
11. Inventory `hedron-ui.mjs`, `hedron-disclose.mjs`, every `hedron-elements` tag, provider host,
    and registered Alpine/browser controller in the machine engine inventory. Build behavior-parity
    fixtures and choose one native, Alpine, Web Component, provider-owned, fixture, or non-fit
    disposition per task. Register removed public paths for runtime or target-1.0 warnings; retain
    the element ABI, and evaluate specialist script/native/Alpine hosts for Web Component promotion.
12. Audit PineMix's 30 public categories and permissively licensed Alpine component sources. Copy
    nothing without an exact redistribution grant; for admitted source, freeze commit/tag, notices,
    modifications, dependencies, and test provenance. Tailwind, remote templates, auto-import, and
    another component runtime do not enter the consumer contract.
13. Exercise JavaScript disabled, Alpine/core/plugin 404, SRI mismatch, CSP refusal, partial plugin
    failure, and slow initialization. Essential content and the only usable control may never depend
    on `x-cloak`; enhanced hiding begins only under an initialized-root marker.
14. Freeze the exact compatibility BOM: Python/FastAPI/Pydantic, adapters, coordinated and
    independent satellites, Alpine/HTMX artifacts, browser/OS revisions, pyright configuration,
    CLI/config/HDJ schema versions, and cross-version fixture constraints.

## Expected repository seams

| Existing authority | Expected extension |
|---|---|
| `hedron_core._html.policy` / serializer | admit only normalized sink-specific Alpine attributes and recheck trust/CSP/URL/style rules at serialization and reactive assignment |
| `hedron_core.application_assets` / registry assets | exact local Alpine core/plugin plans, dependencies, placement, integrity, manifests |
| `RenderSession`, `Page`, page assets, route graph, build manifests | collect component/interaction demands, compute initial + reachable-fragment closure, fingerprint it, enforce fragment subsets, and omit feature-off assets |
| `htmx-ext-hedron` | documented-surface Alpine init/cleanup/process/settle/history outcomes without request ownership or undocumented Alpine internals |
| HDJ source/inventory/checker | declared `alpine` capability, directive grammar, plugin and trust findings |
| component and interaction catalogs | read-only Alpine feature/directive facts and local-state ownership |
| Explorer / CLI / scenario testing | inspect state roots, active plugins, lifecycle events, CSP findings, and deterministic assertions |
| security policy and CSP reconciliation | refuse normal Alpine build, `unsafe-eval`, response registration, remote assets, and untrusted `x-html` |

## Implementation order and prerelease checkpoints

W0 freezes the 1.0-compatible contract and warning/BOM authorities before W1 begins. W1–W2 freeze
document closure, activation, syntax, and trust boundaries. W3–W4 implement the complete feature
inventory only through that model. W5 implements the already-frozen discriminated interaction and
role-indexed outcomes; W6–W7 settle lifecycle and state ownership before any built-in recipe claims
are made. W8–W10 expand authoring, failure evidence, and budgets. W11 proves the frozen subset and
all removal warnings before W12 publishes docs or packages.

The working checkpoints are:

1. `0.67a0` — `FREEZE-067`, warning registry, compatibility BOM, and upstream supply decisions;
2. `0.67a1` — document feature closure, assets, typed directives, and CSP grammar;
3. `0.67a2` — lifecycle, official plugins, state, failure behavior, and optional Morph disposition;
4. `0.67a3` — bidirectional component-engine dispositions, conversions, and per-family
   `@alpinejs/ui` decisions;
5. `0.67rc1` — dual-version fixtures, warnings/migration, AT/a11y, budgets, fleet, and packaging; and
6. `1.0a1` — removal/default-switch hardening from the frozen 0.67 subset, with no new public
   capability or calling form.

Failure of a Stage 0 probe changes the proposed contract or its maturity label; it does not justify
adding `unsafe-eval`, remote assets, implicit activation, hidden state preservation, or an unbounded
raw-attribute bypass.

## Definition of done

- Every Alpine core/plugin feature has a machine-readable Supported, Progressive, Experimental,
  or Excluded disposition tied to an evidence row.
- Every practical widget need has an enhance/consolidate/add/defer disposition. Required widgets
  reuse one existing Hedron component name and pass provenance plus accessibility evidence; no
  parallel `Alpine*` component family or copied paid-component implementation exists.
- Every Hedron-owned Required common widget uses a registered Alpine module for enhanced local
  behavior. Existing delegated controllers and duplicate custom elements remain 0.67 compatibility
  paths only and have complete warning/migration coverage for 1.0 removal.
- Every current tag, controller, registered Alpine module, provider host, and promotion candidate
  has one evidence-backed engine disposition and one canonical public task/component name.
- The public Web Component ABI and third-party authoring path remain supported; retained or promoted
  specialist hosts pass their existing ABI, lifecycle, fallback, HTMX, CSP, accessibility, and
  performance obligations.
- A docs/static lint rejects parallel native/Alpine/Web-Component variants for one ordinary task.
- Feature-off applications emit no Alpine asset, directive, observer, store, or request.
- Canonical components and interactions contribute their own typed feature demands; the PAGE plan
  closes over declared reachable fragments, and a fragment requiring an absent plugin/module fails
  deterministically without response-time registration.
- Feature-on applications work under `script-src 'self'` without `unsafe-eval` and without a user
  Node build.
- Python and HDJ normalize to identical directive and feature facts.
- Ordinary HTMX replacement/reset has deterministic initialization, cleanup, focus, history, state,
  and generated-content behavior across three engines. An admitted Progressive Morph path meets the
  same bar; otherwise the recorded non-admission is complete.
- Essential semantic content remains available when JavaScript is disabled or Alpine/core/plugin
  assets are missing, refused, slow, or fail integrity; `x-cloak` never owns the only usable path.
- Security, accessibility, no-JavaScript, performance, leak, packaging, and upgrade gates pass.
- The complete canonical 1.0 interface is present and its fixture corpus passes on `v0.67.0`.
- Every documented/exported/generated/configured executable 0.67 path excluded from 1.0—including
  beta/experimental paths—produces a visible-by-default structured
  `HedronFutureWarning`; every static-only config, HDJ, markup, manifest, import, or CLI use produces
  the equivalent target-1.0 finding. Each has one replacement or explicit non-fit reason, migration
  fixture, and complete/partial/unknown analysis confidence; dynamic uncertainty is never reported
  as a clean migration.
- The exact compatibility BOM is exercised by both 0.67 and 1.0 source/type-check fixtures.
- A docs/API lint proves one canonical public path per audited developer task and abstraction
  level; compatibility aliases remain migration-only and do not enter 1.0.
