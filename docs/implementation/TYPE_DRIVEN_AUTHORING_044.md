# Phase 0.44 implementation requirements — type-driven authoring

**Status:** Planned; Stage 0 contract refined against Published in-tree `v0.43.0` (D-076)<br>
**Target:** Hedron `v0.44.0`<br>
**Planning baseline:** Published in-tree `v0.43.0` (original Stage 0 baseline was Published `v0.42.0`)<br>
**Required predecessor/cut baseline:** Verified in-tree Hedron `v0.43.0`<br>
**Decision/RFC:** D-072, refined by D-073 / D-076 / [RFC-0071](../rfcs/RFC-0071-TYPE-DRIVEN-AUTHORING.md)<br>
**Public contract:** [TYPE_DRIVEN_AUTHORING](../api/TYPE_DRIVEN_AUTHORING.md)<br>
**Capability inventory:**
[`type-authoring-capability-inventory-044.toml`](../acceptance/type-authoring-capability-inventory-044.toml)<br>
**Form inventory:**
[`type-form-inventory-044.toml`](../acceptance/type-form-inventory-044.toml)<br>
**TypeSchema lock:**
[`type-schema-044.toml`](../acceptance/type-schema-044.toml)<br>
**Adapter dispositions:**
[`adapter-disposition-044.toml`](../acceptance/adapter-disposition-044.toml)

This document defines implementation boundaries and traceable requirements for Pydantic-backed
view/command boundaries, annotation markers, generic specialization, generated forms, typed effects and
outcomes, optional class handlers, and a shared tooling schema. Runtime work cannot begin until the
0.43 handle/update foundation is implemented and Verified.

## Architecture

Every type-aware consumer uses one normalization pipeline attached to the 0.43 foundation:

```text
authoritative 0.43 base handle descriptor + fingerprint
                              │
                              ├──────────────────────────────► existing route/host/output/security
                              │
trusted runtime signature + Annotated metadata + Pydantic model
                              │
                              ▼
             TypeNormalizer + compiled validators
                              │
                              ▼
 versioned redacted TypeSchema extension + provenance + base fingerprint
                 │          │          │
                 ▼          ▼          ▼
          modeled bind    forms     effects/outcomes
                 │          │          │
                 └──────────┴──────────┘
                              │
                              ▼
             existing 0.43 handle/response stack
```

Explorer, CLI, OpenAPI extensions, form builders, scenarios, and runtime validation may not each
invent their own interpretation of a handler. Pydantic owns shape validation; Hedron owns boundary
source, redaction, identity contribution, form presentation, and effect declarations. The 0.43
descriptor remains authoritative for route/interaction rules.

No parallel dependency solver, action router, renderer, form-validation engine, response converter,
target policy, or reactive dependency graph is permitted.

## Package boundaries

| Package | 0.44 responsibility |
|---|---|
| `hedron-core` | Portable markers (`Sensitive`, `InstanceKey`) with no FastAPI dependency, `TypeSchema` records under `hedron.type`, redaction/provenance, schema limits, generic portable result metadata. |
| `hedron` | `ViewParams`/`FormBody`/`Control`/`Refreshes`/`Updates`/`OutcomeMap`/`RefreshableView`/`CommandHandler`/`ActionHandle.form`, Pydantic implementation of the 0.43 `BindingAdapter`, overload specialization, FastAPI integration, scenarios. |
| `hedron-explorer` | Redacted model/form/effect/outcome inspection, preview, diagnostics, dynamic-mode labeling. |
| `hedron-conformance` | Versioned boundary/form/effect/outcome fixtures and adapter capability labels. |
| `hedron-flask` / `hedron-django` | Consume portable schemas/results where supported; expose bounded machine-readable exceptions instead of emulating FastAPI DI. |
| `hedron-jinja` | Explicit access to registered form/handle schema and generated form components; no annotation evaluation in templates. |

`hedron-core` must not import FastAPI, Starlette, Flask, Django, Explorer, Jinja, mypy, pyright, or
browser packages. Pydantic is already a core dependency and may be used through documented public
v2 APIs.

