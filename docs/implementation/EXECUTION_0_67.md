# Phase 0.67 full implementation execution plan

**Status:** Planned implementation sequence  
**Authority:** [RFC-0095](../rfcs/RFC-0095-ALPINE-BROWSER-ENHANCEMENT.md), refined by D-115 / D-116  
**Successor:** [RFC-0096](../rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md)  
**Implementation contract:** [ALPINE_INTEGRATION_067](ALPINE_INTEGRATION_067.md)  
**Acceptance:** [RELEASE_0_67](../acceptance/RELEASE_0_67.md)  
**Baseline:** Verified Hedron `v0.66.2`  
**Target:** `v0.67.0`

This document turns the Phase 0.67 specification into an executable delivery sequence. The
implementation specification defines the subsystem seams; the acceptance packet defines the gates;
this plan defines what lands, in what order, and what evidence permits the next step.

## Implementation objective

Deliver one demand-driven Alpine browser-local path through Hedron's existing rendering, asset,
security, interaction, HTMX, component, HDJ, diagnostics, and packaging authorities:

```text
Python / HDJ declaration
        -> typed feature demand + directive / interaction facts
        -> immutable document plan and asset manifest
        -> semantic HTML + Alpine CSP projection
        -> disposable local presentation state
        -> explicit HTMX / Hedron lifecycle handoff
```

Phase 0.67 is complete only when the browser-local path, the 1.0-compatible canonical interface,
the component-engine dispositions, and the migration bridge are all evidenced together. A working
Alpine demo by itself is not phase completion.

## Non-negotiable invariants

1. `FREEZE-067` is the W0 exit and W1 entry gate. No W1 runtime implementation starts while it is
   Planned.
2. The 0.66.2 behavior remains the upgrade baseline. Existing pages without Alpine demand emit no
   Alpine asset, marker, observer, store, directive, or request.
3. Alpine owns disposable local presentation state, local DOM behavior, focus, geometry, and
   preferences. Hedron/HTMX own requests, HTML placement, authorization, validation, mutation,
   domain truth, jobs, and server outcomes.
4. One immutable document plan covers the initial presentation tree and the transitive closure of
   statically declared reachable fragments. A response cannot register a plugin, module, store, or
   executable asset.
5. The normal Alpine evaluator, `unsafe-eval`, remote production assets, response scripts, a
   consumer Node build, and hidden global state are excluded.
6. Python and HDJ produce the same normalized directive, feature-demand, interaction, provenance,
   and warning facts.
7. Every ordinary task has one canonical Python/component name and one browser-engine disposition.
   Web Component ABI and third-party authoring remain supported for specialist hosts.
8. Ordinary replacement/reset is Supported. Morph is at most one separately admitted Progressive
   path and may be non-admitted without blocking the base release.
9. Essential semantic content and ordinary forms/links remain usable with JavaScript disabled,
   missing/refused assets, integrity failure, plugin failure, or slow initialization.
10. Every documented/exported/generated/configured 0.67 path absent from 1.0 has a visible
    `HedronFutureWarning` or deterministic `hedron check --target 1.0` finding.

## Entry lock: Stage 0 / W0

The entry packet already exists in the repository. Before runtime work begins, make it executable
and reproducible:

- [ ] `scripts/check_067.py --check-plan` passes and validates all 30 gate rows, packet references,
      contract decisions, engine inventory, and compatibility claims.
- [ ] The `v0.66.2` unit, browser, adapter, HDJ, package, docs, and security baselines are recorded
      with commit, Python, browser, dependency, and operating-system identity.
- [ ] The exact Alpine `3.16.3` CSP candidate, nine official plugins, and the `@alpinejs/ui`
      candidate are reproduced locally with hashes, licenses, notices, dependency order, raw/gzip
      sizes, and provenance. No source is copied from restricted Alpine UI material or an unclear
      license.
- [ ] The expression corpus is run in Chromium, Firefox, and WebKit. Assignment, member
      assignment, calls, async values, getters, arrays/objects, comparisons, magic values, errors,
      and prohibited global/HTML injection cases receive machine-readable dispositions.
