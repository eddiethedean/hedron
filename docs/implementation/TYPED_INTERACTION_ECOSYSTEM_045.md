# Phase 0.45 implementation requirements — typed interaction ecosystem

**Status:** Published as in-tree `v0.45.0` (tag/PyPI deferred; D-074 / D-077)<br>
**Target:** Hedron `v0.45.0`<br>
**Planning baseline:** Published in-tree `v0.44.0` (D-077; original Stage 0 baseline was Published `v0.42.0`)<br>
**Required predecessor/cut baseline:** Verified in-tree Hedron `v0.44.0`<br>
**Decision/RFC:** D-074, refined by D-077 / [RFC-0072](../rfcs/RFC-0072-TYPED-INTERACTION-ECOSYSTEM.md)<br>
**Public contract:** [INTERACTION_CATALOG](../api/INTERACTION_CATALOG.md)<br>
**Capability inventory:**
[`ecosystem-capability-inventory-045.toml`](../acceptance/ecosystem-capability-inventory-045.toml)<br>
**Entry lock:** [`catalog-entry-045.toml`](../acceptance/catalog-entry-045.toml)<br>
**Manifest lock:** [`manifest-format-045.toml`](../acceptance/manifest-format-045.toml)<br>
**Host lock:** [`host-portable-facts-045.toml`](../acceptance/host-portable-facts-045.toml)

This document defines the implementation and verification requirements for the read-only
interaction catalog, sealed manifest, package projections, host/tooling integration, and
whole-fleet disposition program. Runtime work cannot begin until 0.43 and 0.44 are implemented and
Verified. **D-077 does not authorize Stage 1.**

## Architecture

```text
0.43 authoritative base descriptor ───────┐
                                          ├──► CatalogCompiler ─► InteractionCatalog (sealed)
0.44 optional TypeSchema extension ───────┘              │
                                                          ├──► trusted runtime consumers
trusted package ProjectionProvider ─► bounded projection ┤
                                                          └──► InteractionManifest
                                                                    │
                    ┌───────────────────────────────────────────────┼───────────────┐
                    ▼                                               ▼               ▼
               Explorer/CLI                                  conformance       deployment/build
```

The compiler indexes existing artifacts; it does not reinterpret them. Runtime routes, forms,
validation, effects, outcomes, and response conversion continue using their 0.43/0.44 paths. A
consumer that needs executable behavior resolves an entry back through the live app-owned registry
and repeats normal policy checks.

D-077 binds the compiler to shipped seams rather than planned names:
`FragmentHandle[BindT, ContentT]`, `ActionHandle[InputT, ResultT]`, `BoundFragment[ContentT]`,
`Patch[ContentT]`, `BaseHandleDescriptor`, `descriptor_fingerprint`, `BindingAdapter` /
`StructuralBindingAdapter` / `BindingPlan` / `BoundValues`, explicit `Form(action=handle, ...)`,
`TypeSchema` under `hedron.type`, and `OutcomeMap(case(...), ...)`.
`descriptor_fingerprint()` does not hash `effect` or `extensions`; type-extension fingerprints
are separate.

The D-077 refine does not authorize Stage 1.

## Package boundaries

| Package | 0.45 responsibility |
|---|---|
| `hedron-core` | Immutable catalog/manifest/projection/disposition/capability models, canonical JSON, fingerprints, redaction, version compatibility, bounds. |
| `hedron` | Catalog compiler/seal lifecycle, app accessor, build artifact, CLI, OpenAPI, FastAPI bridge, scenario lookup, production validation. |
| `hedron-flask`, `hedron-django` | Portable catalog projection and host-capability limitations; native reversal/security remain host-owned. |
| `hedron-explorer` | Catalog/projection graph, drift, forms/outcomes/effects/provenance panels, safe trusted/static modes. |
| `hedron-jinja` | Registered handle/form helpers backed by explicit catalog binding; no manifest execution. |
| `hedron-data`, `hedron-charts`, `hedron-elements`, `hedron-extras` | Current-surface projection providers and handle-consumption proof only; 0.46 features excluded. |
| `hedron-mcp`, `hedron-gradio` | Explicit separately authorized exposure adapters that may consume catalog facts. |
| `hedron-conformance` | Portable fixture schema and runner capabilities. |
| `hedron-sim`, `hedron-notebook`, `hedron-sample-kit` | Offline/localhost/third-party-shaped consumers with declared limitations. |
| `hedron-posit`, `hedron-workbench` | Mount/deployment validation and diagnostics. |
| `fastapi-workbench`, `hedron-native`, Node/Java evaluators | Compatibility-only evidence; no Hedron semantic dependency or application-server promotion. |

