# Hedron `v0.67.0` Alpine integration acceptance plan

Phase 0.67 is governed by [RFC-0095](../rfcs/RFC-0095-ALPINE-BROWSER-ENHANCEMENT.md), D-113,
the D-115 contract-freeze and D-116 component-engine refinements, the
[contract freeze](contract-freeze-067.toml), [compatibility BOM](compatibility-bom-067.toml),
[release-gate manifest](release-gate-0.67.toml), the
[HTMX/Alpine boundary](../api/HTMX_ALPINE_BOUNDARY_1_0.md), the
[component engine dispositions](../implementation/COMPONENT_ENGINE_DISPOSITIONS_067_1_0.md) and
[machine inventory](component-engine-dispositions-067.toml), the
[capability and widget audit](../implementation/ALPINE_CAPABILITY_AUDIT_067.md), and the
[implementation plan](../implementation/ALPINE_INTEGRATION_067.md). The predecessor is `v0.66.2`.

`FREEZE-067` is the W0 exit and W1 entry gate. It freezes exact public names/signatures/returns,
interaction/outcome algebra, document feature-closure ownership, warning records, and the
compatibility BOM before runtime implementation. Artifact-derived pins, budgets, browser fixtures,
and implementation thresholds then freeze from Stage 0 evidence without changing those public
forms. All release gates are Planned until their evidence exists; the cut requires every Required
row Verified and zero undocumented Deferred row.

| Gate | Required evidence |
|---|---|
| `FREEZE-067` | Accepted machine-readable task graph; function-only page/view/action signatures; single-tree page/view returns; role-indexed closed `Outcome`; discriminated local/request/combined `Interaction`; document feature closure; public/removal/warning schema; exact compatibility BOM; W1 remains blocked until Verified |
| `CONTRACT-067` | Accepted authority, feature inventory, state classes, non-goals, and exact public contract with no alternate canonical spelling |
| `SUPPLY-067` | Reproducible exact CSP core/plugin/official-UI candidate pins, hashes, licenses, provenance, SBOM, ecosystem-source notices, and local/offline assets |
| `CSP-067` | Three-engine expression corpus passes without `unsafe-eval`, inline response scripts, remote origins, or normal-build fallback |
| `PLAN-067` | One immutable document browser feature plan; canonical components/interactions self-contribute exact demands; existing scripts/extensions have explicit normalization and 1.0 dispositions |
| `CLOSURE-067` | Initial tree plus declared reachable-fragment transitive closure, versioned plan fingerprint, fragment subset enforcement, dynamic/unknown diagnostics, and zero response-time plugin/module registration |
| `ASSET-067` | Demand-driven ordering, dedupe, fingerprint, PAGE/build manifests, integrity, and feature-off zero requests; fragments never install executable assets |
| `DIRECTIVE-067` | Python/HDJ long-form directive normalization, sink-specific binding types, typed state/expression/modifier grammar, stable serialization, and diagnostics |
| `CORE-067` | Every documented Alpine directive, magic, and global has an executable disposition; Required core verticals pass |
| `PLUGIN-067` | All nine official plugins have explicit maturity, exact assets, dependency order, failure behavior, and focused tests |
| `UI-067` | The exact `@alpinejs/ui` candidate has a tagged/published license and stability disposition; each of combobox, dialog, disclosure, listbox, menu, popover, radio, switch, and tabs passes or receives an explicit fallback after CSP/Focus/lifecycle/a11y/browser/budget probes |
| `INTERACTION-067` | One discriminated 1.0-compatible declaration covers closed local/request/combined effects; role-indexed `Outcome` values and illegal-state rejection lower to existing Alpine/HTMX/Hedron authorities; dual DOM writers, duplicate dispatch, and cross-authority state are rejected |
| `HTMX-067` | The normative HTMX/Alpine boundary passes init/cleanup/settle/OOB/delete/history/error, one-writer focus/announcement/pending presentation, and Alpine-created HTMX content across Chromium/Firefox/WebKit |
| `MORPH-067` | Ordinary replacement/reset remains Supported; either exactly one Progressive Alpine-aware Morph path passes state/identity/focus/stale-state evidence or a recorded non-admission proves no morph authority ships |
| `STATE-067` | Component/store/persist/form/interaction/domain ownership and bounded transfer/storage rules pass adversarial tests |
| `FAILURE-067` | JavaScript-disabled, Alpine/core/plugin 404, integrity mismatch, CSP refusal, plugin-registration failure, and slow-start fixtures retain essential semantic content and ordinary form/link/server behavior; `x-cloak` never owns the only usable path |
| `SECURITY-067` | Untrusted expressions/HTML/globals/URLs/selectors/storage, response registration, secrets, and policy bypasses fail closed |
| `AUTHOR-067` | Python components, HTML primitives, recipes, registry/catalog, adapters, and direct escape hatch use one model |
| `HDJ-067` | HDJ declaration, static checking, CSP, rendering, fragments, and provider/manifest parity pass without template execution in checks |
| `TOOLING-067` | check/inspect/Explorer/scenario/browser trace outputs are deterministic, source-mapped, bounded, and redacted |
| `ENGINE-067` | Every first-party tag/controller/Alpine module/provider host and promotion candidate has one evidence-backed native/Alpine/Web-Component/provider/fixture/non-fit disposition; lightweight migrations and retained/promoted specialist hosts pass parity, ABI, lifecycle, fallback, CSP, a11y, HTMX, performance, warning, and one-canonical-engine checks; the public element ABI and third-party authoring path remain supported |
| `WIDGET-067` | Current components/controllers plus the PineMix 30-category and permissive-source audits have dispositions; every Required common widget uses registered Alpine or admitted `@alpinejs/ui` behavior through one Hedron API, has behavior-parity and immutable license/design provenance, contains no restricted/unclearly licensed source or parallel Alpine-prefixed family, and gives each legacy controller/custom-element path a 1.0 warning disposition |
| `A11Y-067` | Semantic/no-JS plus keyboard/focus/zoom/reflow/reduced-motion/forced-colors/RTL automated fixtures pass for admitted recipes/plugins; high-complexity admitted widgets have a named human-AT matrix or remain Progressive without an accessibility-conformance claim |
| `PERF-067` | Core/plugin bytes, requests, init/DOM walk, observers, swaps, and repeated cleanup remain within frozen budgets |
| `COMPAT-067` | 0.66 upgrade is additive; the frozen function-only 1.0 `page`/`view`/`action`, role-indexed `Outcome`, discriminated `Interaction`, `hedron.ui`, and inclusion corpus runs on 0.67; every 0.67-only path has a disposition/remediation; a task lint proves one canonical path per abstraction level |
| `DEPRECATE-067` | Every documented/exported/generated/configured executable 0.67 interface absent from 1.0—including beta/experimental paths—emits visible-by-default structured `HedronFutureWarning`; static-only config/HDJ/markup/manifest/import/CLI uses produce the equivalent target-1.0 warning with code, replacement/non-fit reason, removal version, source, fixture, and complete/partial/unknown confidence |
| `BOM-067` | Exact Python, FastAPI, Pydantic, adapters, coordinated/independent satellites, Alpine/HTMX assets, browser/OS, pyright, CLI/config/HDJ, and fixture constraints are machine-locked and exercised for 0.67/1.0 source and type compatibility |
| `DOCS-067` | Concepts, authority boundary, security, recipes, feature matrix, lifecycle, migration, and no-backend examples are accurate |
| `REGRESS-067` | Full supported Python, adapter, HDJ, HTMX, Web Component, browser, a11y, security, and package suite passes |
| `PKG-067` | Clean wheel/sdist/offline installs, coordinated ranges, notices, manifests, signatures, and release rehearsal pass |