- [ ] The current `Page.scripts`, `Page.htmx_extensions`, application assets, browser-module
      registry, Web Components, controllers, HDJ helpers, and CLI/config entry points are inventoried
      against the 1.0 audit.
- [ ] The function-only `page` / `view` / `action` spine, one-tree returns, closed role-indexed
      `Outcome`, discriminated `Interaction`, `hedron.ui`, and `app.include(...)` forms have exact
      signatures, return schemas, diagnostics, and dual-version fixtures.
- [ ] The component-engine inventory assigns every current tag/controller/module/provider host one
      preliminary disposition and one owner. The public element ABI and third-party author kit have
      explicit continuity fixtures.
- [ ] Warning records have a stable schema for runtime, import, generated, CLI, configuration,
      HDJ, manifest, and browser-markup paths, including replacement/non-fit reason, removal
      version, source, fixture, and complete/partial/unknown confidence.
- [ ] The compatibility BOM freezes Python, FastAPI, Pydantic, adapters, satellites, Alpine/HTMX
      artifacts, browsers, OS revisions, Pyright, CLI/config/HDJ schemas, and fixture constraints.
- [ ] Baselines and budgets cover feature-off bytes/requests, feature-on assets, Alpine init and
      DOM walk, observers, swap cleanup, repeated lifecycle operations, browser traces, diagnostics,
      and package artifacts.

Stage 0 may amend scope or maturity from probe evidence. It may not weaken security, authority,
fallback, or compatibility invariants. Once `FREEZE-067` is Verified, a new canonical spelling,
second engine choice, or silent 1.0 removal is prohibited.

## Repository seam map

| Authority | Existing seam | Phase 0.67 extension |
|---|---|---|
| HTML and trust policy | `packages/hedron-core/src/hedron_core/_html/`, `html.py`, `htmx/attrs.py` | Normalize long-form Alpine directives and recheck sink-specific text, boolean, ARIA, class, style, URL, DOM-property, and expression rules at serialization. |
| Registry and browser assets | `application_assets.py`, `page_assets.py`, `head_support.py`, `registry/browser_module.py`, `registry/asset.py`, `registry/builder.py` | Register exact CSP core/plugins/modules, dependency order, integrity, provenance, feature demand, and document-plan fingerprint. |
| Render and route graph | `packages/hedron-core/src/hedron_core/rendering/`, `packages/hedron/src/hedron/app/`, `packages/hedron/src/hedron/build/` | Collect demands from trees and declared reachable fragments; enforce fragment subsets and feature-off zero cost. |
| HTMX lifecycle | `packages/hedron-core/src/hedron_core/htmx_064.py`, `htmx_extensions.py`, `packages/hedron/src/hedron/htmx.py` | Add documented Alpine init/cleanup/settle/OOB/delete/history outcomes without taking request or HTML authority. |
| Interaction authority | `packages/hedron-core/src/hedron_core/interaction.py`, `packages/hedron/src/hedron/interaction/`, `interactions.py` | Add closed `Interaction` lowering and role-indexed `Outcome` validation without a third runtime. |
| Component engine | `component.py`, `registry/component.py`, `registry/element.py`, built-ins, `hedron-elements` | Apply the frozen native/Alpine/Web Component/provider/fixture dispositions; preserve specialist ABI and third-party authoring. |
| HDJ | `packages/hedron-jinja/src/hedron_jinja/` and `tests/jinja/` | Normalize the same Alpine facts and check them without executing templates or exposing raw requests/registries. |
| Tooling and Explorer | `packages/hedron/src/hedron/cli/`, `packages/hedron-explorer/`, scenario/conformance helpers | Add deterministic inspect/check/trace/scenario outputs, target-1.0 findings, migration inventory, and redaction. |
| Static/browser assets | `packages/hedron-core/src/hedron_core/static/`, package manifests, notices | Vendor only exact local CSP assets and admitted plugins; expose demand-driven manifests and offline artifacts. |
| Evidence and release | `docs/acceptance/`, `scripts/check_067.py`, `scripts/ci_checks.sh`, CI workflows | Replace planning guards with gate verifiers, retain reports, run the full browser/package matrix, and cut only from a verified commit. |

## Milestones and dependency graph

