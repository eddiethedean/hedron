# Phase 0.46 implementation requirements — package-native typed workflows

**Status:** Planned; Stage 0 requirements packet<br>
**Target:** Hedron `v0.46.0`<br>
**Planning baseline:** Published `v0.42.0`<br>
**Required predecessor/cut baseline:** Verified Hedron `v0.45.0`<br>
**Decision/RFC:** D-075 / [RFC-0073](../rfcs/RFC-0073-PACKAGE-NATIVE-WORKFLOWS.md)<br>
**Public contract:** [PACKAGE_WORKFLOWS](../api/PACKAGE_WORKFLOWS.md)<br>
**Capability inventory:**
[`package-workflow-capability-inventory-046.toml`](../acceptance/package-workflow-capability-inventory-046.toml)

This document defines implementation boundaries and traceable requirements for feature bundles,
data workspaces, linked charts/data, schema-aware elements, remote workflows, authoring workbenches,
and package scenario/conformance experiences. Runtime work requires Verified 0.45.

## Architecture

```text
package configuration + explicit app policy
                    │
                    ▼
              FeatureProvider
                    │
                    ▼
    immutable FeatureBundle description
       │          │          │
       ▼          ▼          ▼
  0.43 handles  components  scenarios
       │          │          │
       └──────────┴──────────┘
                    │
                    ▼
   normal registry + 0.44 type extensions
                    │
                    ▼
       0.45 catalog + package projection
                    │
                    ▼
       existing runtime/tooling/adapters
```

There is no package workflow executor. A feature provider compiles configuration into ordinary
registered artifacts before registry seal. Request execution uses the existing handle/route/form/
effect/outcome machinery.

## Package boundaries

| Package | 0.46 responsibility |
|---|---|
| `hedron-core` | Immutable feature requirement/descriptor/conflict values and portable bundle metadata only. |
| `hedron` | Atomic include/registration orchestration, capability checks, scenario hooks, diagnostics, rollback bookkeeping. |
| `hedron-data` | `DataWorkspace`, explicit source/policy contracts, query/list/detail/create/edit/conflict surfaces. |
| `hedron-charts` | Typed selection/filter/drill-down/export bindings on Supported first-party chart paths. |
| `hedron-elements` | Supported schema-control mappings and async command/outcome enhancement with native fallback. |
| `hedron-mcp`, `hedron-gradio` | Separate explicit exposure/remote-workflow policies and adapters. |
| `hedron-explorer`, `hedron-jinja`, `hedron-extras`, `hedron-notebook`, `hedron-sim` | Workflow inspection, registered rendering, workbenches, labs, offline subset, and reviewable test/code generation. |
| `hedron-conformance`, `hedron-sample-kit` | Portable bundle fixtures and third-party author reference. |
| `hedron-flask`, `hedron-django` | Portable bundle semantics and explicit host exceptions. |
| deployment/compatibility-only packages | Preserve 0.45 disposition; smoke included applications without acquiring workflow semantics. |

## Normative requirements

### Feature bundle and inclusion (`PW-BUNDLE-*`)

- **PW-BUNDLE-001:** `FeatureBundle` is immutable, bounded, deterministic, package-provenanced, and
  contains only documented handle/component/scenario/projection/requirement descriptions.
- **PW-BUNDLE-002:** bundle inclusion occurs before registry/catalog seal and validates the complete
  proposed change before atomically registering any route, handle, component, asset, scenario, or
  projection.
- **PW-BUNDLE-003:** inclusion rejects duplicate ids/routes/namespaces/assets, cross-app objects,
  stale fingerprints, incompatible type extensions, and attempts to override existing artifacts.
- **PW-BUNDLE-004:** declared bundle dependencies are acyclic, version/capability checked, depth/
  count bounded, and ordered deterministically independent of import/hash order.
- **PW-BUNDLE-005:** required versus optional capabilities are explicit; missing required
  capabilities fail, while optional absence is recorded and cannot silently select different
  security or execution semantics.
- **PW-BUNDLE-006:** a bundle owns no executor, application/global state, transaction, dependency
  solver, route dispatcher, response converter, effect engine, or browser runtime.
- **PW-BUNDLE-007:** provider configuration is immutable or fingerprinted; equivalent configuration
  produces equivalent artifacts and projection fingerprints.
