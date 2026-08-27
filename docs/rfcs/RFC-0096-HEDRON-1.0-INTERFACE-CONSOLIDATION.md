# RFC-0096: Hedron 1.0 interface and HTMX/Alpine interaction consolidation

**Status:** Accepted / Stage 0 Refined; implementation pending
**Target:** `v1.0.0`, after `v0.67.0` Alpine integration is Verified  
**Decision:** D-114, refined by D-115 / D-116 / D-117
**Capability baseline:** Hedron `v0.67.0`; no net-new Required runtime capability  
**Input:** [RFC-0095](RFC-0095-ALPINE-BROWSER-ENHANCEMENT.md), Edron's published authoring facade,
and the 0.67 compatibility inventory  
**Alpine capability/widget audit:**
[ALPINE_CAPABILITY_AUDIT_067](../implementation/ALPINE_CAPABILITY_AUDIT_067.md)  
**Interface audit:**  
[HEDRON_1_0_EDRON_INTERFACE_AUDIT](../implementation/HEDRON_1_0_EDRON_INTERFACE_AUDIT.md)
**0.67 contract freeze:**
[contract-freeze-067.toml](../acceptance/contract-freeze-067.toml)  
**Compatibility BOM:**
[compatibility-bom-067.toml](../acceptance/compatibility-bom-067.toml)
**HTMX/Alpine boundary:**
[HTMX_ALPINE_BOUNDARY_1_0](../api/HTMX_ALPINE_BOUNDARY_1_0.md)
**Component engine dispositions:**
[COMPONENT_ENGINE_DISPOSITIONS_067_1_0](../implementation/COMPONENT_ENGINE_DISPOSITIONS_067_1_0.md)
**1.0 cut contract:**
[one-zero-cut-contract.toml](../acceptance/one-zero-cut-contract.toml)
**Implementation and acceptance:**
[HEDRON_1_0](../implementation/HEDRON_1_0.md) ·
[RELEASE_1_0](../acceptance/RELEASE_1_0.md) ·
[release-gate-1.0.toml](../acceptance/release-gate-1.0.toml)

**Stage 0 revision (2026-08-27):** D-117 rebases the cut plan on Verified Beta `v0.67.0`,
defines the subtractive release/package/maturity/support boundary, records the incomplete warning
registry as an explicit W0 blocker, and freezes 17 Planned release gates plus dual-version upgrade
fixtures. It changes no runtime, package version, maturity classifier, or release claim.

## Summary

Hedron 1.0 is a deliberate developer-interface and frontend-interaction consolidation release. It
uses the major-version boundary to replace today's parallel HTMX helpers, Alpine directives, handle
controls, lifecycle hooks, local-state conventions, and browser activation knobs with one coherent
HTMX/Alpine model. The same boundary removes redundant aliases, overlapping workflow spellings,
compatibility shims, and interfaces whose alternatives have made ordinary application authoring
overwhelming.

The unified model is frozen before 0.67 runtime implementation and ships in 0.67 so 1.0 applications
remain source-compatible with 0.67. Version 1.0 makes it canonical, removes the superseded paths,
and hardens the lifecycle; it does not add a public runtime capability or calling form beyond 0.67.

Edron is a primary design input because it has exercised a smaller, more Pythonic surface over the
same Hedron authorities. Hedron will adopt reusable interface lessons—one obvious entry point,
coherent names, request-scoped ownership, exact lowering, and precise optional-capability errors—
without copying Edron's class facade wholesale or merging the separately versioned packages.

The source-compatibility promise is intentionally reversed from a conventional predecessor
guarantee: every application written solely to Hedron 1.0's public interface must run unchanged on
Hedron 0.67. Applications using 0.67 compatibility, beta, experimental, or removed duplicate paths
may not run on 1.0 until migrated.

## Why a major release is now justified

The 0.x capability program produced broad, evidence-backed depth, but the public surface grew by
addition. At the 0.66.2 planning baseline, static `__all__` inspection finds 409 root `hedron`
exports and 574 root `hedron_core` exports; the existing stability checker reports 1,192 public
exports across nine coordinated packages. Export count is not itself a quality defect, but it is a
useful signal when the same task is reachable through root re-exports, package-native imports,
decorators, handles, response helpers, component helpers, compatibility shims, and experimental
aliases.