| Milestone | Work packages | Depends on | Primary exit evidence |
|---|---|---|---|
| E0 — entry lock | W0 | — | `FREEZE-067`, `CONTRACT-067`, `BOM-067` packet is executable; W1 remains blocked until freeze. |
| E1 — supply and CSP | W0 | E0 | `SUPPLY-067`, `CSP-067`; exact artifacts, licenses, hashes, expression corpus, and no `unsafe-eval`. |
| E2 — document plan and assets | W1 | E0–E1 | `PLAN-067`, `CLOSURE-067`, `ASSET-067`; closure, fingerprint, subset rejection, ordering, integrity, and feature-off proof. |
| E3 — typed directives and sinks | W2 | E0–E2 | `DIRECTIVE-067`, `SECURITY-067`; Python/HDJ normalization, safe serialization, typed expressions, and adversarial rejection. |
| E4 — interaction and outcome spine | W5 | E0, E3 | `INTERACTION-067`; valid local/request/combined lowering and construction/static rejection of illegal combinations. |
| E5 — Alpine capability surface | W3–W4 | E1–E3 | `CORE-067`, `PLUGIN-067`, `UI-067`; per-feature maturity, demand loading, and vertical slices. |
| E6 — lifecycle and state | W6–W7 | E2–E5 | `HTMX-067`, `MORPH-067`, `STATE-067`; init/cleanup/swap/OOB/history/focus/state-transfer evidence. |
| E7 — engine and widgets | W9 | E4–E6 | `ENGINE-067`, `WIDGET-067`, `A11Y-067`; one disposition per task, parity fixtures, accessible common widgets, retained specialist hosts. |
| E8 — authoring and tooling | W8 | E3–E7 | `AUTHOR-067`, `HDJ-067`, `TOOLING-067`; Python/HDJ/catalog/Explorer/CLI/scenario parity and bounded traces. |
| E9 — failure, security, performance | W10 | E5–E8 | `FAILURE-067`, `SECURITY-067`, `PERF-067`; failure matrix, leak cleanup, budgets, and three-browser evidence. |
| E10 — migration bridge | W11 | E0, E4, E8 | `COMPAT-067`, `DEPRECATE-067`, `BOM-067`; complete warnings/findings, conservative migration fixtures, 1.0-on-0.67 corpus. |
| E11 — fleet and release docs | W12 | E2–E10 | `DOCS-067`, `REGRESS-067`, `PKG-067`; adapters, examples, notices, clean artifacts, and release rehearsal. |
| E12 — cut authorization | all | E0–E11 | Every Required gate Verified; no undocumented Deferred row; final report and rollback packet approved. |

The critical path is `E0 → E1 → E2 → E3 → E4 → E6 → E7 → E8 → E9 → E10 → E11 → E12`.
E5 can run in parallel after E3 for features whose demand model is stable. E10 cannot begin removal
claims before the canonical interface and warning registry are frozen; E11 cannot publish package
metadata while runtime gate rows remain Planned.

## Work package execution

### W0 — freeze the contract and evidence machinery

1. Validate and then extend `scripts/check_067.py` with gate-specific verifiers as each runtime
   slice lands. Keep `--check-plan` separate from runtime verification; the current planning guard
   must never report a Planned gate as Verified.
2. Add machine-readable inventories for feature maturity, directives/sinks, state owners, warnings,
   component engines, browser assets, budgets, fixtures, and issue-to-gate ownership.
3. Record the baseline report and exact artifact/provenance packet. Store reports in the evidence
   bundle, not generated build output in source directories.
4. Freeze the public names, signatures, returns, discriminants, closure rules, warning schema, and
   compatibility BOM. Review the packet as an API change before opening W1 implementation work.

**Exit:** `FREEZE-067` and `CONTRACT-067` are Verified; the packet is reproducible; W1 is unblocked.

### W1 — build the immutable document browser plan

1. Introduce one normalized feature-demand representation consumed by components, `Interaction`
   values, typed Alpine values, and the Advanced registered-module path.
2. Collect demands from the initial presentation tree and statically declared reachable views and
   fragments. Reject unknown/dynamic closure or require an explicit Advanced declaration.