`hedron-core` imports no flagship, framework, Explorer, Jinja, package satellite, CLI, or browser
module. Optional packages may depend on public core/flagship contracts in their current direction;
the flagship must not eagerly import them.

## Normative requirements

### Catalog compiler and lifecycle (`EC-CAT-*`)

- **EC-CAT-001:** one compiler consumes the sealed registry's public 0.43 `BaseHandleDescriptor`
  values and optional fingerprint-matching 0.44 `TypeSchema` extensions under `hedron.type`
  (`type_schema_from_descriptor()`); consumers may not independently reconstruct catalog entries.
  Field/fingerprint lock:
  [`catalog-entry-045.toml`](../acceptance/catalog-entry-045.toml).
- **EC-CAT-002:** `CatalogEntry` is immutable, deterministic, JSON-projectable, and records logical
  id, kind (`view`/`command` from `BaseHandleDescriptor.kind`), descriptor/type versions and
  fingerprints, effect-state copied from `BaseHandleDescriptor.effect`, optional TypeSchema
  references (`handler_fingerprint`, `model_fingerprint`, `boundary_sources`, `field_paths`,
  `control_dispositions`, `sensitivity_flags`, `identity_flags`, `declared_target_ids`,
  `outcome_variant_ids`), capabilities, limitations, projections, and redacted provenance.
- **EC-CAT-003:** descriptor fields remain authoritative and are referenced rather than copied into
  an independently mutable routing/security model; disagreement is a stale-catalog error.
- **EC-CAT-004:** the catalog follows the existing registration/seal lifecycle, rejects mutation
  after seal, and supports concurrent readers without request-local state.
- **EC-CAT-005:** duplicate logical ids, incompatible type extensions, ambiguous app ownership, or
  projection namespace conflicts fail atomically before catalog publication.
- **EC-CAT-006:** iteration, view/command filtering, namespace lookup, fingerprints, and diagnostic
  ordering are stable across equivalent registration order and supported Python hash seeds.
- **EC-CAT-007:** catalog lookup never imports optional packages, calls handlers/dependencies,
  validates request data, renders components, executes effects, or performs network/file I/O.
- **EC-CAT-008:** catalog entries contain no callbacks, request/model/dependency instances,
  credentials, current input values, arbitrary HTML/scripts, or raw sensitive identity material.
- **EC-CAT-009:** applications with only unmodeled 0.43 handlers receive valid entries with absent
  type-extension fields and dynamic/observed effect labels copied from the descriptor, not false
  type precision. CLASS-044 class handlers remain the same `view`/`command` kinds.
- **EC-CAT-010:** app/registry/catalog fingerprints make cross-app or stale entry reuse fail clearly;
  logical ids and fingerprints are not authorization capabilities.

### Manifest and compatibility format (`EC-MAN-*`)

- **EC-MAN-001:** `InteractionManifest` has an independent format version, canonical JSON
  serialization, deterministic whole-document fingerprint, entry/projection fingerprints, and
  explicit application/catalog provenance. Format lock:
  [`manifest-format-045.toml`](../acceptance/manifest-format-045.toml).
- **EC-MAN-002:** production, development, and conformance profiles have closed redaction rules;
  development-only source detail cannot leak into production output.
- **EC-MAN-003:** manifest ordering and numeric/string/Unicode normalization are specified and
  byte-golden across supported Python; optional native acceleration must produce identical bytes.
- **EC-MAN-004:** manifest read/write uses bounded parsing and atomic replacement; truncated,
  corrupt, duplicate-key, unknown-critical-version, or fingerprint-invalid input fails closed.
- **EC-MAN-005:** `hedron build` may import only the configured trusted app entry point through the
  documented build lifecycle and emits the manifest beside existing build artifacts.
- **EC-MAN-006:** static/no-execution inspection reads source or an existing manifest without
  importing/evaluating application code/plugins/annotations and marks runtime-only facts unknown.
- **EC-MAN-007:** production startup can require a manifest and validates it against the sealed
  catalog before serving; security-sensitive missing/mismatched entries cannot be ignored.