Edron provides a counterexample inside the same repository: its deliberately smaller root contract
chooses one `App`, one page model, one `include` escape hatch, typed
fragments/actions, direct native interoperation, and exact lowering. The goal is not to force
Hedron down to an arbitrary export count. The goal is to make the native framework equally
intentional even while Edron's in-development facade continues to change.

This decision supersedes the no-scheduled-1.0 clause of D-038 and the corresponding no-calendar-1.0
wording in D-053. Their capability-based maturity, evidence, and stable-tier rules remain in force.

## Release invariants

1. **0.67 feature freeze.** Hedron 1.0 adds no Required runtime capability, canonical calling form,
   browser feature, host behavior, or package relationship absent from `v0.67.0`.
2. **1.0-on-0.67.** The complete 1.0 documentation example and application fixture corpus executes
   unchanged on both `v0.67.0` and `v1.0.0`.
3. **One clear way.** Each developer task at each abstraction level has exactly one documented,
   scaffolded, generated, and stable public entry point. A lower-level escape hatch is admitted
   only for a distinct capability and is visibly advanced, never an equally recommended spelling.
4. **No hidden authority change.** Consolidation may rename or relocate interfaces; it may not
   move routing, rendering, state, validation, security, HTMX, Alpine, job, or persistence authority.
5. **Evidence before removal.** Every removed 0.67 path has usage evidence, a replacement or explicit
   non-fit disposition, a diagnostic, migration documentation, and an executable before/after fixture.
6. **Package honesty.** A root facade does not pretend optional satellites are installed. Canonical
   package imports remain available when they clarify ownership.
7. **No compatibility layer in 1.0.** Removed interfaces are not silently retained through dynamic
   `__getattr__`, duplicate decorators, or shadow modules. The migration bridge lives in 0.67 and
   tooling, not as permanent 1.0 ambiguity.
8. **No silent 0.67 removal.** Every public 0.67 path absent from 1.0 emits a deprecation warning or
   deterministic target-1.0 static finding in 0.67, with replacement and removal metadata.
9. **No alias residue.** A rename or merge finishes at 1.0; compatibility aliases, dynamic shims,
   class/function route alternatives, and “also spelled” documentation do not enter the stable
   facade.
10. **Freeze before implementation.** `FREEZE-067` locks the task graph, exact canonical
    signatures/returns, interaction/outcome algebra, document browser-feature closure, warning
    registry, and compatibility BOM before 0.67 W1 begins.
11. **Exact matrix.** The 1.0-on-0.67 promise always names tested Python, dependency, adapter,
    satellite, browser, type-checker, CLI, template, and artifact ranges; “Supported matrix” is not
    an unversioned escape clause.

Executable compatibility paths use a visible-by-default structured `HedronFutureWarning`, not a
normally hidden bare `DeprecationWarning`. Static-only config, HDJ, markup, manifest, import, and
CLI uses receive the same warning record from `hedron check --target 1.0`.

## Unified HTMX/Alpine interaction architecture

The normative ownership, handoff, DOM-writer, state-transfer, failure, security, accessibility, and
non-interference contract is
[HTMX_ALPINE_BOUNDARY_1_0](../api/HTMX_ALPINE_BOUNDARY_1_0.md). This RFC summarizes that boundary;
the dedicated contract governs implementation and conformance details.

The 1.0 frontend contract is one interaction graph with two execution lanes:

```text
DOM event
   -> local lane: Alpine state / DOM / focus / presentation
   -> server lane: Hedron handle -> HTMX request / target / swap
                              -> authoritative HTML/result
   -> reconcile: reset / retain / versioned transfer of declared local state
```

One public `Interaction` value contains a closed discriminated effect: `local`, `request`, or
`combined`. Event, fallback, lifecycle presentation, accessibility, reconciliation, and trace
identity surround that closed effect; the model is not a bag of unrelated optional fields. Purely
local interactions compile only to Alpine. Purely server interactions compile to existing
Hedron/HTMX behavior without requiring Alpine. Combined interactions use both lanes and one
lifecycle coordinator. Invalid cross-lane combinations fail construction and static checks.

The revamp must consolidate these currently separate concerns:

| Concern | 1.0 outcome |
|---|---|
| Browser activation | one feature plan for HTMX extensions, Alpine core/plugins, and registered modules |
| Authoring | one task-oriented typed interaction model with one explicit advanced escape hatch |
| State | named local/document/persist/form/operation/domain ownership and reconciliation policy |
| Lifecycle | one init/cleanup/settle/OOB/history/morph coordinator |
| Concurrency | one operation identity/generation/revision model shared with local pending presentation |
| Errors/fallback | one normal HTTP/no-JS, HTMX, and Alpine-enhanced outcome matrix |
| Accessibility | one semantic/keyboard/focus/announcement contract rather than recipe-specific scripts |
| Components | one semantic Hedron component family and engine disposition per task; native/Alpine owns common widgets, while admitted Web Components own specialist browser subsystems; no parallel engine catalogs |
| Diagnostics | one source-mapped trace from Python/HDJ declaration to Alpine/HTMX/rendered facts |
| Testing | one scenario API for local-only, server-only, and combined interactions across swaps/history |

Canonical components and interactions contribute typed feature requirements automatically. The
document plan is the transitive union of the initial tree and declared reachable fragments; later
fragments must be a subset of that installed plan and never register plugins after Alpine starts.
Manual per-page plugin lists are not a second ordinary authoring path. Direct Alpine/module use
carries its requirements through the single Advanced registration surface.

Direct low-level Alpine and HTMX use remains an advanced escape hatch when it has a distinct need,
but it is not a second beginner-facing way to describe the same interaction. Alpine never owns
requests or domain truth; HTMX never becomes necessary for purely local presentation.

The component revamp follows the same rule. Phase 0.67 enhances existing semantic components and
adds missing standards-based widgets; 1.0 consolidates overlaps such as the current dialog and
disclosure families after structured warnings. Every Hedron-owned common widget that needs
enhanced browser-local behavior compiles to a registered Alpine module. Overlapping delegated
controllers, per-widget scripts, and common-widget custom elements leave the 1.0 canonical surface.
It does not publish separate static, headless, HTMX, and Alpine component names for the same task.
Styling and enhancement modes lower from one component contract.

Web Components remain canonical when they provide a real specialist-host boundary. The
[component engine disposition plan](../implementation/COMPONENT_ENGINE_DISPOSITIONS_067_1_0.md)
keeps the public element ABI and third-party author kit, retains chart/map/data-editor hosts, moves
lightweight common wrappers to native/Alpine lowering, and evaluates complex editor, terminal,
upload/media, canvas, and WASM hosts for promotion in the opposite direction. The Python component
name remains stable across engine changes; 1.0 never makes engine selection an ordinary author
choice.

“Alpine is the engine” does not mean “JavaScript is required.” Server-rendered semantics and
adequate native element behavior remain the fallback, pages without local interaction load no
Alpine, and HTMX remains the request/swap lane. Nor does it require rewriting specialist
third-party chart/map/data/editor hosts whose lifecycle is a distinct package capability.
Independently built common-widget behavior follows W3C APG and Hedron evidence; restricted Alpine
UI Components source and subscriber material are not implementation inputs. The separately
MIT-declared official `@alpinejs/ui` package is evaluated as the preferred nine-widget behavior
substrate, not confused with the paid product. Permissively licensed ecosystem code may inform an
implementation only through the 0.67 provenance and conformance gates.

## Interface audit

The complete feature-by-feature Edron comparison and recommended native surface are recorded in
[HEDRON_1_0_EDRON_INTERFACE_AUDIT](../implementation/HEDRON_1_0_EDRON_INTERFACE_AUDIT.md). Its
recommended spine is one `Hedron` application; function-only `page`, `view`, and `action`
registration; one returned presentation tree per page/view; role-indexed closed `Outcome` values;
one discriminated `Interaction`
declaration; and one `app.include(...)` feature path. It rejects Edron's class-page DSL, implicit
output buffer, and broad display-method facade as poor fits for native Hedron workflows.

`@app.page(...)` owns the document shell, title, layout, head, and browser metadata; its function
returns one presentation tree. Multiple siblings use the explicit composition node. Direct `Page`
construction remains an Advanced render/adapter capability rather than a second canonical page-
handler result. Views return one presentation tree. Actions return the one role-valid `Outcome`
family; raw response objects remain limited to Advanced raw HTTP routes.