3. Produce a versioned plan fingerprint and add it to the applicable HTMX request facts. A fragment
   may consume only a subset of the installed plan.
4. Extend the existing asset graph for exact Alpine core/plugins/modules, dependency order,
   deduplication, integrity, local/offline manifests, and feature-off omission.
5. Preserve `Page.scripts` and `Page.htmx_extensions` as compatibility inputs by normalizing them
   into the same plan and inventorying their 1.0 dispositions.

**Exit:** `PLAN-067`, `CLOSURE-067`, and `ASSET-067` prove deterministic closure, asset ordering,
subset rejection, no response-time registration, and zero feature-off Alpine output.

### W2 — normalize typed directives and trust sinks

1. Add the single `AlpineAttrs`-style value to normal Python components and `html.*` attributes.
2. Canonicalize long-form `x-on:*` and `x-bind:*`; validate finite event/modifier, selector,
   transition, mask, and plugin options.
3. Implement sink-specific values for scalar/text, boolean, ARIA, admitted class tokens, typed style
   properties/tokens, `SafeUrl` purposes, and DOM properties. Reject generic runtime attribute maps.
4. Add the small CSP-verified expression AST and one reviewed Advanced expression escape hatch.
   Untrusted strings, request values, user content, arbitrary `x-html`, and unreviewed globals never
   become executable.
5. Emit provenance into manifests, diagnostics, Explorer, HDJ facts, and traces while redacting
   secrets and sensitive state.

**Exit:** `DIRECTIVE-067` and `SECURITY-067` pass construction, serialization, manifest, HDJ, and
negative-input corpora without policy bypass.

### W3–W4 — implement capability and plugin parity

1. Implement the pinned CSP core and only the exact official plugin/UI artifacts admitted by Stage 0.
2. Add a machine-readable disposition for every documented core directive, magic, global, and
   official plugin. “Dispositioned” does not mean “Supported.”
3. Register plugins before the single Alpine start, deduplicate by logical identity, and fail closed
   on duplicate starts, missing dependencies, failed registration, or asset mismatch.
4. Implement the Required core verticals first: local state, events/modifiers, model/form behavior,
   `x-show`/`x-if`, IDs/refs, focus, collapse, anchor, intersect, resize, and masked native input.
5. Evaluate `@alpinejs/ui` family by family. If a family fails license, CSP, browser, lifecycle,
   accessibility, stability, or budget evidence, record its fallback/maturity rather than forking
   or silently claiming support.

**Exit:** `CORE-067`, `PLUGIN-067`, and `UI-067` have executable evidence and explicit maturity for
every candidate; no unadmitted upstream source enters the tree.

### W5 — implement the unified interaction and outcome model

1. Add the frozen closed `Interaction` discriminant: `local`, `request`, or `combined`.
2. Add the role-indexed closed `Outcome` family and validate action returns before lowering.
3. Lower local effects to Alpine, request effects to existing Hedron/HTMX handles, and combined
   effects through one lifecycle coordinator. Do not add a client request or domain-state authority.
4. Reject duplicate dispatch, dual DOM writers, cross-lane state ownership, invalid target/swap
   combinations, and unauthorized client-derived outcomes at construction and static-check time.
5. Add one scenario fixture for each lane plus a combined form/action/fragment flow with HTTP and
   no-JavaScript fallback.

**Exit:** `INTERACTION-067` proves exact lowering, illegal-state rejection, identity, fallback,
accessibility, and trace behavior.

### W6–W7 — settle HTMX lifecycle, state, and Morph

1. Integrate Alpine roots with the documented HTMX lifecycle: init, cleanup, settle, OOB, delete,
   history restoration, errors, and Alpine-created HTMX content.
2. Make initialization and cleanup idempotent and observable. Every listener, observer, timer,
   store, object URL, and module resource has an owning cleanup boundary.
3. Define reset as the ordinary replacement behavior. Preserve local state only through explicit,
   bounded, versioned transfer rules for the declared state class.
4. Compare normal replacement, Alpine Morph, community Morph integration, and a Hedron adapter.
   Admit no more than one Alpine-aware Morph path, and only as Progressive after identity, focus,
   stale-state, cleanup, and three-browser evidence.