## Normative requirements

### Boundary models (`TA-MODEL-*`)

- **TA-MODEL-001:** one normalization service reads preserved signatures with
  `get_type_hints(..., include_extras=True)` for trusted runtime code and produces a versioned
  `TypeSchema` extension bound to the 0.43 base-descriptor fingerprint; no type-aware consumer
  independently re-parses the handler.
- **TA-MODEL-002:** one Pydantic v2 compiled adapter/configuration implements the 0.43 binding
  protocol and owns modeled validation for bind, path/query reconstruction, form submission,
  Explorer preview, and scenario submission; base reversal/identity/ownership remain 0.43-owned.
- **TA-MODEL-003:** `ViewParams()` identifies at most one bindable Pydantic boundary; `bind` cannot
  populate `Depends`, request/context, security, or other injected parameters.
- **TA-MODEL-004:** `FormBody()` identifies at most one ordinary form boundary and enforces
  URL-encoded/multipart content type, body, upload, CSRF, and method policy before model use.
- **TA-MODEL-005:** model aliases, defaults, strictness, extras, discriminators, validators, custom
  serializers, generic specialization, and forward references have explicit supported or rejected
  dispositions and consistent fingerprints.
- **TA-MODEL-006:** missing/extra/invalid values produce stable model/field paths without raw reprs;
  safe development detail and compact production responses are separate.
- **TA-MODEL-007:** path/query/form serialization round-trips validated values or fails
  registration/build; no alternate coercion exists outside the Pydantic adapter.
- **TA-MODEL-008:** bare Pydantic models are not assigned a Hedron source by guesswork; ambiguous
  or contradictory Hedron/FastAPI metadata fails registration.
- **TA-MODEL-009:** recursive depth, model count, fields, aliases, union variants, defaults, schema
  bytes, input bytes, and validation-error count are bounded before expensive projection.
- **TA-MODEL-010:** an unmodeled 0.43 function remains valid and receives no behavioral
  reinterpretation solely because it has ordinary type annotations.
- **TA-MODEL-011:** modeled request boundaries register through documented FastAPI/Pydantic public
  APIs; no parallel raw-`Request` parser or internal dependency-solver invocation is permitted.

### Annotation markers (`TA-MARKER-*`)

- **TA-MARKER-001:** `ViewParams`, `FormBody`, `Sensitive`, `InstanceKey`, `Control`, `Refreshes`,
  and `Updates` are immutable, documented, side-effect-free metadata values.
- **TA-MARKER-002:** each marker has a closed set of valid annotation/class-config locations;
  misplaced, duplicate, or conflicting Hedron markers fail with a stable diagnostic.
- **TA-MARKER-003:** unknown third-party `Annotated` metadata is preserved/ignored and never invoked,
  serialized, repr'd into output, or treated as a Hedron policy.
- **TA-MARKER-004:** `Sensitive` redacts values/defaults/examples before framework-owned identity,
  DOM/event metadata, errors, logs, traces, schemas, Explorer, snapshots, and scenario failures.
- **TA-MARKER-005:** `InstanceKey` accepts only non-sensitive validated fields and feeds a bounded,
  versioned, non-reversible identity fingerprint; raw values never appear in ids/events.
- **TA-MARKER-006:** `Control` is presentation metadata only and cannot weaken Pydantic validation,
  inject attributes/HTML/events/roles, or select a control outside the supported inventory.
- **TA-MARKER-007:** marker metadata cannot override 0.43 route, method, fallback, cache, host,
  target, response, privacy, tenant, or CSRF policy; fallback/cache stay explicit configuration.
- **TA-MARKER-008:** marker/schema serialization contains type/config data only—never callbacks,
  dependency values, application instances, request data, or executable code.

### Generic handles and static typing (`TA-HANDLE-*`)

- **TA-HANDLE-001:** 0.44 specializes the generic slots already frozen by 0.43—
  `FragmentHandle[Params, Content]`, `BoundFragment[Content]`,
  `ActionHandle[Input, Result]`, and `Patch[Content]`—without changing class arity/order or runtime
  semantics.