- **EC-MAN-008:** manifest compatibility defines supported reader/writer version ranges, unknown
  optional fields, required-field failures, downgrade behavior, and regeneration guidance.
- **EC-MAN-009:** counts, nesting, string lengths, projection bytes, total bytes, and diagnostic
  volume are bounded before allocation/normalization hotspots.
- **EC-MAN-010:** the manifest is an integrity-checked build artifact, not a credential, signature,
  authorization token, remote exposure policy, or executable application format.

### Package projection protocol (`EC-PROJ-*`)

- **EC-PROJ-001:** `ProjectionProvider` has a documented framework-neutral registration/build
  protocol and returns immutable `PackageProjection` values only.
- **EC-PROJ-002:** every projection has a unique validated namespace, schema version, provider
  package/version/fingerprint, referenced catalog/entry fingerprint, capabilities, limitations,
  and bounded JSON data.
- **EC-PROJ-003:** providers run only in explicit trusted modes before catalog seal; static tooling
  never loads or invokes them.
- **EC-PROJ-004:** a projection cannot add routes, execute handles, mutate descriptors/type schemas,
  change validation/effects/outcomes, inject assets/scripts, weaken policy, or confer exposure.
- **EC-PROJ-005:** duplicate namespaces, cycles, deep provider dependencies, nondeterministic output,
  stale fingerprints, and undeclared optional dependencies fail with provider/source diagnostics.
- **EC-PROJ-006:** unknown optional projection versions leave the base entry usable and are labeled
  unsupported; required consumer projections fail clearly rather than guessing.
- **EC-PROJ-007:** disabling/removing a provider removes only its projection and cannot change the
  underlying view/command runtime behavior.
- **EC-PROJ-008:** projection capability classes distinguish Supported, Experimental, unavailable,
  and unknown facts without upgrading package or feature maturity.
- **EC-PROJ-009:** projection caching keys include provider/config/catalog/entry versions and
  fingerprints; invalidation is deterministic and retained objects are bounded.
- **EC-PROJ-010:** third-party providers receive public redacted catalog views, never internal
  registry mutation handles, dependency values, application secrets, or privileged package hooks.

### Host adapters (`EC-HOST-*`)

- **EC-HOST-001:** FastAPI catalog entries reflect the existing 0.43/0.44 route, dependency,
  OpenAPI, validation, response, and security paths without adding a parallel request parser.
- **EC-HOST-002:** Flask and Django project the portable descriptor/type/effect/outcome subset and
  record machine-readable host capability exceptions. They remain `projection_adapter` surfaces
  stacked on
  [`adapter-disposition-044.toml`](../acceptance/adapter-disposition-044.toml); they do not become
  FastAPI DI or TypeSchema producers. Portable fact lock:
  [`host-portable-facts-045.toml`](../acceptance/host-portable-facts-045.toml).
- **EC-HOST-003:** adapter projections use each host's public reversal, request, session, CSRF,
  response, async, and mount contracts; they do not emulate FastAPI dependency injection.
- **EC-HOST-004:** equivalent portable fixtures produce the same logical ids, semantic fingerprints,
  form/effect/outcome facts, and redaction after excluding declared host-specific fields.
- **EC-HOST-005:** ASGI/WSGI cancellation, lifespan, streaming, background-task, and async limitations
  are capabilities, not silent behavioral approximations.
- **EC-HOST-006:** adapter absence/import failure does not affect core/flagship catalog imports;
  clean-wheel tests prove optionality.
- **EC-HOST-007:** mount/root-path/script-name reversal remains live-host authoritative and manifest
  previews distinguish internal paths from external request-derived URLs.
- **EC-HOST-008:** adapter conformance covers native/HTMX/no-JavaScript requests, authz denial,
  validation, every result class, projection absence, and rollback.

### Authoring and plugin integration (`EC-AUTHOR-*`)

- **EC-AUTHOR-001:** Jinja helpers accept registered handles/bound handles or catalog logical ids
  through an explicit environment binding; templates never execute raw manifest records. Helpers
  bind to shipped `FragmentHandle.bind`, `ActionHandle.form()` (opted-in `FormBody` only), and
  `Form(action=handle, ...)`.
- **EC-AUTHOR-002:** Jinja view/form helpers preserve normal reversal, target, CSRF, fallback,
  validation, escaping, and async rendering behavior without annotation evaluation.