- **PW-BUNDLE-008:** inclusion failure, disablement, uninstall, rollback, or hot-development rebuild
  leaves no partial routes, assets, components, projections, scenarios, caches, or background work.
- **PW-BUNDLE-009:** third-party providers use public plugin/catalog APIs with namespace and
  dependency isolation; privileged flagship internals are unavailable.
- **PW-BUNDLE-010:** applications can inspect/eject a bundle into ordinary explicit
  views/commands/components/configuration without an opaque serialized workflow dependency.

### Data workspaces (`PW-DATA-*`)

- **PW-DATA-001:** `DataWorkspace[ModelT]` requires explicit logical name, Pydantic/public model
  boundaries, already-authorized source/factory, and `DataWorkspacePolicy`; it discovers none.
- **PW-DATA-002:** the initial Supported inventory is bounded list, detail, create, and edit; delete,
  bulk mutation, arbitrary relations, and automatic nested writes are excluded by default.
- **PW-DATA-003:** list query models explicitly allowlist page size, cursor/page, sort fields/
  directions, filters, search, projection, and maximum cost; invalid/unknown fields fail.
- **PW-DATA-004:** detail identity uses explicit validated fields and application/source policy;
  catalog/DOM ids never substitute for database/tenant authorization.
- **PW-DATA-005:** create/edit commands use 0.44 supported forms or explicit overrides, ordinary
  CSRF/method/content/upload limits, and typed success/validation/forbidden/not-found/conflict
  outcomes.
- **PW-DATA-006:** every read/mutation repeats live application authorization and source scoping;
  model validation is not authz, tenancy, transaction, or business policy.
- **PW-DATA-007:** transaction, idempotency, retry, audit, revision/conflict, and side-effect policy
  remain application/source-owned and are never guessed from source/model methods.
- **PW-DATA-008:** optimistic mutation is opt-in only for the existing Supported risk inventory,
  requires revisions/idempotency/rollback/refetch, and denies destructive/high-risk classes.
- **PW-DATA-009:** list/detail/summary/form columns, layouts, controls, queries, commands, outcomes,
  effects, empty/loading/error states, and components have explicit override/eject paths.
- **PW-DATA-010:** unsupported recursive/nested/polymorphic/file/custom types require explicit
  forms/components/commands; no generic text/JSON control is guessed.
- **PW-DATA-011:** query count, rows, fields, payload, files, validation errors, concurrent loads,
  refresh fan-out, memory, and retained optimistic history are bounded and measured.
- **PW-DATA-012:** sync/async sources, FastAPI/Flask/Django, native/HTMX/no-JS, authorization denial,
  conflict, rollback, and existing direct DataTable/DataEditor APIs have conformance fixtures.

### Linked charts and data (`PW-VISUAL-*`)

- **PW-VISUAL-001:** `ChartInteraction` supports a closed initial inventory of typed selection,
  filter, drill-down, and deterministic export bindings on Supported first-party chart paths.
- **PW-VISUAL-002:** each browser event maps to an explicit Pydantic input model and registered
  command; event payloads are untrusted and cannot contain executable callbacks/expressions.
- **PW-VISUAL-003:** command results declare explicit refresh/update targets for linked charts,
  tables, summaries, or detail views; shared data reads do not create dependencies.
- **PW-VISUAL-004:** graph cycles, depth, fan-out, duplicate targets, event rate, debounce policy,
  selection cardinality, payload bytes, request count, and retained state are bounded.
- **PW-VISUAL-005:** chart filters/selections remain URL/form/session/application state according to
  explicit ownership; no hidden global browser store or durable draft appears.
- **PW-VISUAL-006:** drill-down destinations and export commands repeat live authorization and use
  registered routes/output/download policies; labels/ids do not grant access.
- **PW-VISUAL-007:** empty/loading/error/unsupported/stale/partial/cancelled states and full-chart/
  tabular/no-JS fallbacks are defined for every binding.
- **PW-VISUAL-008:** keyboard and assistive alternatives expose equivalent selection/filter/
  drill-down information without requiring pointer-only chart interaction.
- **PW-VISUAL-009:** optional/Experimental chart adapters retain their classifications and declare
  event/export limitations; projection availability does not promote them.
- **PW-VISUAL-010:** chart↔data goldens cover ordering/races, rapid events, stale responses,
  cancellation, target replacement, adapter absence, and rollback.