5. Test OOB and history behavior with deterministic reset/preserve semantics and no duplicate
   announcements, requests, or DOM writers.

**Exit:** `HTMX-067`, `MORPH-067`, and `STATE-067` pass the lifecycle and state corpus; a Morph
non-admission is a valid complete result.

### W8 — wire authoring consumers and tooling

1. Project the same normalized facts through Python components, HTML primitives, recipes, registry,
   catalog, adapters, and HDJ.
2. Add HDJ declaration and static checking without executing templates, expressions, manifests,
   browser modules, or application code.
3. Add deterministic `check`, `inspect`, Explorer, scenario, and browser-trace output for demands,
   plan fingerprints, state ownership, lifecycle events, warnings, CSP findings, and failures.
4. Keep direct Alpine/module use behind one explicit Advanced registration path. Do not add ordinary
   manual per-page plugin lists or a parallel directive API.

**Exit:** `AUTHOR-067`, `HDJ-067`, and `TOOLING-067` pass Python/HDJ equivalence, source mapping,
redaction, bounded output, and non-execution tests.

### W9 — complete the engine and widget program

1. Apply the frozen selection ladder: native HTML, Alpine enhancement, specialist Web Component,
   provider-owned component, fixture, or non-fit.
2. For each engine change, land behavior-parity fixtures before changing lowering. Preserve the
   public Python component name and Web Component ABI where applicable.
3. Migrate only evidence-backed common wrappers to native/Alpine. Retain chart, map, data-editor,
   and other specialist hosts when their resource/lifecycle boundary justifies them.
4. Implement or disposition disclosure, overlays, menus, tabs, choice controls, notifications,
   tooltip, carousel, listbox, combobox, field helpers, and sortable patterns using one Hedron
   component family. Do not create an `Alpine*` parallel catalog.
5. Require semantic initial HTML, keyboard/focus/ARIA behavior, no-JavaScript fallback, HTMX cleanup,
   reduced motion, forced colors, RTL/reflow, provenance, and license evidence for every admitted
   widget. Keep complex or uncertain widgets Progressive rather than overstating support.

**Exit:** `ENGINE-067`, `WIDGET-067`, and `A11Y-067` prove one task/one engine, parity, ABI
continuity, accessible fallback, and provenance.

### W10 — failure, security, performance, and cleanup closure

1. Exercise JavaScript disabled, Alpine/core/plugin 404, integrity mismatch, CSP refusal, plugin
   registration failure, and slow-start paths. Prove `x-cloak` never hides the only usable content
   or control.
2. Run adversarial inputs for expressions, HTML, globals, URLs, selectors, storage, response
   registration, secrets, DOM properties, and cross-tenant/client-derived state.
3. Measure feature-off and feature-on bytes, requests, initialization, DOM walks, observers, swaps,
   cleanup, repeated mount/unmount, and browser memory/leak indicators against frozen budgets.
4. Run Chromium, Firefox, and WebKit coverage for lifecycle, focus, announcements, forms, OOB,
   history, generated content, no-JS, reduced motion, forced colors, zoom, RTL, and responsive cases.

**Exit:** `FAILURE-067`, `SECURITY-067`, and `PERF-067` pass exact-limit and one-over-limit tests;
no failing Required behavior is hidden by a maturity relabel without an amendment.

### W11 — build the 1.0 migration lane

1. Implement visible-by-default structured `HedronFutureWarning` for runtime paths and the equivalent
   deterministic target-1.0 finding for static-only imports, config, HDJ, markup, manifests, CLI,
   and generated code.
2. Give every removal one replacement or explicit non-fit reason, owner, first-warning version,
   removal version, source/documentation anchor, automation status, fixture, and confidence.
3. Add conservative migration analysis/codemods only where the transformation is complete and
   semantics-preserving. Unknown or partial cases must remain findings requiring review.
4. Run the complete canonical 1.0 application corpus unchanged on 0.67. Run representative
   transitional 0.67 paths and confirm they warn without changing server authority or fallback.
5. Enforce one canonical task path with docs/API/static lint. Compatibility aliases remain in 0.67
   only and do not enter 1.0.