## Required vertical slices

1. counter/local toggle with semantic initial content;
2. disclosure/dropdown with outside click, Escape, and focus return;
3. tabs with stable ids, keyboard navigation, and no-JavaScript content access;
4. dialog/anchored popover using Focus/Collapse/Anchor with reduced-motion fallback;
5. client-only filter over already-authorized rendered rows;
6. masked native form input whose server submission/validation remains authoritative;
7. HTMX fragment replacement containing Alpine roots and Alpine-created content containing HTMX;
8. initial page whose later declared fragment needs a plugin/module absent from the initial tree,
   proving closure installs it up front; an undeclared/dynamic incompatible fragment fails clearly;
9. OOB update and history restoration with deterministic reset/preserve behavior;
10. bounded non-sensitive Persist preference with version/key cleanup;
11. sortable content with keyboard/non-drag fallback or an explicit Progressive label;
12. native-first switch/radio/listbox behavior with form submission parity;
13. local-option combobox with IME/mobile/empty-state behavior or an explicit Progressive label;
14. notification queue with interruption, pause, dismissal, and lifecycle behavior;
15. JavaScript/core/plugin/CSP/integrity failure with semantic content and ordinary controls usable,
    including proof that essential content is not permanently cloaked; and
16. component-provenance audit proving W3C/web-platform/first-party inputs and excluding restricted
    Alpine UI source, screencasts, subscriber materials, and copied markup.
17. component-engine corpus proving at least one lightweight Web-Component-to-Alpine migration,
    retained chart/map/data-editor specialist hosts, preserved third-party element ABI behavior,
    and an evidence-backed admission or non-admission for each Web Component promotion candidate.

## Prerelease checkpoints

| Checkpoint | Exit evidence |
|---|---|
| `0.67a0` | `FREEZE-067`, warning registry, compatibility BOM, and supply/CSP candidate decisions |
| `0.67a1` | document closure, assets, directives, security sinks, and CSP grammar |
| `0.67a2` | lifecycle, plugins, state, failure behavior, and Morph admission/non-admission |
| `0.67a3` | bidirectional component-engine dispositions, conversions, and per-family `@alpinejs/ui` decisions |
| `0.67rc1` | complete compatibility/warning/migration, AT/a11y, budget, fleet, docs, and package evidence |
| `1.0a1` | removal/default-switch hardening from the frozen 0.67 subset; no new calling form or capability |

## Explicit exclusions

- Alpine's normal evaluator build or any `unsafe-eval` policy;
- remote CDN runtime/plugins in production;
- arbitrary user/third-party values entering expressions or `x-html`;
- Alpine-owned requests, authorization, domain mutation, durable jobs, or canonical server state;
- implicit runtime/plugin activation, response-time plugin registration, or hidden global stores;
- manual ordinary-page plugin lists that duplicate requirements already owned by canonical
  components/interactions;
- essential content or the only usable control hidden by `x-cloak` before successful initialization;
- dependence on undocumented Alpine initialization/destruction internals;
- a consumer Node/build-tool requirement; and
- a claim that Alpine alone makes a custom widget accessible.