### Schema-aware elements (`PW-ELEMENT-*`)

- **PW-ELEMENT-001:** one finite mapping connects Supported 0.44 control schemas to Supported
  `hedron-elements` tags; unknown/ambiguous controls remain native or require override.
- **PW-ELEMENT-002:** enhanced controls preserve native form name/value/multiple/file/content-type,
  method, CSRF, disabled/read-only, and ordinary submission semantics.
- **PW-ELEMENT-003:** labels, descriptions, groups, required/invalid state, server errors, focus,
  announcements, retention, autocomplete, and keyboard behavior have parity fixtures.
- **PW-ELEMENT-004:** pre-upgrade, failed-upgrade, JavaScript-off, CSP-restricted, and removed-package
  paths remain useful native controls/forms.
- **PW-ELEMENT-005:** typed custom-event payloads are bounded untrusted input and route only to
  explicitly registered command bindings; arbitrary event names/selectors/callbacks are forbidden.
- **PW-ELEMENT-006:** async command elements use explicit idle/submitting/success/error/cancelled
  outcomes and ordinary form/link fallback; browser state is not server authority.
- **PW-ELEMENT-007:** elements never retain/reflect secrets, credentials, CSRF material, files, or
  sensitive rejected values beyond explicit native form policy.
- **PW-ELEMENT-008:** HTMX swap/upgrade/disconnect/reconnect/listener/resource cleanup is
  deterministic under repeated workflow updates and late responses.
- **PW-ELEMENT-009:** existing element ABI, Supported inventory, React-island disposition, no-Node
  Python path, and direct element APIs remain unchanged unless explicitly extended with evidence.

### Remote and agent workflows (`PW-REMOTE-*`)

- **PW-REMOTE-001:** `McpExposure` is separate explicit registration referencing a live catalog
  entry and cannot be inferred from bundle inclusion, annotations, names, routes, or projections.
- **PW-REMOTE-002:** MCP policy specifies resource/tool role, read/mutation class, principal/authz,
  confirmation, rate/concurrency/timeouts, cancellation, audit, output bounds, and allowed outcomes.
- **PW-REMOTE-003:** MCP input uses the local 0.44 schema but repeats live validation/dependencies/
  authz; sensitive fields/defaults/examples and DOM target authority are excluded.
- **PW-REMOTE-004:** effect/outcome results are explicitly serialized and bounded; browser refresh/
  patch descriptions do not authorize remote DOM or follow-up operations.
- **PW-REMOTE-005:** `RemoteWorkflow` requires an explicit Gradio adapter, allowlisted endpoint,
  local input model, complete outcome mapping, and egress/file/job policy.
- **PW-REMOTE-006:** remote endpoint metadata/results/errors are untrusted and cannot override local
  models, labels, validation, authz, output policy, or safe rendering.
- **PW-REMOTE-007:** file upload/download uses existing size/type/path/retention/cleanup/authorization
  contracts; remote paths/URLs are never exposed directly.
- **PW-REMOTE-008:** progress, polling/job state, cancellation, retry, timeout, partial results,
  remote drift/unavailability, and multi-worker limits have deterministic outcomes.
- **PW-REMOTE-009:** no Gradio UI embedding, arbitrary user-supplied remote URL, automatic endpoint
  discovery at request time, ambient credential capture, or Supported live-transport promotion.
- **PW-REMOTE-010:** audit/redaction/adversarial/rollback fixtures prove that removing exposure or a
  remote provider leaves local bundle/views/commands unchanged.

### Workbench and authoring experiences (`PW-WORKBENCH-*`)

- **PW-WORKBENCH-001:** Explorer workflow views consume 0.45 catalog and bundle projections, not
  package-specific callable/annotation reinspection.
- **PW-WORKBENCH-002:** Explorer shows composition/dependencies, capabilities/limitations,
  provenance, forms/controls, every outcome, effects, query/refresh cost, security/a11y evidence,
  and adapter support.
- **PW-WORKBENCH-003:** Explorer executes only allowlisted synthetic/example or explicitly supplied
  inputs through normal HTTP/auth/CSRF/validation/policy; it is disabled/secured per existing modes.
- **PW-WORKBENCH-004:** Explorer-generated application/test code is deterministic, reviewable,
  source-mapped, no-overwrite by default, and never an opaque production workflow database.