- **TA-HANDLE-002:** decorator overloads retain boundary/input/content/result types for sync and
  async functions while preserving `__wrapped__`, signatures, annotations, docs, and inspection.
- **TA-HANDLE-003:** `bind(model)` type-checks the correct model and returns the correct content
  bound handle; keyword binding is runtime-validated and documented where static precision ends.
- **TA-HANDLE-004:** modeled and unmodeled handlers interoperate; absent boundary models retain the
  coarse 0.43 mapping input slots and no `TypeSchema`, not false precision or runtime rejection.
- **TA-HANDLE-005:** mypy and pyright positive/negative fixtures cover supported Python versions,
  functions, classes, inheritance/protocols, overloads, unions, aliases, generics, and async.
- **TA-HANDLE-006:** basic correct application code requires no Hedron-specific type-checker plugin;
  any optional plugin has separate installation, versioning, failure, and parity evidence.
- **TA-HANDLE-007:** runtime generic/schema metadata is immutable and redacted and cannot retain
  request/model instances beyond their lifecycle.

### Schema-derived forms (`TA-FORM-*`)

- **TA-FORM-001:** an `ActionHandle` with one `FormBody` model can generate a native form using the
  existing 0.43 action route, unsafe method, CSRF strategy, fallback, and response behavior;
  explicit `Form(action=handle, ...)` remains the universal/manual path.
- **TA-FORM-002:** a machine-readable field-shape inventory dispositions scalar, enum, optional,
  bounded collection, date/time, UUID, file, nested model, and discriminated union shapes as
  Supported, explicit-override-only, or rejected. The locked catalog is
  [`type-form-inventory-044.toml`](../acceptance/type-form-inventory-044.toml)
  (D-076). Unknown `Control.kind` values fail generation.
- **TA-FORM-003:** unsupported/ambiguous model shapes fail generation with an explicit
  field/control/form override; no guessed text-input fallback is emitted.
- **TA-FORM-004:** Pydantic field order, aliases, constraints, titles/descriptions, required state,
  defaults, validators, and discriminators serialize and parse consistently.
- **TA-FORM-005:** `Control` and explicit control overrides affect presentation only; unsafe attrs,
  raw HTML, JavaScript, roles, event handlers, and validation bypass are rejected.
- **TA-FORM-006:** forms provide deterministic ids/names, visible labels, descriptions,
  fieldsets/legends, error summary/association, safe value retention, encoding, submit/busy state,
  and native keyboard behavior.
- **TA-FORM-007:** enhanced validation fragments and ordinary HTTP full-page/redirect/error paths
  use the same error model and never rely only on client validation.
- **TA-FORM-008:** passwords, sensitive fields, tokens, file bytes, invalid secrets, and excessive
  collections are not reflected into markup, errors, traces, or snapshots by default.
- **TA-FORM-009:** an explicit `Form`/`AutoForm`/custom component can replace any generated field or
  the complete form without changing the action input model or duplicating route URLs/methods.

### Effects and outcomes (`TA-EFFECT-*`)

- **TA-EFFECT-001:** `Refreshes` and `Updates` declare a finite set of registered same-app
  handles/bound fragments; they do not execute an effect or discover data dependencies.
- **TA-EFFECT-002:** actual `RefreshIntent`/`PatchSet` targets are normalized through 0.43 policy
  and must be a subset of declared effects when a declaration exists.
- **TA-EFFECT-003:** undeclared, foreign, unregistered, unresolved, duplicate, excessive, or
  incompatible targets fail before response emission and cannot be made legal by annotations.
- **TA-EFFECT-004:** commands without declarations retain explicit 0.43 behavior and are labeled
  dynamic (or observed only in development traces) in Explorer, CLI, OpenAPI extensions, and
  static analysis; observations never become declarations.
- **TA-EFFECT-005:** typed outcomes use finite Pydantic discriminated unions and a complete,
  non-overlapping `OutcomeMap` validated at registration.