**Exit:** `COMPAT-067`, `DEPRECATE-067`, and `BOM-067` prove 1.0-on-0.67 compatibility, no silent
removals, deterministic findings, and exact matrix coverage.

### W12 — fleet adoption, docs, package, and release

1. Migrate the reference application and starters first, then built-ins, HDJ, Explorer, FastAPI,
   Flask, Django, `hedron-elements`, charts, maps, data, extras, workbench, notebook, simulation,
   MCP, and Gradio consumers according to their disposition.
2. Add the required vertical slices and no-backend examples to the docs. Every example states its
   browser feature demand, fallback, authority boundary, maturity, and migration status.
3. Run clean wheel/sdist/offline installation tests, verify local asset inclusion, notices, manifests,
   signatures/provenance, coordinated dependency ranges, and no accidental Node requirement.
4. Replace planning guards in `scripts/check_067.py` with gate-specific verifiers. Update the release
   manifest only when the verifier consumes real evidence and all Required rows are green.
5. Produce the final gate report, evidence bundle, changelog, upgrade notes, rollback instructions,
   and version authorization. Tag/package/publish only after release rehearsal succeeds.

**Exit:** `DOCS-067`, `REGRESS-067`, and `PKG-067` are Verified and E12 authorizes the cut.

## Pull-request sequence

Each PR names its work package, gates advanced, compatibility effect, security/accessibility impact,
budget impact, test command, evidence artifact, and rollback. Split a package when its browser or
artifact evidence is too large to review as one change.

1. **Entry lock:** W0 inventories, contract freeze, BOM, asset provenance, budgets, warning schema,
   and `check_067.py --check-plan`.
2. **Supply/CSP:** exact local Alpine candidates, licenses/notices, expression corpus, and CSP
   rejection tests.
3. **Document plan:** demand graph, reachable-fragment closure, fingerprint, subset failure, and
   asset ordering/manifest integration.
4. **Directive sinks:** typed Alpine attributes, expressions, serializer policy, provenance, and
   negative security corpus.
5. **Interaction spine:** `Interaction`, `Outcome`, lowering, illegal-state rejection, and scenario
   fixtures.
6. **Core/plugins:** CSP core, Required directives/magics/globals, official plugins, and UI family
   dispositions with feature-demand tests.
7. **Lifecycle/state:** HTMX bridge, cleanup, OOB/history, reset/preserve, and Morph decision.
8. **Engine/widgets:** component-engine conversions/retentions, common widget recipes, parity,
   accessibility, and provenance evidence.
9. **Consumers/tooling:** Python, HDJ, registry, Explorer, CLI, scenario, traces, and adapters.
10. **Hardening:** failure, security, browser/a11y, performance/leak, and package matrix.
11. **Migration:** warnings, target-1.0 checks, conservative codemods, dual-version corpus, and
    one-canonical-path lint.
12. **Fleet/release:** docs, reference app, package artifacts, full regression, final gate report,
    release rehearsal, and cut authorization.

## Gate-to-evidence matrix

| Evidence group | Gates | Required retained evidence |
|---|---|---|
| Contract and supply | `FREEZE-067`, `CONTRACT-067`, `SUPPLY-067`, `BOM-067` | TOML locks, task graph, exact hashes/licenses, provenance/SBOM, baseline and compatibility matrix. |
| Plan and syntax | `PLAN-067`, `CLOSURE-067`, `ASSET-067`, `DIRECTIVE-067`, `CORE-067` | Demand/closure fixtures, plan fingerprints, manifests, serializer corpus, expression dispositions, feature-off proof. |
| Extensions and interaction | `PLUGIN-067`, `UI-067`, `INTERACTION-067` | Per-plugin maturity, UI family decisions, local/request/combined scenarios, invalid-state diagnostics. |
| Lifecycle and state | `HTMX-067`, `MORPH-067`, `STATE-067` | Three-browser swap/OOB/history traces, init/cleanup counts, focus/state transfer, Morph admission or non-admission. |
| Consumers and diagnostics | `AUTHOR-067`, `HDJ-067`, `TOOLING-067` | Python/HDJ parity, non-executing checks, redacted traces, Explorer/scenario output, source maps. |
| Engines and UX | `ENGINE-067`, `WIDGET-067`, `A11Y-067` | Complete inventory, parity fixtures, ABI tests, APG/keyboard/focus/no-JS/RTL/forced-colors evidence, license provenance. |
| Hardening | `FAILURE-067`, `SECURITY-067`, `PERF-067` | Failure matrix, adversarial corpus, exact-limit/one-over-limit measurements, cleanup/leak reports. |
| Migration and release | `COMPAT-067`, `DEPRECATE-067`, `DOCS-067`, `REGRESS-067`, `PKG-067` | Warning registry/findings, dual-version fixtures, docs lint, full CI, clean artifacts, release bundle. |