- **PW-WORKBENCH-005:** Jinja renders included feature handles through explicit environment catalog
  bindings; templates cannot construct bundles, expose tools, inspect models, or bypass policies.
- **PW-WORKBENCH-006:** extras data/callable/chart workbenches use registered schemas and supported
  controls, retain Beta/Experimental boundaries, and reject arbitrary executable callable metadata.
- **PW-WORKBENCH-007:** notebook workflow labs remain loopback/token-gated, bound resource/history
  use, explicit inputs, deterministic shutdown, and no Supported hosted/public server claim.
- **PW-WORKBENCH-008:** sim supports documented native/HTMX form/result/effect subsets and refuses
  unsupported dependency, remote, file, live, custom-element-authority, or server-only behavior.
- **PW-WORKBENCH-009:** CLI inspection/scaffold/eject commands use versioned catalog/bundle data,
  stable diagnostics, safe paths, no target-code execution in static mode, and no overwrite.
- **PW-WORKBENCH-010:** workbench/browser flows meet responsive, keyboard, error/focus,
  reduced-motion, visual-mode, cleanup, and performance budgets.

### Scenarios, conformance, and package authors (`PW-SCENARIO-*`)

- **PW-SCENARIO-001:** every first-party bundle ships synthetic examples and `AppScenario` coverage
  for native, HTMX, no-JS, validation, authz denial, outcomes, effects, errors, and rollback.
- **PW-SCENARIO-002:** scenario helpers operate on registered feature/handle ids and preserve raw
  HTTP assertions; they do not invoke handlers or mutate catalog state directly.
- **PW-SCENARIO-003:** generated scenario code is deterministic/reviewable and includes explicit
  policies/fixtures rather than captured credentials, database state, or sensitive values.
- **PW-SCENARIO-004:** conformance adds versioned portable bundle/composition/requirement/form/
  outcome/effect/projection fixtures with positive, negative, hostile, and skew cases.
- **PW-SCENARIO-005:** sample-kit demonstrates a third-party Data/Chart-neutral feature bundle,
  projection, scenario, Explorer integration, dependency optionality, disablement, and uninstall.
- **PW-SCENARIO-006:** Node/Java evaluators validate portable artifacts only and are not required to
  execute Python bundles or become app servers.
- **PW-SCENARIO-007:** fuzz/property corpora cover bundle graphs, schemas, queries, event payloads,
  outcomes, remote metadata, manifests, and bounds without external services.
- **PW-SCENARIO-008:** real-service/browser suites are separate, retry-bounded, provenance-recorded,
  and cannot be replaced by mocks for release-critical remote/deployment claims.
- **PW-SCENARIO-009:** fixtures and package data ship in clean wheels with schema compatibility,
  license/provenance, and offline execution evidence.

### Host and deployment parity (`PW-HOST-*`)

- **PW-HOST-001:** FastAPI uses documented 0.43–0.45 registration/request/dependency/OpenAPI paths;
  feature inclusion adds no parallel router or solver.
- **PW-HOST-002:** Flask and Django support the portable bundle/data/form/effect/outcome subset and
  expose explicit async/lifespan/background/cancellation limitations.
- **PW-HOST-003:** adapter/source authorization, sessions, CSRF, URL reversal, validation,
  responses, uploads/downloads, and mount prefixes remain native-host authoritative.
- **PW-HOST-004:** feature bundle/catalog fingerprints are host-portable for semantic fields and
  host-specific for declared fields; conformance does not compare false equivalents.
- **PW-HOST-005:** Posit/Workbench/Connect and ordinary ASGI/WSGI deployment smokes preserve
  included-feature routes/assets/catalog URLs under mounts, restarts, multi-worker, and rollback.
- **PW-HOST-006:** existing adapter/deployment/package APIs, clean imports, and compatibility-only
  dispositions remain unchanged without feature inclusion.

### Security and privacy (`PW-SEC-*`)

- **PW-SEC-001:** threat model covers bundle/provider/plugin trust, model/source confusion, authz
  omission, route/projection collisions, event injection, remote exposure, files, and generated code.
- **PW-SEC-002:** bundle inclusion cannot weaken descriptor/type/catalog/host/CSRF/output/security
  authority; attempts fail before registry mutation.