- **TA-EFFECT-006:** every outcome variant explicitly maps renderer/response, status, refresh/patch
  effects, fallback, and cache/header semantics where applicable.
- **TA-EFFECT-007:** command output is validated before mapping; wrong types, invalid variants,
  unmapped variants, renderer failures, or effect mismatches fail safely without raw model output.
- **TA-EFFECT-008:** arbitrary `BaseModel` return values are never auto-rendered or auto-serialized
  into UI merely because they are Pydantic models.
- **TA-EFFECT-009:** effect/outcome graph metadata is versioned, redacted, bounded, and shared by
  runtime, Explorer, CLI, OpenAPI extensions, and tests.

### Optional class handlers (`TA-CLASS-*`)

- **TA-CLASS-001:** `RefreshableView[Params, Data]` provides explicit `load` and `render` lifecycle
  methods and registers into the same `FragmentHandle`, route, host, bind, and response stack as a
  function view.
- **TA-CLASS-002:** only `load` is a request/dependency-injection entrypoint; `render` receives the
  validated loaded value and remains deterministic rendering code.
- **TA-CLASS-003:** `CommandHandler[Input, Result]` provides one `execute` mutation entrypoint and
  registers into the same `ActionHandle`, POST/CSRF, form, result, response, and fallback stack as
  a function command.
- **TA-CLASS-004:** registration accepts documented class/instance/protocol forms only when
  construction, lifecycle, concurrency, and signature semantics are unambiguous.
- **TA-CLASS-005:** a shared handler instance cannot retain request/user/model/dependency state;
  request-scoped mutable state requires an explicit documented factory and teardown behavior.
- **TA-CLASS-006:** class configuration for host/loading/empty/error/cache/form/effects/outcomes and
  decorator configuration has one precedence/conflict rule; conflicting declarations fail.
- **TA-CLASS-007:** sync/async methods, exceptions, cancellation, inheritance, dataclasses,
  protocols, generics, forward references, and dependency overrides have explicit fixtures.
- **TA-CLASS-008:** function and class equivalents produce matching routes, schemas, handles,
  markup, validation, effects, errors, tracing, security, and performance within recorded bounds.
- **TA-CLASS-009:** class handlers are optional and absent from the beginner scaffold unless their
  lifecycle separation materially improves the example.

### Shared schema and tooling (`TA-SCHEMA-*`)

- **TA-SCHEMA-001:** immutable `TypeSchema` records schema version, handler/model fingerprints,
  referenced 0.43 descriptor version/fingerprint, boundary/field provenance, validation/control
  disposition, sensitivity/identity disposition, outcomes/effects, and read-only fallback/cache
  projection without runtime values or callbacks. The payload lives under
  `BaseHandleDescriptor.extensions["hedron.type"]` and must match
  [`type-schema-044.toml`](../acceptance/type-schema-044.toml) (D-076).
- **TA-SCHEMA-002:** modeled binding, forms, effects/outcomes, Explorer, CLI, OpenAPI extensions,
  and `AppScenario` consume the same schema extension/version or fail a compatibility check;
  runtime routing/identity/host/output/security continue consuming the 0.43 base descriptor.
- **TA-SCHEMA-003:** Pydantic JSON Schema remains Pydantic's output and HTTP OpenAPI remains
  FastAPI's output; Hedron extensions reference/project normalized metadata without forking them.
- **TA-SCHEMA-004:** runtime inspection imports only the explicitly configured trusted app; static
  inspection parses source without imports, annotation evaluation, plugin loading, or code
  execution and labels unresolved facts.
- **TA-SCHEMA-005:** schema caches invalidate on handler/model/config/version changes, are bounded,
  thread/task safe, and do not retain obsolete app registries or request values.
- **TA-SCHEMA-006:** schema or base-descriptor fingerprint/version mismatch has an explicit
  compatibility diagnostic and no best-effort silent interpretation across runtime, Explorer,
  fixtures, or adapters.

### Security, privacy, and accessibility (`TA-SEC-*`, `TA-A11Y-*`)