- **EC-AUTHOR-003:** missing, stale, foreign-app, wrong-kind, or unsupported catalog references fail
  with template source context and no copied-route fallback.
- **EC-AUTHOR-004:** plugin registration may add a declared projection provider before seal through
  public `PluginContext`; it receives no privileged mutation or app-secret access.
- **EC-AUTHOR-005:** plugin/provider ids, namespaces, dependencies, ordering, disablement, and
  rollback are deterministic and included in build/package diagnostics.
- **EC-AUTHOR-006:** `hedron-sample-kit` demonstrates a third-party-shaped view/command projection,
  optional dependency, Explorer panel, conformance fixture, and clean removal.
- **EC-AUTHOR-007:** scaffold and guide examples teach handles first, catalog inspection second,
  and projections only for package authors; application authors do not hand-author manifests.
- **EC-AUTHOR-008:** no template/plugin/package path can reinterpret unknown annotations, discover
  arbitrary callables, or register interactions after seal.

### Current surface package integration (`EC-SURFACE-*`)

- **EC-SURFACE-001:** `hedron-data` projects existing table/editor/source/query/mutation capability
  metadata and can target registered handles without adding `DataWorkspace` in 0.45.
- **EC-SURFACE-002:** `hedron-charts` projects `ChartSpec`, host, interaction, export, adapter, and
  limitation metadata without adding linked chart workflows in 0.45.
- **EC-SURFACE-003:** `hedron-elements` projects Supported tag/control/event/form/fallback capability
  metadata without treating schema hints as browser authority.
- **EC-SURFACE-004:** `hedron-extras` projects Beta/Experimental workbench/specialty capabilities
  and retains plugin/feature-gated discovery.
- **EC-SURFACE-005:** each package projection references catalog/type/control fingerprints and uses
  namespaced data rather than copying route, target, schema, or security policy.
- **EC-SURFACE-006:** package absence, older compatible package versions, Experimental adapters, and
  unsupported capabilities produce honest omissions/limitations, not catalog failure.
- **EC-SURFACE-007:** current component/direct APIs remain unchanged and usable without any catalog
  consumer; no package-native workflow factory lands before 0.46.
- **EC-SURFACE-008:** cross-package fixtures prove data/chart/element/extras projections coexist
  without namespace, asset, component, route, or optional-dependency collisions.

### Remote projections (`EC-REMOTE-*`)

- **EC-REMOTE-001:** MCP registration/catalog presence creates no resource/tool; exposure requires
  a separate explicit allowlisted policy owned by `hedron-mcp`.
- **EC-REMOTE-002:** an explicit MCP adapter may reuse redacted description/input/outcome facts but
  repeats principal resolution, authorization, mutation confirmation, bounds, cancellation,
  audit, and output policy at invocation.
- **EC-REMOTE-003:** MCP clients receive no DOM target capability, dependency value, credential,
  internal route, or undeclared effect authority from catalog metadata.
- **EC-REMOTE-004:** Gradio catalog integration requires an explicit configured adapter and
  allowlisted endpoint; it preserves existing egress, host, credential, schema, file, job, and
  vendor policy.
- **EC-REMOTE-005:** remote schemas are untrusted descriptive inputs and cannot become Hedron
  `TypeSchema`, application models, or form authority without explicit local mapping.
- **EC-REMOTE-006:** static/tooling modes perform no remote discovery or network calls and redact
  configured remote origins/credentials according to profile.
- **EC-REMOTE-007:** remote projection payloads, errors, files, progress, cancellation, concurrency,
  timeouts, and retained audit/history are bounded.
- **EC-REMOTE-008:** denial, stale schema, unavailable remote, cancellation, partial result,
  projection removal, and rollback fixtures leave local interactions consistent.

### Explorer, CLI, OpenAPI, and scenarios (`EC-TOOL-*`)

- **EC-TOOL-001:** Explorer consumes catalog/manifest public APIs and does not independently inspect
  handlers or package providers for facts already normalized.
- **EC-TOOL-002:** Explorer shows application graph, descriptor/type/projection provenance,
  capabilities/limitations, declared/dynamic/observed effects, forms/outcomes, drift, and
  static/dynamic mode.
- **EC-TOOL-003:** Explorer simulation invokes only allowlisted live handles through normal HTTP,
  CSRF, dependencies, authz, validation, output, and rate-limit paths.