Before signatures are frozen, every documented symbol, import path, decorator, CLI/config field,
markup contract, manifest, diagnostic, and browser activation path is assigned one disposition:

| Disposition | Meaning in 1.0 |
|---|---|
| `canonical` | Preferred public path; available unchanged in 0.67 and 1.0 |
| `advanced` | Public lower-level escape hatch with a distinct non-overlapping use case |
| `compatibility` | Runs in 0.67, removed in 1.0 with a deterministic replacement |
| `merge` | Several 0.67 paths normalize to one canonical 1.0 interface |
| `package-native` | Public from its owning package, not duplicated through the root facade |
| `experimental` | Excluded from the 1.0 promise or moved behind an explicit experimental namespace |
| `internal` | No public compatibility promise; removed from exports/docs |
| `defer` | Valid concern, but not part of the 1.0 cut |

The audit is task-oriented, not just alphabetical. It covers application construction, page and
route registration, composition/rendering, components and HTML, forms/actions, refreshable views,
responses/updates, state/cache/jobs, data/charts/maps, styling/themes, browser features, security,
testing, plugins, adapters, manifests, and deployment.

For each task the audit compares:

- current native beginner and advanced examples;
- Edron's spelling and exact Hedron lowering;
- stability level and real consumer usage;
- typing, diagnostics, inspectability, and source mapping;
- whether two spellings have meaningfully different semantics; and
- the cost of migration versus the ongoing cost of ambiguity.

## Design rules learned from Edron

Hedron should adopt these general lessons where the native audit supports them:

- one explicit application object and one obvious registration vocabulary;
- coherent class/function naming rather than aliases chosen by historical phase;
- typed direct arguments instead of callback `args`/`kwargs` bags or stringly attribute maps;
- one body-level composition escape hatch for arbitrary native renderables;
- one interaction model that exposes ordinary requests, effects, fallbacks, and native handles;
- exact optional dependency errors at the call site, with owning-package imports kept clear;
- source-mapped lowering visible in check, inspect, Explorer, and tests; and
- progressive disclosure: the common path is compact while advanced native authority remains
  accessible without a second framework.

Hedron should not copy Edron's request-local output buffer, page-class DSL, Streamlit-inspired
vocabulary, or batteries-included packaging into core merely for symmetry. Edron remains a separate
facade and a design customer.

The Edron lesson is stricter than “prefer” or “golden path”: when two public interfaces perform the
same task with the same authority, the audit chooses one and migrates the other out of 1.0. Classes
remain appropriate for models, reusable components, services, policies, and feature providers, but
not as a second route-authoring syntax beside functions.

## Work program

### Stage 0A — freeze the 1.0 contract before 0.67 W1 (complete)

- generate the complete API/artifact inventory and task-to-interface graph;
- run native and Edron golden applications through the same outcome matrix;
- record import count, concepts required, annotations/signatures, diagnostic quality, and escape
  frequency without treating line count alone as the goal;
- publish proposed dispositions and migration examples before removing anything;
- freeze exact public imports, signatures, role-specific returns, interaction/outcome variants,
  browser-feature closure, warning records, and the compatibility BOM; and
- make `FREEZE-067` a hard entry gate for W1, with tests that reject accidental post-freeze
  additions or alternate calling forms.

### Stage 0B — refine the cut against Verified 0.67 (D-117)

- generate the complete public/task/artifact inventory from immutable `v0.67.0` artifacts;
- reconcile every proposed removal with the 0.67 runtime/static warning registry and a fixture;
- treat the three existing route/include warnings as a known floor rather than inventory closure;
- enumerate the stable symbol/package inventory and keep Beta/Experimental surfaces outside it;
- materialize the canonical/transitional/negative/rollback dual-version fixture lanes;
- publish the exact matrix and 0.67.x migration-support window before the cut; and
- keep `ENTRY-100` Planned and removal work blocked until those artifacts are complete.

### Stage 1 — make 0.67 the migration bridge

- ensure every canonical 1.0 import, signature, config, CLI form, and browser feature exists in
  `v0.67.0`;
- emit precise deprecations for every path accepted for removal, including browser arguments,
  directive/attribute spellings, config, HDJ features, CLI forms, imports, and dynamic shims;