- **TA-SEC-001:** type/model validation is never represented as authentication, authorization,
  tenancy, business validation, transaction, idempotency, or retry policy.
- **TA-SEC-002:** bind/form/explorer/scenario inputs cannot supply or shadow dependencies, request
  objects, security principals, app context, CSRF state, or server-owned outcome/effect metadata.
- **TA-SEC-003:** runtime annotation evaluation is limited to trusted imported app code through
  documented Python/Pydantic APIs; static analysis never imports/evaluates target code.
- **TA-SEC-004:** sensitive defaults/examples/validation inputs and custom serializer output are
  covered by a leakage corpus across all framework-owned surfaces.
- **TA-SEC-005:** generated forms preserve safe URLs, CSRF, body/file limits, filenames/content
  types, redirects, CSP, escaping, and upload quarantine contracts.
- **TA-SEC-006:** forged/cross-app effect declarations, outcome discriminators, schemas, aliases,
  extras, recursive models, enormous unions/collections/errors, and schema cache exhaustion fail
  within recorded resource bounds.
- **TA-SEC-007:** no schema, marker, control hint, outcome map, or class config may carry arbitrary
  executable strings/callbacks into client output; application render callbacks stay server-side.
- **TA-SEC-008:** dependency/route/output authorization from 0.43 remains the final authority after
  all type-driven normalization.
- **TA-A11Y-001:** supported generated controls have native semantics, visible labels, descriptions,
  grouped legends, required/invalid state, error association, and usable keyboard behavior.
- **TA-A11Y-002:** missing/inadequate labels or incompatible control hints fail generation instead
  of deriving inaccessible UI from field names alone.
- **TA-A11Y-003:** validation errors retain safe values, provide an error summary, focus/announce
  predictably, and remain usable without JavaScript or color alone.
- **TA-A11Y-004:** optional/required, disabled/read-only, help, file, choice, collection, nested, and
  discriminated fields have explicit semantic and fallback dispositions.
- **TA-A11Y-005:** generated and overridden forms pass reduced-motion, forced-colors, 200%/400%
  zoom, keyboard, no-JS, and Chromium/Firefox/WebKit scenarios.
- **TA-A11Y-006:** evidence is scoped to 0.44 form/workflow behavior and does not close or market
  the outstanding product-wide `SR-021` human-AT work.

### Developer experience, compatibility, and performance (`TA-DX-*`, `TA-QUAL-*`)

- **TA-DX-001:** beginner docs introduce one input model plus one source marker before presenting
  field hints, effects, outcomes, or class handlers.
- **TA-DX-002:** diagnostics name handler/model/field/source and give an actionable model, marker,
  control override, or explicit-form remediation without leaking values.
- **TA-DX-003:** Explorer shows validation, controls, effects, outcomes, fallback/cache, provenance,
  dynamic/unknown facts, and the equivalent 0.43 route/target mechanics.
- **TA-DX-004:** CLI/check detects ambiguous boundaries, unsupported forms, sensitive schema data,
  dependency shadowing, effect mismatches, incomplete outcomes, unsafe shared class state, and
  schema-version drift.
- **TA-DX-005:** `AppScenario` accepts typed model inputs/outcomes, exposes field-path errors, and
  asserts declared/actual effects while retaining raw HTTP and 0.43 handle assertions.
- **TA-DX-006:** IDE/autodoc displays decorated generic types, original signatures, model schemas,
  marker help, and class lifecycle without private attributes.
- **TA-DX-007:** static tooling clearly distinguishes syntax facts from runtime facts and never
  suggests that an unresolved effect/schema is verified.
- **TA-DX-008:** docs retain four layers: function handles, type-driven boundaries/forms, optional
  class lifecycles, and existing explicit/protocol escape hatches.
- **TA-QUAL-001:** unchanged Published 0.42 and Published 0.43 fixtures pass; existing annotations are
  not reinterpreted without a Hedron opt-in marker/class.
- **TA-QUAL-002:** migration fixtures cover incremental function annotations, generated-to-manual
  form fallback, effect declaration, typed outcomes, function/class equivalence, and rollback.