- **EC-TOOL-004:** `hedron inspect interactions` provides human output plus versioned JSON, source/
  manifest/trusted-app modes, stable exit classes, and redacted diagnostics.
- **EC-TOOL-005:** `hedron build` emits the manifest atomically and reports provider/entry omissions,
  unsupported versions, nondeterminism, and fingerprint drift.
- **EC-TOOL-006:** OpenAPI extensions reference catalog/type/projection fingerprints and safe
  descriptions while standard FastAPI/Pydantic OpenAPI remains authoritative.
- **EC-TOOL-007:** `AppScenario` resolves handles/logical ids through the live catalog and adds
  assertions for fingerprints, projections, capabilities, limitations, and manifest parity.
- **EC-TOOL-008:** static CLI never imports/evaluates target code; trusted dynamic mode requires an
  explicit app entry point and labels side-effect/trust boundaries.
- **EC-TOOL-009:** diagnostics have stable `HED-CATALOG-*`/`HED-PROJECTION-*` families, redact data,
  identify owner/provenance, and provide actionable regeneration/disablement guidance.
- **EC-TOOL-010:** tooling remains bounded under large catalogs/projections and paginates/truncates
  human views without truncating validated machine artifacts silently.

### Portable tooling and development packages (`EC-PORT-*`)

- **EC-PORT-001:** `hedron-conformance` adds versioned fixture capabilities for catalog,
  manifest, projection, disposition, fingerprint, redaction, form, effect, and outcome facts.
- **EC-PORT-002:** fixtures contain synthetic values only and cover positive, negative, hostile,
  version-skew, unknown-optional, stale-fingerprint, and rollback cases.
- **EC-PORT-003:** Node/Java evaluators validate portable artifact semantics and canonicalization
  where declared without becoming production Hedron servers or loading Python apps.
- **EC-PORT-004:** `hedron-sim` reads a bounded supported manifest subset for static demos and
  refuses dependency, remote, file, live-transport, or browser-authority behavior.
- **EC-PORT-005:** `hedron-notebook` provides loopback/token-gated catalog browsing and preview;
  hosted/public bind remains outside Supported behavior.
- **EC-PORT-006:** notebook/sim outputs preserve redaction, mount-safe URLs, no ambient credentials,
  resource cleanup, and clear offline/localhost limitations.
- **EC-PORT-007:** sample-kit author fixtures prove independent-package namespace, version,
  dependency, projection, clean-wheel, disable, and uninstall behavior.
- **EC-PORT-008:** portable fixtures distinguish semantic fields from host/package-specific fields
  so conformance does not demand false byte equality.
- **EC-PORT-009:** fixture/artifact schema compatibility, provenance, package data inclusion, and
  release rehearsal are verified from clean installations.

### Deployment and operations (`EC-DEPLOY-*`)

- **EC-DEPLOY-001:** `hedron-posit` validates catalog/manifest fingerprints and produces mount-aware
  internal/external interaction diagnostics in Workbench and Connect modes.
- **EC-DEPLOY-002:** ephemeral Workbench mounts and trusted Connect external bases never become
  stable manifest route identity or leak environment/session values.
- **EC-DEPLOY-003:** `hedron-workbench` retains one-way compatibility through `hedron-posit` and
  exposes no second catalog implementation.
- **EC-DEPLOY-004:** `fastapi-workbench` remains Hedron-independent; integration smoke uses the
  Hedron specialization from outside the generic package.
- **EC-DEPLOY-005:** production build/startup detects missing/stale/corrupt manifests before serving
  according to configuration and retains atomic rollback to a previous verified artifact.
- **EC-DEPLOY-006:** deployment diagnostics redact paths/origins/cookies/tokens/principals and
  distinguish local bind, internal mount, and browser-visible base.
- **EC-DEPLOY-007:** real Workbench/Connect and ordinary ASGI deployment evidence covers restart,
  multi-worker, read-only filesystem, rollback, and package-version skew.

### Security and privacy (`EC-SEC-*`)

- **EC-SEC-001:** threat model treats manifests/projections/logical ids/package metadata as
  attacker-influenced data, not capabilities or authorization proof.
- **EC-SEC-002:** sensitive values/defaults/examples/identities/dependencies/credentials/request
  data are absent from catalog, manifest, projections, logs, traces, errors, snapshots, and tools.