- add `hedron check --target 1.0` with deterministic text/JSON/SARIF output;
- add a reviewable `hedron migrate api --target 1.0` transform that never imports or executes the
  application and never overwrites without an explicit output/apply choice;
- publish before/after fixtures for every mechanical and manual migration; and
- maintain a `0.67-only`, `shared`, and `1.0-canonical` symbol/artifact manifest.

The bridge uses one structured warning registry. “Public 0.67” means every documented, exported,
generated, configured, CLI, HDJ, or browser-markup contract, including beta/experimental contracts;
private underscore/internal implementation details are excluded. Each removed executable path warns once per
source callsite with code, replacement or non-fit reason, owner, first-warning/removal versions,
documentation anchor, and automation status. Static-only uses produce equivalent target-1.0
warning findings. Static analysis records `complete`, `partial`, or `unknown` confidence and reports
dynamic imports, generated keyword bags, reflection, and opaque templates as incomplete rather than
claiming a clean migration.

### Stage 2 — cut 1.0 from the frozen subset

- remove accepted compatibility paths and dynamic root shims;
- make the unified HTMX/Alpine interaction declaration and lifecycle coordinator canonical;
- reduce root re-exports to the canonical facade plus clear owning-package imports;
- make docs, templates, scaffolds, examples, Explorer, and generated code use only canonical paths;
- run the full behavior, typing, security, a11y, browser, packaging, migration, and rollback suites;
  and
- publish a major-version migration guide organized by developer task rather than module history.

## Compatibility model

The promise applies to documented public 1.0 application source, configuration, templates, and CLI
forms within the exact [compatibility BOM](../acceptance/compatibility-bom-067.toml). It does not claim that a wheel built against 1.0 metadata can be
installed into a 0.67 environment without dependency resolution, nor that private internals or
serialized Python objects are portable backward.

The conformance corpus must demonstrate:

```text
source/app/config fixtures authored for 1.0
       ├── execute and type-check on Hedron 0.67.0
       └── execute and type-check on Hedron 1.0.0

0.67 compatibility/transitional fixtures
       ├── execute on 0.67.0 with a migration disposition
       └── may fail on 1.0.0 with a precise replacement diagnostic
```

If a necessary 1.0 correction cannot be expressed on 0.67, it is either backported into a 0.67
patch before the 1.0 cut or deferred until 1.1. It is not silently added only to 1.0.

## Semantic versioning after 1.0

The accepted canonical 1.0 surface follows semantic versioning. Stable public interfaces require a
new major for incompatible change. Additive 1.x work must preserve authority and compatibility
rules. Beta/experimental surfaces retain visibly weaker promises, but must remain out of the stable
facade and inventories. Independently versioned satellites keep their own major lines and explicit
Hedron compatibility ranges; the coordinated train does not force unrelated satellites to `1.0.0`.

## Non-goals

- rewriting the runtime or reimplementing capabilities solely to make the version number larger;
- collapsing `hedron-core`, the flagship, adapters, and satellites into one distribution;
- copying all Edron APIs into Hedron or removing Edron;
- removing advanced interfaces that have a distinct, evidence-backed use case;
- preserving every 0.67 beta/experimental spelling in 1.0;
- making Alpine mandatory on pages without an admitted local-interaction demand, making HTMX
  mandatory for purely local presentation, or making Web Components, live transports, Node, or
  optional satellites globally mandatory; or
- claiming 1.0 means every package/capability is Supported, GA, or human-AT verified.

## Acceptance criteria

The 1.0 cut requires accepted interface and removal inventories, a frozen canonical surface already
present in `v0.67.0`, complete 1.0-on-0.67 fixtures, zero undocumented removals, deterministic check
and migration tooling, proof that every removal warned in 0.67, unified HTMX/Alpine local/server/
combined interaction fixtures, task-oriented migration/rollback documentation, clean wheel/sdist
installs, a docs/API lint proving one stable path per audited task, user evidence that no “which
API?” decision page is needed, and the full supported behavior/security/a11y/browser/package
regression matrix. Contract/removal/compatibility gate IDs and commands freeze in `FREEZE-067`
before 0.67 W1. Artifact-derived numeric budgets and per-browser implementation thresholds may be
refined by recorded Stage 0 evidence, but may not change the public 1.0 calling forms or compatibility
direction.