- **PW-SEC-003:** models/types/field names never infer authn/authz/tenancy/transactions/idempotency/
  retry/destructive safety/business validation.
- **PW-SEC-004:** sensitive values/defaults/examples/identities/source rows/files/credentials/
  remote metadata are redacted across forms, outcomes, ids, events, catalog, workbenches, scenarios,
  logs, traces, and errors.
- **PW-SEC-005:** sources and remote endpoints are explicit/allowlisted; no ambient ORM manager,
  filesystem root, URL, network discovery, plugin, callable, or credential lookup.
- **PW-SEC-006:** queries, mutations, events, forms, files, outcomes, graphs, fan-out, remote calls,
  history, generated artifacts, and concurrency have pre-execution bounds.
- **PW-SEC-007:** destructive/high-risk actions default deny, require explicit command/policy/
  confirmation/fallback/audit, and are absent from automatic data-workspace inventory.
- **PW-SEC-008:** generated HTML/attributes/URLs/OpenAPI/manifest/template/code paths use contextual
  escaping/safe paths/no-overwrite and reject executable metadata.
- **PW-SEC-009:** Explorer/notebook/sim/MCP/Gradio/adapter paths retain their existing auth/origin/
  CSRF/rate/egress/token/production-disablement policies.
- **PW-SEC-010:** structured security review has zero unresolved critical/high and records residual
  risks for sources, packages, remote services, browser enhancements, and generated code.

### Accessibility and browser (`PW-A11Y-*`)

- **PW-A11Y-001:** data list/detail/create/edit surfaces use semantic native structures/forms,
  labels, instructions, errors, focus, announcements, empty/loading/conflict states, and no-JS paths.
- **PW-A11Y-002:** chart selection/filter/drill-down has keyboard and non-visual/tabular alternatives
  carrying equivalent information and action availability.
- **PW-A11Y-003:** enhanced elements meet native parity before upgrade and under failed/no-JS/CSP
  conditions; browser-only state is not the sole source of essential information.
- **PW-A11Y-004:** workbench/Explorer/notebook/sim experiences are keyboard accessible, responsive,
  zoom/reflow/high-contrast/reduced-motion compatible, and manage focus/errors predictably.
- **PW-A11Y-005:** Chromium/Firefox/WebKit matrices cover full data/chart/element/remote-mocked
  workflows, rapid updates, cancellation, reconnection, cleanup, and ordinary fallback.
- **PW-A11Y-006:** generated/overridden controls and package components expose machine inventory
  and automated/manual evidence with owned limitations/waivers.
- **PW-A11Y-007:** scoped 0.46 evidence does not close `SR-021` or create an unqualified product-wide
  human-AT/WCAG claim.

### Quality, compatibility, and release (`PW-QUAL-*`)

- **PW-QUAL-001:** unchanged 0.42–0.45 applications and existing package APIs pass; no included
  features means no behavioral/request-path change.
- **PW-QUAL-002:** every bundle compiles to and preserves 0.43 handles, 0.44 type behavior, and 0.45
  catalog/projection authority without special runtime shortcuts.
- **PW-QUAL-003:** application adoption is incremental by package/feature and supports explicit
  overrides/ejection plus rollback with no orphan artifacts.
- **PW-QUAL-004:** package feature inventory records Supported/Experimental scope, versions,
  dependencies, host/browser limitations, security/a11y obligations, owner, evidence, and rollback.
- **PW-QUAL-005:** clean wheel/sdist/source/offline/import-smoke tests prove optional dependency
  direction and absence of eager heavy package/browser/remote tooling.
- **PW-QUAL-006:** independently versioned packages retain explicit compatibility ranges; feature
  completion does not imply blanket maturity or Supported promotion.
- **PW-QUAL-007:** registration/cold compile, warm requests, query/render/mutation, chart events,
  element upgrade, remote adapters, tools, allocations, payloads, concurrency, and memory have
  budgets versus equivalent explicit 0.45 paths.
- **PW-QUAL-008:** bundle abstraction overhead is measured separately from application source/
  remote/database work and may not hide N+1, unbounded fan-out, or retry amplification.
- **PW-QUAL-009:** mixed versions, optional package absence, provider disable/uninstall, adapter
  limits, remote drift/outage, rolling deploy, failed inclusion, and 0.45 rollback fixtures pass.