- **EC-SEC-003:** canonical JSON and readers reject duplicate keys, non-finite numbers, excessive
  nesting/counts/bytes, invalid Unicode policy, and fingerprint ambiguity.
- **EC-SEC-004:** provider/package/plugin code runs only in trusted lifecycle modes with explicit
  ownership; static and manifest-only consumers execute none of it.
- **EC-SEC-005:** cross-app entry/projection reuse, stale artifacts, namespace squatting, downgrade,
  path traversal, symlink races, partial writes, and TOCTOU replacement have adversarial fixtures.
- **EC-SEC-006:** remote exposure remains a separate deny-by-default policy with live authz and
  cannot be smuggled through projection data.
- **EC-SEC-007:** development source/provenance detail is separated from production profiles and
  refuses accidental production inclusion.
- **EC-SEC-008:** Explorer/CLI/notebook/deployment access retains existing auth, origin, CSRF,
  rate, token, production-disablement, and audit contracts.
- **EC-SEC-009:** manifest/projection data cannot inject HTML, attributes, URLs, scripts, styles,
  headers, OpenAPI executable behavior, template objects, or unsafe diagnostics.
- **EC-SEC-010:** security review has zero unresolved critical/high findings and documents residual
  risks, package trust, build trust, and non-goals.

### Accessibility and browser (`EC-A11Y-*`)

- **EC-A11Y-001:** catalog-derived forms/controls/previews preserve 0.44 native semantics,
  validation, labels, descriptions, errors, focus, announcements, and no-JavaScript paths.
- **EC-A11Y-002:** package capability/projection metadata may record obligations/evidence/limits but
  cannot automatically claim WCAG, AT, or application conformance.
- **EC-A11Y-003:** Explorer catalog/projection graphs and tables are keyboard navigable, semantic,
  screen-reader usable, responsive, and usable without color alone.
- **EC-A11Y-004:** browser fixtures cover native and enhanced package surfaces across Chromium,
  Firefox, and WebKit, including failed/missing projection/provider behavior.
- **EC-A11Y-005:** loading/error/stale/unsupported/drift states retain focus, announcements,
  reduced-motion behavior, and useful ordinary navigation/form fallback.
- **EC-A11Y-006:** evidence scope is honest and does not close `SR-021` or create a new product-wide
  human-AT claim.

### Quality, compatibility, and release (`EC-QUAL-*`)

- **EC-QUAL-001:** unchanged Published 0.42, Published 0.43 unmodeled-handle, and Published 0.44
  modeled applications pass; catalog unused means no behavioral reinterpretation.
- **EC-QUAL-002:** the frozen 0.43/0.44 descriptor/type/binding/form/effect/outcome handoff fixtures
  remain authoritative after catalog/projection attachment.
- **EC-QUAL-003:** every first-party package/runtime has a machine-readable disposition, owner,
  capability/limitation set, compatibility range, evidence, and rollback path.
- **EC-QUAL-004:** current direct package APIs and plugin paths remain supported; a missing optional
  provider cannot break core interaction behavior.
- **EC-QUAL-005:** clean wheel/sdist/source/offline/import-smoke matrices prove optional dependency
  direction and no eager satellite/framework/tooling imports.
- **EC-QUAL-006:** independently versioned satellites retain explicit ranges and maturity; phase
  completion does not imply blanket promotion.
- **EC-QUAL-007:** cold compile/seal, warm lookup, manifest read/write, projection, CLI/Explorer,
  startup validation, allocation, payload, concurrency, and retained-memory budgets are measured.
- **EC-QUAL-008:** applications not inspecting/emitting catalogs and packages without providers pay
  no material request-path cost or new browser asset requirement.
- **EC-QUAL-009:** mixed-version, unknown optional projection, required-version mismatch, rolling
  deployment, manifest rollback, provider disable/uninstall, and 0.44 rollback fixtures pass.
- **EC-QUAL-010:** API, package-author, application, tooling, security, deployment, migration,
  troubleshooting, format compatibility, and disposition documentation is complete.
- **EC-QUAL-011:** all new public symbols begin Beta unless an existing stable contract is merely
  reused; inventories and docs agree on stability/readiness.
- **EC-QUAL-012:** every 0.45 gate is Verified with retained evidence, tracking issue closure,
  changelog/version/package rehearsal, and zero Deferred before cut.

## Implementation stages

### Stage 0 — contracts and predecessor lock