- **TA-QUAL-003:** FastAPI is the complete flagship; Flask/Django/Jinja/conformance surfaces either
  pass portable schema/result fixtures or publish a machine-visible bounded exception.
  Locked dispositions:
  [`adapter-disposition-044.toml`](../acceptance/adapter-disposition-044.toml) (D-076).
- **TA-QUAL-004:** new 0.44 symbols begin Beta and no existing stability tier is reduced or
  promoted solely by this phase.
- **TA-QUAL-005:** Pydantic/FastAPI integration uses documented public APIs and the supported version
  matrix; private dependency-solver/schema internals are prohibited.
- **TA-QUAL-006:** no new required browser asset, client framework, hydration, Node build, live
  transport, global store, or reactive dependency graph is introduced.
- **TA-QUAL-007:** cached validation adds at most 10% and 1 ms absolute p95 framework overhead to
  equivalent 0.43 bind/form/result paths on the recorded runner.
- **TA-QUAL-008:** cold normalization/form/schema build, cached validation, model sizes, effect and
  outcome checking, schema payload, allocation, concurrency, and retained memory have recorded
  budgets/results.
- **TA-QUAL-009:** docs cover models, markers, forms, effects, outcomes, classes, errors, static
  analysis, security, a11y, testing, adapters, migration, rollback, and explicit escape hatches.
- **TA-QUAL-010:** clean wheel/source/import and supported Python/Pydantic/FastAPI/type-checker/
  browser/adapter matrices pass without optional tooling dependency leakage into runtime packages.
- **TA-QUAL-011:** the Verified 0.43 handoff fixture passes unchanged: generic arity, base descriptor
  authority/fingerprint, structural adapter for unmodeled handlers, explicit forms,
  dynamic/observed effects, targets, and response conversion remain intact after 0.44 attaches.

## Work slices

### Stage 0 — contract and predecessor bind

- Accept D-072/RFC-0071 and land API, implementation, inventory, release gate, acceptance, upgrade,
  roadmap, decision, status, index, and traceability documents.
- **D-076:** rebase planning onto Published in-tree `v0.43.0`; lock form/`TypeSchema`/adapter
  inventories; consume shipped 0.43 handle/descriptor/adapter symbols; remove Fallback/Cache
  marker drift. No runtime or version bump.
- Create and bind one tracking issue before implementation begins.
- Keep workspace versions and published claims at 0.43. Do not claim 0.44 runtime.
- Make Verified in-tree 0.43 an explicit Stage 1 prerequisite. Do not block Stage 1 on `#311`
  PyPI/Git assets.

### Stage 1 — normalized schema and markers

- After 0.43 verification, consume its handoff fixture and add marker data, a fingerprint-bound
  `TypeSchema` extension, provenance/redaction, a Pydantic implementation of the binding adapter,
  schema caching/limits, and negative corpus.
- Record 0.43 bind/form/result baselines before adding request-path work.

### Stage 2 — generic specialization and modeled boundaries

- Specialize the fixed 0.43 generic slots with overloads; add `ViewParams`/`FormBody`
  normalization, modeled bind/form parsing, route reconstruction through the base adapter seam,
  stable diagnostics, and mypy/pyright fixtures.

### Stage 3 — forms, effects, and outcomes

- Add supported-field inventory, control builder/overrides, validation/error/fallback behavior,
  effect declarations/checking, typed outcome mapping, and HTTP/HTMX integration.

### Stage 4 — optional class lifecycles

- Add `RefreshableView` and `CommandHandler` protocols/base classes, factories, concurrency guards,
  function/class equivalence fixtures, and lifecycle diagnostics.

### Stage 5 — tooling and adapter projection

- Project `TypeSchema` into Explorer, CLI static/dynamic modes, OpenAPI extensions, AppScenario,
  Jinja, conformance, and documented Flask/Django capability labels.

### Stage 6 — security, a11y, browser, performance, and release closure

