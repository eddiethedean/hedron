# RFC-0073: Package-native typed workflows

**Status:** Accepted<br>
**Target phase:** 0.46 (`v0.46.0`)<br>
**Decision:** D-075<br>
**Stage 0 contract refine:** D-079<br>
**Planning baseline:** Published in-tree `v0.45.0` (D-079; original Stage 0 baseline was Published `v0.42.0`)<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.45.0`<br>
**Extends:** RFC-0010, RFC-0011, RFC-0014, RFC-0019, RFC-0021, RFC-0024, RFC-0027,
RFC-0033, RFC-0039, RFC-0040, RFC-0043, RFC-0049, RFC-0060, RFC-0064, RFC-0070,
RFC-0071, and RFC-0072<br>
**Forward extension:** RFC-0074 / D-078 (phase 0.47 first-class maps)

**Revision:** 2026-08-16 — D-079 contract refine against Published in-tree `v0.45.0`:
planning baseline rebased, bundle/workspace/chart locks recorded, real 0.43 descriptor,
0.44 `TypeSchema`, and 0.45 catalog/projection seams named. D-075 bundle/workspace/chart/
element/remote authority and gate IDs stay in scope. 0.47 authority is unchanged. Prior:
Stage 0 packet written against Published `v0.42.0` while 0.43–0.45 were planned. D-076's
0.44 and D-077's 0.45 Stage 0 contract refines did not change this RFC's workflow
authority. D-079 rebases planning facts only.

## Summary

Phase 0.46 turns the converged 0.45 interaction ecosystem into new opt-in package capabilities.
First-party packages may assemble typed views, commands, forms, components, scenarios, and
catalog projections into package-native feature bundles. Every bundle compiles to the ordinary
0.43/0.44 runtime and registers through the 0.45 catalog; no package receives a parallel workflow
engine or new execution authority.

The initial vertical slices are model-driven data workspaces, linked chart/data interactions,
schema-aware element controls, explicit MCP/Gradio workflow projections, Explorer/Jinja/extras/
notebook workbenches, and executable simulation/conformance scenarios.

## Required 0.45 predecessor contract

0.46 begins only after 0.45 Verifies:

- one sealed read-only `InteractionCatalog` and deterministic `InteractionManifest`;
- the fixed descriptor → type extension → catalog → projection authority hierarchy;
- a namespaced, bounded, redacted `PackageProjection` protocol;
- package disposition and capability/limitation records;
- host, Jinja, Explorer, CLI, OpenAPI, scenario, conformance, simulation, notebook, remote-projection,
  and deployment consumption paths; and
- unchanged 0.44 behavior when the catalog or optional projections are unused.

If a proposed 0.46 feature requires changing that authority hierarchy or introducing a package
runtime, work stops for an RFC/decision amendment.

## Goals

- Define a small immutable `FeatureBundle` integration unit that groups existing handles,
  components, scenarios, and projections but owns no execution semantics.
- Provide an explicit include/register lifecycle with deterministic ids, composition rules,
  package provenance, capability checks, and teardown/rollback behavior.
- Add an opt-in `DataWorkspace` path for model-backed list/detail/create/edit workflows with
  explicit sources, authorization hooks, mutation policy, conflict outcomes, and overrides.
- Add explicit typed chart selection, filtering, drill-down, export, and chart↔data coordination
  through existing commands/effects.
- Let `hedron-elements` select enhanced controls and async command states from the supported 0.44
  control/outcome inventory while native HTML remains canonical.
- Let `hedron-mcp` and `hedron-gradio` expose selected package workflows through separate explicit
  policies, typed inputs/outcomes, confirmations, progress, and audit.
- Turn Explorer, Jinja, extras, notebooks, and simulation into coherent workflow authoring,
  preview, diagnostics, and test-generation experiences.
- Publish package-author and language-neutral conformance fixtures for third-party bundles.
- Preserve application authority, progressive enhancement, package optionality, and rollback.

## Non-goals

- A universal CRUD generator, ORM discovery, implicit `.objects.all()`, or inferred persistence.
- Inferring authentication, authorization, tenancy, transactions, idempotency, retry safety,
  destructive-action safety, or business validation from models or field names.
- Hidden chart/data dependency discovery, automatic invalidation, signals, hooks, a global store,
  or full-script reruns.
- An opaque visual programming format or Explorer-owned production workflow representation.
- Automatic MCP/Gradio/public exposure, remote URL discovery, or ambient credentials.
- Automatic form/control generation beyond the Supported 0.44 inventory.
- Required Web Components, browser frameworks, Node builds, live transports, or type-checker
  plugins.
- Replacing package-specific expert APIs, data sources, chart specifications, element ABI, or
  adapter escape hatches.
- Promoting Experimental surfaces or package maturity without their own evidence.

## Feature bundle contract

A `FeatureBundle` is an immutable registration description containing a bounded set of:

- existing `FragmentHandle` and `ActionHandle` definitions or factories using documented
  registration APIs;
- Hedron components and package-owned presentation providers;
- example/scenario definitions with synthetic safe data;
- package projections referencing the resulting catalog fingerprints;
- capability requirements and honest adapter/browser limitations; and
- package/version/provenance metadata.

A bundle does not execute handlers, own application state, create arbitrary routes after registry
seal, override descriptors or type schemas, weaken policy, or act as a transaction boundary.
Including a bundle is deterministic and fails atomically before registry seal if ids, routes,
projections, or capability requirements conflict.

Bundles may compose other bundles only through declared, acyclic dependencies with depth/count
limits. Optional child capabilities remain explicit; missing optional packages cannot silently
change behavior.

## Model-driven data workspaces

`hedron-data` may provide an opt-in `DataWorkspace[ModelT]` that assembles ordinary handles and
components for a bounded initial inventory:

- paginated/filterable/sortable list view;
- detail view with explicit identity mapping;
- create and edit forms/commands for Supported model fields;
- validation, not-found, conflict, forbidden, and success outcomes;
- refresh/update declarations for list/detail/summary surfaces; and
- optional optimistic mutation only for the already-Supported risk inventory.

Applications must supply an already-authorized source/factory and explicit read/mutation policy.
The workspace never discovers models, queries, tenants, transactions, authorization, delete
semantics, or audit retention. Destructive deletion is absent by default and requires an explicit
application command, confirmation/fallback, and policy.

Every generated surface has field, column, layout, query, form, outcome, and command overrides.
Unsupported schemas require an explicit component/form rather than guessed UI.

## Linked charts and data

`hedron-charts` may provide typed interaction bindings for the Supported first-party `ChartSpec`
path:

- selection and filter payload models;
- drill-down commands and destination views;
- explicit refresh/update targets for linked tables, summaries, and charts;
- deterministic export commands with existing authorization; and
- declared empty/loading/error/unsupported states.

Browser chart events are untrusted inputs validated through ordinary command boundaries. Links are
explicit edges, not discovered from shared data reads. Cycles, fan-out, event frequency, payload,
selection cardinality, and refresh cost are bounded. Experimental chart adapters do not become
Supported merely because they can attach a projection.

## Schema-aware elements

`hedron-elements` may map the closed Supported 0.44 control inventory to its Supported element
inventory. Enhancements preserve the same field name/value encoding, labels, descriptions,
required/invalid state, error association, focus, CSRF, form participation, and no-JavaScript
submission.

Async command elements may display explicit idle/submitting/success/error/cancelled states derived
from existing command outcomes. They do not execute undeclared commands, retain secrets, or make
the browser authoritative. Upgrade failure leaves a useful native control/form.

## Remote and agent projections

`hedron-mcp` may expose a selected view as a resource or selected command as a tool only through an
explicit `McpExposure`-class policy. It reuses the catalog/type schema for description and input
shape but separately specifies principal resolution, authorization, confirmation, mutation class,
rate/concurrency limits, cancellation, audit, and output bounds. Effects are reported as typed
results; an MCP client does not gain DOM target authority.

`hedron-gradio` may provide an explicit remote-workflow adapter for allowlisted discovered endpoint
metadata. It maps supported inputs/results/files/progress to Hedron forms, commands, views, and
outcomes while retaining existing egress, host, credential, file, job, cancellation, and vendor
policy. It does not embed Gradio UI or treat remote schemas as trusted Hedron models.

## Workbench and authoring experiences

- Explorer gains a workflow view that previews bundle composition, package provenance,
  capabilities, outcome variants, declared/observed effects, and cross-surface costs. It may
  generate reviewable Python/test scaffolds but is not a production workflow database.
- `hedron-jinja` gains typed helpers for included package features through catalog logical ids and
  handles; templates do not construct bundles, inspect annotations, or bypass registration.
- `hedron-extras` workbenches consume catalog/type/control metadata instead of arbitrary callable
  introspection and retain explicit sandbox/Experimental boundaries.
- `hedron-notebook` offers localhost-only workflow labs with synthetic/example inputs, controlled
  command execution, result history, and scenario export.
- `hedron-sim` executes the documented offline subset and refuses unsupported dependency, remote,
  file, live, or browser-authority behavior.

## Scenarios and conformance

Every first-party bundle ships synthetic examples and `AppScenario` coverage for native and HTMX
paths, validation, every typed outcome, effects, authorization denial, no-JavaScript fallback, and
adapter limitations. Explorer/notebook actions can export reviewable scenario code; generated
tests are never silently trusted.

`hedron-conformance` publishes versioned portable fixtures for bundle metadata, composition,
catalog projections, forms, outcomes, and effects. Node/Java evaluators validate portable
artifacts only. Third-party packages use the sample kit to prove namespace, optional-dependency,
registration, rollback, and no-privileged-access rules.

## Security, accessibility, and performance

- Models and schemas improve validation and tooling but never confer authority.
- Sources are pre-authorized; mutation policy is explicit and checked at execution.
- Remote projections repeat live authorization and never trust catalog possession.
- Bundle/projection/model/field/route/edge/scenario counts, recursion, payloads, files, refresh
  fan-out, event rate, and retained history are bounded.
- Native forms and server-rendered content remain canonical; enhanced controls preserve 0.44
  semantics and existing accessibility claim boundaries.
- Package workspaces define query/request/render budgets and avoid N+1 or unbounded refresh fan-out.
- Applications not using package bundles pay no material request-path cost.

## Compatibility, migration, and rollback

0.46 is opt-in. Existing package APIs and unchanged 0.42–0.45 applications continue to work.
Applications may adopt one package feature at a time and may eject generated configuration into
ordinary explicit views/commands/components without losing behavior.

Rollback removes bundle inclusion and uses the underlying explicit package/0.45 APIs. A package
may version its feature independently within declared compatibility ranges; phase completion does
not require a blanket maturity promotion. A bundle absent at rollback cannot leave routes,
projections, assets, or registry entries behind.

## Resolved questions (D-075)

1. **Is `FeatureBundle` a workflow runtime?** No. It is an atomic registration/composition unit for
   existing handles, components, scenarios, and projections.
2. **Does `DataWorkspace` infer authorization or persistence?** No. Applications provide
   pre-authorized sources and explicit mutation policy.
3. **Are chart links reactive dependencies?** No. Every event model, command, and effect edge is
   explicit and bounded.
4. **Do enhanced elements replace native forms?** No. Native form encoding and fallback remain
   canonical.
5. **Does a catalog entry become an MCP tool?** No. `McpExposure`-class policy is a separate
   explicit registration with live authorization.
6. **Can Explorer define production workflows?** No. It inspects and generates reviewable code/tests.
7. **Must every package ship a bundle?** No. The accepted 0.46 inventory names the initial feature
   packages; compatibility-only packages retain their 0.45 disposition.
8. **What is the cut baseline?** Verified in-tree `v0.45.0`. Original Stage 0 planning used
   Published `v0.42.0`. **D-079** rebases the living/planning baseline to Published in-tree
   `v0.45.0`.

## Resolved questions (D-079)

1. **Is `FeatureBundle` a workflow executor?** No. It is an atomic pre-seal registration unit
   for existing handles, components, `AppScenario` fixtures, and projections. Request execution
   stays on ordinary handles, routes, forms, effects, and `Hedron.interactions`.
2. **Which shipped 0.45 seams do bundles consume?** Portable catalog types in
   `hedron_core.catalog` (`InteractionCatalog`, `CatalogEntry`, `PackageProjection`,
   `ProjectionProvider`); compiler/seal/`Hedron.interactions` in `hedron.interactions`;
   `seal_app_catalog` after `seal_registry`. Bundles register before that seal, the same
   window as `Hedron.include_component`. Bundle inclusion does not fork catalog authority.
3. **May 0.46 reuse `FeatureManifest` or Jinja `ProviderManifest`?** No.
   `PluginContext.register_feature` / `FeatureManifest` and Jinja `ProviderManifest.feature_id`
   remain 0.16/HDJ surfaces.
4. **Where do symbols live?** Portable `FeatureBundle`, `FeatureRequirement`, and
   `FeatureConflictError` in `hedron-core`. `Hedron.include_feature` in `hedron`.
   `DataWorkspace` / `DataWorkspacePolicy` in `hedron-data`; `ChartInteraction` in
   `hedron-charts`; `McpExposure` in `hedron-mcp`; `RemoteWorkflow` in `hedron-gradio`.
   `FeatureProvider` is a `hedron-core` Protocol like `ProjectionProvider` and is **not** on
   the `hedron` facade. Drop the former “API-046 review” placeholder.
5. **How does `DataWorkspace` compile?** It produces a `FeatureBundle`. Beginner spelling
   remains `app.include_feature(orders)`. Policy type is `DataWorkspacePolicy`. Sources are
   shipped `DataEditorSource` / `AsyncDataEditorSource` (and existing InMemory /
   DjangoQuerySet / SQLAlchemy adapters). Never `.objects.all()`. Surfaces compile to
   `FragmentHandle` / `ActionHandle` / `ActionHandle.form()` / `DataTable` / `DataQuery` /
   `write_policy`. Optimism is `collection_edit` via shipped `OptimisticMutation` only.
   Resulting handles index as ordinary `view`/`command` `CatalogEntry` rows; workspace
   metadata is a new namespaced `PackageProjection` stacked on `hedron.data` current-surface
   projection (`direct_apis=True`, `exposure=False`). Lock:
   [data-workspace-046.toml](../acceptance/data-workspace-046.toml).
6. **How does `ChartInteraction` compile?** It is an explicit binding, not a second chart
   runtime. Event payloads are untrusted Pydantic input to a registered `ActionHandle`;
   effects use shipped `Refreshes` / `Updates`. Closed typed kinds remain
   `CHART_038_EVENT_KINDS` on the first-party `hedron-chart` path. Initial Supported `event`
   values are host-emitted first-party kinds plus equivalent keyboard/tabular commands:
   `select`, `inspect`, `focus`, `reset`. Export is an `ActionHandle`, never a `ChartSpec`
   callback. `legend_filter` / `brush` / `drill_intent` stay typed but Experimental until
   host emission and a11y evidence. Adapter `ChartEvent` kinds stay Experimental.
   `compose_chartlink_039` is an implementation helper, not the public API. Lock:
   [chart-interaction-046.toml](../acceptance/chart-interaction-046.toml).
7. **Do enhanced elements replace native `Control.kind` forms?** No. Mapping stacks on
   [type-form-inventory-044.toml](../acceptance/type-form-inventory-044.toml): text-like →
   `hedron-field-text`; checkbox/select/radio → `hedron-field-choice`; file →
   `hedron-field-file`; unknown stays native or requires override. `ActionHandle.form()`
   remains native-canonical. Async state uses shipped `hedron-action-async` /
   `InteractionState`.
8. **Do remote types replace MCP/Gradio adapters?** No. `McpExposure` wraps
   `McpProjection.register_resource` / `register_tool` plus live `authorize`.
   `RemoteWorkflow` wraps `GradioClientAdapter`, `GradioRemoteConfig`, and
   `GradioEndpoint`. `consume_catalog()` still does not expose. Bundle inclusion grants zero
   remote operations.
9. **Is there a `WorkflowScenario` type?** No. Bundles ship `AppScenario` fixtures or ids.
10. **Do Flask/Django gain FastAPI DI or TypeSchema production?** No. They remain
    `projection_adapter` surfaces stacked on
    [adapter-disposition-044.toml](../acceptance/adapter-disposition-044.toml) and
    [host-portable-facts-045.toml](../acceptance/host-portable-facts-045.toml).
11. **Do bundles add a fourth fingerprint authority?** No. `descriptor_fingerprint` still
    excludes `effect`/`extensions`; type extensions stay redacted `hedron.type`; catalog
    invalidation follows 0.45 rules. Entry lock remains
    [catalog-entry-045.toml](../acceptance/catalog-entry-045.toml). Bundle lock:
    [feature-bundle-046.toml](../acceptance/feature-bundle-046.toml).
12. **Which diagnostic family?** Reserve `HED-BUNDLE-*` in docs only. Do not reuse
    `HED-WORKFLOW-*`, `HED-CATALOG-*`, or `HED-PROJECTION-*`.
13. **May Stage 1 start before the 0.45 PyPI/Git tag?** Yes for in-tree Verified 0.45
    evidence. A tracking issue is still required. Do not wait on `#328`, `#318`, or `#311`
    publish assets. Do not start Stage 1 during this contract refine.
14. **Does this refine change 0.47?** No. RFC-0074/D-078 maps authority, Published in-tree
    `v0.45.0` planning baseline, and Stage 0/1 gates stay.

## Acceptance criteria

- Package feature bundles register atomically, compose deterministically, and compile only to
  existing handle/component/catalog semantics.
- The initial `DataWorkspace` inventory passes source, authz-denial, validation, conflict,
  progressive-enhancement, override, and adapter matrices.
- Typed chart/data links pass event, cycle/fan-out, target, export, accessibility, and browser
  matrices without hidden reactivity.
- Supported element enhancements preserve native form and no-JavaScript behavior.
- MCP and Gradio workflows remain explicit, deny-by-default, bounded, audited, and authorized at
  invocation.
- Explorer, Jinja, extras, notebook, simulation, scenario, and conformance consumers agree on the
  same 0.45 catalog/projection facts.
- Existing applications and package APIs pass unchanged; clean-wheel and rollback evidence covers
  the whole affected fleet.
- Every `release-gate-0.46.toml` row is Verified with zero Deferred before `v0.46.0` is cut.