Every evidence artifact names the commit, environment, command, inputs, output digest, gate, owner,
and maturity disposition. Narrative checkboxes are indexes only; they do not close a gate.

## Verification sequence

Use the planning checker while the phase is unimplemented:

```text
python scripts/check_067.py --check-plan
```

As each runtime gate is implemented, replace its planning guard with a verifier and run the exact
gate command recorded in `docs/acceptance/release-gate-0.67.toml`:

```text
python scripts/check_067.py --gate <GATE-067> --verify
```

The final rehearsal must include the repository suites and package/release checks using the frozen
0.67 matrix. At minimum, run the shared test, quality, docs, browser, evidence, and packaging
suites, all three browser engines, the 0.67 gate version, clean package builds, and the release
gate verifier. Credential-gated host checks are included when their declared environments exist;
otherwise their documented disposition remains explicit.

Do not mark a gate Verified from a happy-path test alone. Repeatability, feature-absent behavior,
malformed input, exact limits, one-over-limit behavior, fallback, redaction, and clean-artifact
checks are part of the gate evidence.

## Stop conditions and rollback

Return to W0 or the owning milestone when:

- a Required contract is being changed after `FREEZE-067` without a recorded decision;
- a second registry, document plan, state store, lifecycle coordinator, renderer, router, or
  browser runtime is proposed;
- an Alpine feature requires `unsafe-eval`, remote production assets, response-time registration,
  hidden global state, consumer Node, or undocumented upstream lifecycle internals;
- a fragment can demand an absent plugin/module or register one during response handling;
- a common task exposes native, Alpine, and Web Component variants as peer ordinary APIs;
- a widget lacks semantic/no-JS fallback, focus/keyboard behavior, cleanup, provenance, or maturity;
- an engine conversion lacks parity, ABI, lifecycle, security, accessibility, or budget evidence;
- essential content is hidden by `x-cloak` or an asset failure changes server behavior;
- a budget is exceeded, a leak appears, or a browser engine diverges without an amendment;
- migration analysis reports uncertain code as clean or a public removal lacks a warning/fixture; or
- any gate is being waived, downgraded, or closed from prose alone.

The safe rollback is declaration- and artifact-level: stop emitting the new Alpine demand from the
affected component/interaction, retain semantic server HTML and ordinary HTMX behavior, remove the
unverified asset/module from the document plan, and restore the last verified 0.66.2-compatible
path. Never leave a partially registered plugin, stale plan fingerprint, half-applied DOM transfer,
or silent compatibility removal. A release rollback removes the 0.67 package/artifact from the
deployment channel and restores the prior coordinated train; it does not erase evidence or mutate
consumer application source.

## Release handoff

E12 produces one reviewable packet containing:

- final contract freeze, compatibility BOM, asset hashes/licenses/notices, and engine/widget
  inventories;
- all 30 gate reports with command, commit, environment, owners, and retained artifact digests;
- required vertical-slice fixtures and three-browser lifecycle/failure/accessibility results;
- Python/HDJ/CLI/Explorer/scenario parity and target-1.0 migration findings;
- performance, cleanup/leak, security/redaction, no-JavaScript, package, and offline-install
  evidence;
- upgrade notes from 0.66.2, warning/removal inventory, rollback instructions, and release notes;
- clean wheel/sdist verification and the exact version authorization for `v0.67.0`.

The phase is ready to publish only when `RELEASE_0_67` reports every Required gate Verified, all
non-Required rows have explicit dispositions, the 1.0-on-0.67 corpus passes, and the final artifacts
are reproducible from the authorized commit.