- Complete adversarial/redaction/schema-limit work, generated-form a11y/no-JS/three-engine matrix,
  type-checker/version matrix, benchmarks/memory, docs/migration, packages, and retained evidence.
- Cut `v0.44.0` only with zero Deferred 0.44-owned rows.

## Traceability matrix

| Requirements | Gate |
|---|---|
| `TA-MODEL-*`, `TA-MARKER-001`–`003`, `TA-MARKER-008` | `MODEL-044` |
| `TA-HANDLE-*` | `TYPING-044` |
| `TA-FORM-*` | `FORM-044` |
| `TA-EFFECT-*` | `EFFECT-044` |
| `TA-CLASS-*` | `CLASS-044` |
| `TA-SCHEMA-*` | `SCHEMA-044`, `TOOLING-044` |
| `TA-MARKER-004`–`007`, `TA-SEC-*` | `SECURITY-044` |
| `TA-A11Y-*` | `A11Y-044`, `BROWSER-044` |
| `TA-DX-*` | `TOOLING-044`, `DOCS-044` |
| `TA-QUAL-001`–`006`, `TA-QUAL-009`–`011` | `COMPAT-044`, `REGRESS-044`, `PKG-044` |
| `TA-QUAL-007`–`008` | `PERF-044` |

The capability inventory maps requirement families to gates and evidence classes. A gate cannot
become Verified while a mapped requirement is missing, Deferred, or represented only by prose.

## Required artifacts at cut

- Public API/autodoc/stability inventory for every symbol and generic overload.
- Verified 0.43 handoff baseline plus fixed generic-arity, base-descriptor/fingerprint, versioned
  marker/`TypeSchema` extension, and redaction/provenance negative fixtures.
- Pydantic model/source/serialization/validation and FastAPI DI-separation matrix.
- Mypy and pyright positive/negative reports across supported Python versions.
- Generated-control shape inventory and browser/a11y/no-JS/error artifacts.
- Effect declaration, typed outcome, target authority, and adversarial fixtures.
- Function/class equivalence, concurrency, cancellation, and teardown report.
- Static-no-execution and trusted dynamic inspection evidence.
- Explorer/CLI/OpenAPI/scenario snapshots with dynamic/unknown labeling.
- FastAPI/Flask/Django/Jinja conformance/capability report.
- Performance/allocation/schema-payload/cache/memory baselines and results.
- Incremental upgrade and rollback fixtures from 0.43 plus unchanged 0.42 evidence.
- Clean wheel/source/import and release rehearsal output.

## Implementation prohibitions

- Do not begin runtime implementation before 0.43 is Verified in-tree and a tracking issue exists.
The D-076 refine does not authorize Stage 1.
- Do not change 0.43 generic arity/order, base descriptor fields/fingerprint authority, structural
  binding for unmodeled handlers, explicit-form path, dynamic/observed semantics, target policy, or
  response conversion; amend the RFC/decision instead if that becomes necessary.
- Do not infer a boundary source from a bare model or ordinary type annotation.
- Do not allow bind/form data to populate dependencies or request/security context.
- Do not infer refresh/update dependencies from model/data access.
- Do not execute effects from annotations; validate explicit returned effects.
- Do not auto-render arbitrary Pydantic model returns.
- Do not generate controls for unknown/ambiguous field shapes.
- Do not expose raw sensitive/default/example values in any framework-owned schema or diagnostic.
- Do not import/evaluate target application code during static CLI analysis.
- Do not keep mutable request state on shared class handler instances.
- Do not use private Pydantic/FastAPI dependency/schema APIs.
- Do not add a required type-checker plugin or browser/runtime framework.
- Do not update train versions or published claims during planning.

## Exit condition

Phase 0.44 is complete only when modeled function and class examples use one fingerprint-bound
schema extension across binding, forms, effects/outcomes, tooling, and tests while routing and
authority stay on the 0.43 base descriptor; generated form and security matrices pass; 0.42 and
0.43 compatibility/handoff fixtures remain green; every
`release-gate-0.44.toml` row is Verified with retained evidence; and no 0.44-owned row is Deferred.