- Accept D-074/RFC-0072 and land API, implementation, inventory, gate, acceptance, upgrade,
  roadmap, status, traceability, and package-disposition artifacts.
- **D-077:** rebase planning onto Published in-tree `v0.44.0`; lock catalog-entry/manifest/host
  inventories; consume shipped 0.43 handle/descriptor/adapter symbols and 0.44 `hedron.type`
  `TypeSchema`; keep CLASS-044 as the same view/command kinds. No runtime or version bump.
- Require Verified in-tree 0.44 before runtime work. Do not block a later Stage 1 on `#318`/`#311`
  PyPI/Git assets. The D-077 refine does not authorize Stage 1.
- Create a tracking issue bound to every 0.45 gate before implementation begins.
- Keep workspace versions and published claims at 0.44. Do not claim 0.45 runtime.

### Stage 1 — core catalog and manifest

- Implement portable values/canonicalization/bounds in core and compiler/seal/build/startup in the
  flagship.
- Establish trusted/static modes, fingerprints, redaction profiles, and adversarial corpus.

### Stage 2 — projections and host/authoring consumers

- Implement provider protocol, FastAPI/Flask/Django, Jinja, plugin/sample-kit, Explorer, CLI,
  OpenAPI, and scenario consumers.

### Stage 3 — package fleet and portable/deployment consumers

- Land surface/remote package projections, conformance, sim, notebook, Posit/Workbench, native and
  Node/Java compatibility evidence.
- Record every package disposition and bounded exception.

### Stage 4 — closure

- Complete security/a11y/browser/perf/docs/compat/package review, upgrade/rollback rehearsal, and
  zero-Deferred gate verification.

## Traceability

| Requirement family | Primary gate | Secondary gates |
|---|---|---|
| `EC-CAT-*` | `CATALOG-045` | `SECURITY-045`, `COMPAT-045` |
| `EC-MAN-*` | `MANIFEST-045` | `SECURITY-045`, `DEPLOY-045` |
| `EC-PROJ-*` | `PROJECTION-045` | `SECURITY-045`, `PKG-045` |
| `EC-HOST-*` | `HOST-045` | `COMPAT-045` |
| `EC-AUTHOR-*` | `AUTHOR-045` | `TOOLING-045`, `DOCS-045` |
| `EC-SURFACE-*` | `SURFACE-045` | `PKG-045` |
| `EC-REMOTE-*` | `REMOTE-045` | `SECURITY-045` |
| `EC-TOOL-*` | `TOOLING-045` | `SECURITY-045`, `DOCS-045` |
| `EC-PORT-*` | `PORTABLE-045` | `COMPAT-045`, `PKG-045` |
| `EC-DEPLOY-*` | `DEPLOY-045` | `SECURITY-045`, `COMPAT-045` |
| `EC-SEC-*` | `SECURITY-045` | `REGRESS-045` |
| `EC-A11Y-*` | `A11Y-045` | `BROWSER-045` |
| `EC-QUAL-*` | `COMPAT-045` / `PERF-045` / `DOCS-045` / `PKG-045` | `REGRESS-045` |

## Required artifacts

- Versioned JSON Schema/goldens for catalog, manifest, projection, disposition, and diagnostics.
- Whole-fleet disposition inventory with owner, packages, versions, capabilities, limits, evidence,
  and rollback.
- Cross-host and cross-package reference application plus portable fixtures.
- Threat model/adversarial corpus, redaction audit, browser/a11y evidence, performance results.
- Upgrade from Verified 0.44 and rollback to 0.44, including provider/package removal and stale
  manifest recovery.

## Explicit prohibitions

- Do not create a third route/type/form/effect/outcome source of truth.
- Do not make a manifest executable or authoritative over live security/runtime policy.
- Do not auto-expose MCP/Gradio or load providers during static analysis.
- Do not invert optional package dependencies or eagerly import the fleet.
- Do not implement 0.46 feature bundles, data workspaces, linked charts, or remote workflows early.
- Do not use private framework/Pydantic/plugin internals or claim capability/maturity without
  evidence.

## Exit condition

Phase 0.45 is complete only when Verified 0.44 is the cut baseline; one catalog/manifest/projection
contract is used by every declared consumer; every package/runtime has an evidence-backed
disposition; remote exposure remains explicit; host/tooling/deployment/security/a11y/performance/
compatibility matrices pass; and every `release-gate-0.45.toml` row is Verified with zero Deferred.