- **PW-QUAL-010:** API, package, recipes, customization/eject, security, accessibility, testing,
  remote, deployment, migration, troubleshooting, and limitation docs are complete.
- **PW-QUAL-011:** new symbols begin Beta/Experimental according to inventory; existing package and
  platform stability tiers are not reduced or silently promoted.
- **PW-QUAL-012:** every 0.46 gate is Verified with retained evidence, tracking issue closure,
  changelogs/version/package rehearsal, and zero Deferred before cut.

## Implementation stages

### Stage 0 — contracts and predecessor lock

- Accept D-075/RFC-0073 and land the complete documentation/evidence packet.
- Require Verified 0.45 and freeze bundle/catalog/projection handoff goldens.
- Create a tracking issue bound to every 0.46 gate.

### Stage 1 — feature bundle SDK

- Implement portable values and atomic flagship inclusion, plugin/sample-kit author path,
  capability checks, diagnostics, ejection, and rollback.

### Stage 2 — data, charts, and elements

- Land bounded `DataWorkspace`, chart interactions, and element mappings behind explicit opt-in.
- Complete direct-API equivalence, overrides, security/a11y/browser, and adapter fixtures.

### Stage 3 — remote and workbench experiences

- Land MCP exposure, Gradio remote workflow, Explorer/Jinja/extras/notebook/sim consumers, and
  generated reviewable scenario/code flows.

### Stage 4 — closure

- Complete conformance, real-service/deployment, perf, docs, package, upgrade/rollback, and
  zero-Deferred verification.

## Traceability

| Requirement family | Primary gate | Secondary gates |
|---|---|---|
| `PW-BUNDLE-*` | `BUNDLE-046` | `SECURITY-046`, `COMPAT-046` |
| `PW-DATA-*` | `DATAFLOW-046` | `SECURITY-046`, `A11Y-046`, `ADAPTER-046` |
| `PW-VISUAL-*` | `VISUAL-046` | `A11Y-046`, `BROWSER-046`, `PERF-046` |
| `PW-ELEMENT-*` | `ELEMENT-046` | `A11Y-046`, `BROWSER-046` |
| `PW-REMOTE-*` | `REMOTE-046` | `SECURITY-046` |
| `PW-WORKBENCH-*` | `WORKBENCH-046` | `SECURITY-046`, `DOCS-046` |
| `PW-SCENARIO-*` | `SCENARIO-046` | `COMPAT-046`, `PKG-046` |
| `PW-HOST-*` | `ADAPTER-046` | `COMPAT-046` |
| `PW-SEC-*` | `SECURITY-046` | `REGRESS-046` |
| `PW-A11Y-*` | `A11Y-046` | `BROWSER-046` |
| `PW-QUAL-*` | `COMPAT-046` / `PERF-046` / `DOCS-046` / `PKG-046` | `REGRESS-046` |

## Required artifacts

- Feature bundle/requirement/conflict/projection schemas and goldens.
- Package feature inventory with Supported/Experimental scope, owners, versions, dependencies,
  limits, evidence, and rollback.
- Reference application combining data workspace, chart link, enhanced form, Explorer/Jinja,
  explicit MCP/Gradio adapters, notebook/sim, and three hosts.
- Synthetic scenario/conformance/fuzz corpora plus bounded real browser/remote/deployment evidence.
- Threat model, accessibility evidence, performance results, clean-package matrix, upgrade from
  0.45 and rollback/ejection to explicit APIs.

## Explicit prohibitions

- Do not create a package workflow executor or hidden reactive graph.
- Do not infer persistence, ORM models, authz, tenants, transactions, mutation safety, or exposure.
- Do not make Explorer an opaque production workflow store.
- Do not treat Web Components or remote clients as server authority.
- Do not auto-generate unsupported controls, arbitrary CRUD, destructive actions, or remote tools.
- Do not promote package capabilities or maturity without inventory and evidence.

## Exit condition

Phase 0.46 is complete only when Verified 0.45 is the cut baseline; every included package feature
compiles through ordinary 0.43–0.45 contracts; data/chart/element/remote/workbench/scenario vertical
slices pass their security/accessibility/browser/adapter/performance matrices; unchanged apps and
direct package APIs remain green; and every `release-gate-0.46.toml` row is Verified with zero
Deferred.

