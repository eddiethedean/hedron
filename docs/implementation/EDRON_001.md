---
status: draft
---

# Edron 0.1 implementation specification

**Status:** Stage 0 draft; implementation is not authorized and Edron is not published<br>
**Target:** Edron `0.1.0`; compatible Hedron train and release phase unassigned<br>
**Planning baseline:** Hedron workspace `0.66.1`; not an accepted compatibility floor<br>
**Roadmap:** [Edron `0.x` release roadmap](../EDRON_ROADMAP.md)<br>
**Decision/RFC:** [RFC-0094](../rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)<br>
**Public API:** [Edron 0.1 public API](../api/EDRON.md)<br>
**State and interaction:** [Edron 0.1 state and interaction](../api/EDRON_STATE_INTERACTION.md)<br>
**Packaging:** [Edron 0.1 packaging](../api/EDRON_PACKAGING.md)<br>
**Capability inventories:** [Edron 0.1 capability inventories](EDRON_CAPABILITY_INVENTORIES.md)<br>
**Acceptance:** [Edron 0.1 acceptance packet](../acceptance/EDRON_001.md)<br>
**Golden fixtures:** [Edron golden applications](EDRON_GOLDEN_APPS.md)

This specification defines how accepted Edron contracts are implemented in this repository. Public
names and observable behavior are controlled by the RFC and API contracts; private module/class
placement may change only when dependency direction, native authority, requirement IDs, and
acceptance evidence remain intact.

## Outcome

Deliver a separately installable, typed `edron` package whose class-oriented Python vocabulary
lowers into the existing Hedron application, component, route, interaction, state, style, asset,
diagnostic, and response systems. The implementation must make the common path smaller without
creating a second runtime.

At completion:

- plain `pip install edron` runs every base golden path;
- `import edron as ed` exposes exactly the frozen root inventory;
- each registered `Page`, fragment, and action has one exact native Hedron projection;
- every request uses fresh page/controller state and one native render/response pass;
- safe inputs produce coherent typed GET/HTMX plans with ordinary HTTP fallback;
- unsafe interactions retain native method, CSRF, authorization, idempotency, conflict, and
  fallback behavior;
- first-party tables/charts/maps and the native data editor for explicit direct composition are
  installed without extra Hedron commands; no Edron `data_editor` method is implied;
- optional adapters activate from compatible direct dependencies, with extras only as shortcuts;
- native Hedron objects and advanced APIs remain directly usable; and
- static/runtime tooling explains the same native registries with Edron source provenance.

## Authorization and blocking rule

This file does not authorize runtime implementation. Decision A may authorize separately useful
Hedron enablement under its own native authority, but no `packages/edron` runtime slice begins until
the acceptance packet records Decision B as Verified. At that point every Required `Enable` row
must have one of these recorded outcomes:

1. an existing public Hedron contract and passing conformance evidence are identified in the
   compatible train; or
2. a separate Hedron RFC/contract is accepted, implemented, verified, and shipped in that train.

No private Edron endpoint, registry, state machine, dependency resolver, target protocol, style
mapping, or browser runtime may temporarily stand in for missing Hedron behavior. If an upstream
item cannot be resolved, its Edron surface remains unavailable/deferred and the public contract is
revised before code is merged.

Numeric performance/resource limits, exact dependency ranges, and release artifact locks are also
Stage 0 gates. Placeholder “reasonable” limits are not sufficient for release.

## Architecture

Edron has two compilation moments and one runtime authority:

```text
trusted application import
        │
        ▼
Edron class/decorator inspection (callbacks are not executed)
        │
        ▼
immutable facade definitions + source provenance
        │
        ▼
native Hedron page/fragment/action/dependency/feature compilation
        │
        ▼
one Hedron app + router + handle registry + interaction catalog + asset/style plan
        │
        ├──────── full page request ────────┐
        ├──────── fragment request ─────────┤
        └──────── action request ───────────┤
                                            ▼
                               fresh page instance + request frame
                                            │
                    author method emits into bounded request-local buffer
                                            │
                    controls/filter relations finalize into native plans
                                            │
                                            ▼
                              native Hedron renderer/response compiler
                                            │
                                            ▼
                              ordinary HTTP or HTMX representation
```

The class/decorator compiler registers addressable native surfaces. The request compiler lowers
imperative display/layout/input calls after the author method runs. It does not run the author
method twice, rerun the module, or render a second component tree. “Transpile” means these
inspectable definition/request lowering steps, never source-to-source generation.

## Package boundaries

| Package/layer | Implementation responsibility |
|---|---|
| `edron` | Public facade classes/descriptors/functions, class inspection, request-local output collection, native calls, source mapping, packaging capability diagnostics, CLI projection |
| `hedron` | FastAPI/ASGI application, routes, DI, screens, handles, interactions, responses, CSRF/security, jobs, styling/assets, HTMX, testing authority |
| `hedron-core` | Framework-neutral native records/protocols/renderables/diagnostics only when already owned there; no Edron concepts |
| `hedron-data` | tables/data views/editors/sources and third-party data adapters |
| `hedron-charts` | first-party charts/assets and optional plotting adapters |
| `hedron-maps` | maps/geometry/assets/providers |
| application | repositories, durable state, transactions, authorization/tenancy, job backend/workers, downloads, deployment, secrets |

Hedron packages must not import or depend on Edron. A reusable missing primitive goes upstream under
native vocabulary and tests, then Edron consumes it. Edron-specific vocabulary/provenance may be
accepted by native APIs as opaque facade metadata, but native schemas do not gain an `edron`
execution dependency.

## Repository and source layout

The planned distribution lives at `packages/edron` and follows the workspace's hatchling `src`
layout:

```text
packages/edron/
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── LICENSE
├── capabilities.toml
└── src/edron/
    ├── __init__.py
    ├── py.typed
    ├── app.py
    ├── page.py
    ├── containers.py
    ├── descriptors.py
    ├── display.py
    ├── inputs.py
    ├── forms.py
    ├── outcomes.py
    ├── dependencies.py
    ├── cache.py
    ├── jobs.py
    ├── downloads.py
    ├── styling.py
    ├── capabilities.py
    ├── diagnostics.py
    ├── cli/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── loading.py
    │   ├── static_check.py
    │   └── reports.py
    └── _internal/
        ├── definitions.py
        ├── compiler.py
        ├── execution.py
        ├── output.py
        ├── filters.py
        ├── lowering.py
        └── source.py
```

This is an implementation partition, not a submodule compatibility promise. Public imports are
frozen only where the API contract says so. `_internal` is never imported by application code,
serialized as a public schema, or consumed by Hedron packages.

Implementation adds `packages/edron` to the UV workspace and development group and includes its
source/tests in Ruff and type-checker configuration. The workspace lock contains local sources for
development; built Edron metadata contains only published bounded distribution requirements, never
workspace paths.

Tests remain in the repository's existing `tests/unit`, `tests/integration`, `tests/typing`,
`tests/security`, `tests/a11y`, `tests/browser`, `tests/performance`, `tests/upgrade`, and artifact
lanes with `edron`-named modules/fixtures. Package-local tests must not be the only evidence for
cross-package behavior.

## Internal data model

Private records are immutable/frozen wherever practical and contain descriptions, not executable
runtime authority:

| Record | Required facts | Forbidden responsibility |
|---|---|---|
| facade source key | module, qualname, member, surface kind, stable source location | route or DOM authority |
| page definition | class identity, page metadata, direct descriptors, dependencies, source | page instance or output |
| fragment definition | wrapped function, inspected signature, metadata, source | endpoint execution/state |
| action definition | wrapped function, method/fallback/effects/idempotency metadata, signature, source | mutation authorization |
| dependency definition | provider/native `Depends`, cache choice, source/name | resolved resource value |
| native projection | native handle/reference plus facade source key | copied registry/route metadata |
| source index | AST/source locations and obvious literal call facts | callback execution/type authority |
| execution frame | active app/page/method/phase, native request facts, buffers, limits | persistence across request |
| output buffer | ordered bounded native-node/control-plan entries | rendering/escaping/HTTP response |
| capability record | fixed distribution/version/import/owner/maturity/remediation facts | installer/entitlement |

Facade source keys are app-scoped when projected to native registrations. They contain no bound
secret values. Generated native paths/DOM IDs remain native implementation details; source keys do
not become alternate public route identities.

There is no process-global “current Edron app,” page registry, output list, dependency map, session
dictionary, or capability enablement set. Definition objects may be reused by separate unsealed apps
because each app owns its native projection and collision checks.

## Definition compilation pipeline

Class compilation proceeds in deterministic phases:

1. **Discover:** inspect the registered class and its direct `__dict__` without invoking render,
   descriptors, dependencies, properties, or arbitrary `getattr` hooks.
2. **Validate class:** require direct `Page` inheritance, no custom constructor, one declared
   `render`, no inherited exposed descriptors, and valid page metadata.
3. **Inspect surfaces:** collect direct `Fragment`, `Action`, and `Dependency` descriptors in source
   order; inspect signatures/annotations through the accepted native type-resolution policy.
4. **Build plan:** construct one immutable native compilation plan for the screen, routes, handles,
   bindings, dependencies, effects, fallbacks, source provenance, and limits.
5. **Validate complete plan:** resolve collisions, paths, methods, signatures, dependencies,
   target/effect references, app ownership, optional required native capabilities, and resource
   bounds before registry mutation.
6. **Commit atomically:** pass the plan to the accepted native compiler/feature inclusion seam so
   failure cannot leave partial routes, handles, assets, catalog entries, or source mappings.
7. **Record projections:** native registry/catalog stores the facade source-to-handle mapping used
   by `app.native`, Explorer, tests, explain, and diagnostics.
8. **Seal normally:** Hedron registry, interaction catalog, styles/assets, OpenAPI, and lifespan
   sealing remain authoritative.

Registration never creates a page instance or invokes `render`, fragments, actions, dependencies,
cache functions, jobs, data providers, optional services, or network/file callbacks. Static source
analysis uses `ast` without evaluating annotations/imports. Trusted registration may inspect
already imported annotation objects only through the native supported policy; it does not `eval`
application strings independently.

### Imperative controls versus static registration

Display/layout/input calls occur inside author methods, so their concrete request plan cannot be
known by running registration without violating the no-callback rule. The implementation therefore
separates:

- registered addressable definitions: pages, fragments, actions, dependencies, features, handles;
- request-local output definitions: component instances, containers, controls, filter groups; and
- static source hints: conservative AST findings shown as source facts, never runtime authority.

At request finalization Edron validates the complete emitted control/filter graph before any body is
rendered. Obvious duplicate literal names or invalid call shapes may also be reported by static
`edron check`. Dynamic names remain runtime validation. `explain` labels static/dynamic/observed
facts honestly instead of pretending imperative output was registered.

## Public descriptor implementation

### Page registration

`App.page(...)` returns a class decorator and returns the identical class object. The app stores an
ordered app-local registration record; it does not mutate the class into a component or install a
process-global owner. Registering after the native seal fails with the documented diagnostic.

`App.from_hedron(...)` stores and delegates to the exact supplied unsealed `Hedron`. `App(...)`
constructs exactly one native instance. Both paths share the same compiler and projection mapping.
The simple constructor forwards the accepted `session_secret`, `production`, `build_dir`, security,
theme, root-path, and debug inputs exactly once without copying secrets into source maps or reports.
Other construction-time native options require an explicitly constructed `Hedron` passed to
`App.from_hedron(...)`; they cannot be retrofitted after middleware/lifespan setup. The Edron
`App.__call__` delegates directly to that native ASGI object.

### `Fragment` and `Action`

The decorators create public descriptor objects that retain the wrapped callable, name/signature,
source, annotations/docstring, and decorator metadata. They use normal descriptor binding and
`functools` introspection conventions; they do not replace the author function with an opaque URL.

Descriptor requirements:

- `__set_name__` records only owner/member identity and performs no app registration;
- class access returns the descriptor;
- active instance access returns a page-bound view while preserving descriptor introspection;
- `.bind(...)` creates an immutable structural bound value with canonical named parameters;
- dependency/request/security parameters are excluded from client binding;
- render-phase action invocation fails before application code;
- fragment invocation during an allowed output phase mounts/materializes the native fragment path;
- a call outside a valid frame fails with `PhaseError`; and
- registration in multiple apps resolves through the active/app-specific native projection.

Generated routes are supplied by the native compiler. Descriptors do not dispatch HTTP requests,
maintain a private endpoint map, synthesize fake requests, or invoke FastAPI DI themselves.

### `Dependency`

The public dependency descriptor retains a callable or native `Depends` declaration. On class
access it returns itself. On an active page instance it asks the native execution frame for the
resolved request value associated with that exact descriptor/page/app; it never calls the provider.

The accepted upstream compiler resolves dependencies before author code, places them in a bounded
request map, and owns async generator cleanup/overrides/caching. A descriptor lookup from the wrong
page, app, request, or closed phase fails. Dependency names are excluded from query/form/action
binding before handler invocation.

## Request execution model

Edron uses one private `ContextVar` execution-frame stack integrated with native request/render
contexts. The frame is installed/reset by a context manager in `try/finally`; tokens are never
manually retained by application objects.

Each frame contains at least:

- exact app/native registration identity;
- fresh page instance identity;
- current registered page/fragment/action source surface;
- phase (`page`, `fragment`, or `action`) as a private guard, not a public lifecycle enum;
- native request/security/render facts by reference;
- resolved dependency values by descriptor identity;
- root/current output buffers when output is allowed;
- mounted-fragment/control/filter identities; and
- native/Edron request budgets and bounded diagnostics/traces.

Edron does not spawn detached tasks for author callbacks. Awaited sync/async execution uses the
native async/thread bridge that preserves context and cancellation. Output after the frame closes,
from an un-awaited task, or from another page instance is rejected. Cancellation/exception cleanup
resets the buffer, container stack, dependency view, and ContextVar even when native response
conversion fails.

### Full page request

1. Native route/dependencies/security validate.
2. The native compiler constructs one fresh no-argument page instance.
3. Edron opens a page frame and root buffer.
4. `render()` executes once.
5. Fragment calls mount and materialize initial registered fragments once on that same instance.
6. Output/control/filter buffers finalize and validate completely.
7. Edron hands the ordered native body/plan to Hedron once.
8. Hedron renders the full page, plans assets/security/cache, and emits the response.
9. Cleanup closes the frame and page instance becomes unreachable.

### Fragment request

1. Native fragment route, binding, target, dependencies, and security validate.
2. A new page instance/frame/buffer are created for the addressed descriptor.
3. Only the fragment method executes once with validated application parameters.
4. The buffer finalizes to the registered native fragment host/response contract.
5. Native generation/history/cache/asset/HTMX behavior emits the response.
6. Cleanup closes all request-local objects.

`render()` does not run, and a prior page instance/buffer cannot be recovered.

### Action request

1. Native method/body/CSRF/auth/dependencies/binding/model/idempotency/revision checks run.
2. A new page instance and action frame are created without an output buffer.
3. Only the addressed action method executes once for an accepted operation.
4. Its returned native outcome/effects are validated against registered policy/targets.
5. Native response conversion selects HTMX or ordinary fallback/PRG behavior.
6. Cleanup and trace finalization run.

Output/container/input calls in an action frame fail. Returning success does not commit an
application transaction; the application/service owns that boundary.

## Output buffer and lowering

`Page` and `Container` share a private output-surface implementation; there is no public `ui`
singleton. A `Container` holds an opaque reference to its owning frame and native container builder,
not a completed component or persistent list.

Buffer requirements:

- append order is deterministic and matches author call order;
- context-manager entry/exit uses a token stack and restores correctly after exceptions;
- explicit container method calls and context-scoped calls target the same native builder;
- every append validates frame/page/container identity and current phase;
- node, depth, container, control, target, byte, and source-fact limits apply before emission;
- author exceptions discard incomplete buffered output;
- native `NodeLike` objects retain identity/trust/assets and are not serialized/reparsed; and
- finalization performs one Edron lowering pass followed by one native render pass.

Each explicit output method calls a documented native constructor/adapter. Edron does not implement
a general magic display registry. Native coercion protocols may be used by `table`, `dataframe`,
charts, and maps only within their documented type/size contracts. Unknown objects fail with
`EDR-LOWER-0001` rather than falling through arbitrary `repr`, HTML, JSON, or plugin discovery.

First-party display adapters preserve native package provenance and assets. Native data editing is
available through direct `hedron-data` composition; no private Edron editor is implemented under
`dataframe`.

## Safe controls and filter-plan implementation

Each safe input call performs two operations against the active page/fragment request:

1. construct a typed native control/binding specification and obtain the validated current query
   value through native codecs; and
2. append a request-local control entry containing its stable name, presentation, update targets,
   source surface, and native facts.

When the output method needs its return value, that individual value is already validated. At
buffer finalization, the accepted native coherent-filter builder receives every control and target
relation, builds connected groups, validates complete target signatures/defaults, rejects overlaps
or duplicates, and emits non-nested GET forms plus HTMX/history policy.

Edron does not parse option values with `format_func`, infer identity from labels, store filter state
in sessions, author raw endpoints/targets, or build a competing filter graph. Fragment routes remain
the authoritative typed binding boundary for fragment requests; full-page controls validate through
the same native codecs.

## Actions, forms, and outcomes implementation

Action/form controls consume registered Edron descriptors/bound values or native `ActionHandle`
objects. Normalization resolves them through the active app's native registry and produces native
controls/forms; URLs/methods/CSRF/targets are never copied into Edron-owned string templates.

Implementation requirements:

- `button` returns `None` and never reports browser click state to render;
- `.bind(...)` validates named application parameters structurally but never authorizes them;
- `form(Model, ...)` requires one compatible action model and native Pydantic form compiler;
- `controls=` uses only compatible registered native control overrides;
- nested/mixed safe/unsafe forms fail before output emission;
- `confirm=` delegates to the accepted native confirmation flow;
- `idempotency="required"` requests native key/control/store policy; Edron generates no private
  replay database;
- `updates=`/`refresh(...)` resolve exact native fragment references and bounded effect plans;
- `success(...)`/`refresh(...)` return the documented native objects; and
- native results/responses retain status, headers, cookies, redirects, error, and fallback policy.

Edron catches only facade validation/phase errors it owns. Native `HED-*` failures retain their
native diagnostic and causal chain with optional safe Edron source context.

## Cache, session, jobs, and download implementation

### Cache

`cache_data` is a signature-preserving decorator over the accepted native bounded cache. The
wrapper creates no module-global unbounded dictionary. Scope keys come from authoritative native
request/subject/tenant facts, never client values. `invalidate` and `invalidate_all` delegate to
the same cache owner and remain separate from transaction/commit behavior.

### Session

Edron implements no session store or dictionary. A native `SessionState` dependency may be placed
on a page through `ed.dependency(...)`; all signing/storage/expiry/migration/write behavior stays in
the native host/application.

### Jobs

`JobFlow` compiles into one accepted native `TaskFlow`/`FeatureBundle`. Its private Edron object may
hold author configuration before inclusion but owns no queue, worker, operation state, polling
loop, scope, result store, or production backend. Inclusion validates backend dependency, scope,
input/payload/result adapters, authorization dependencies, and limits before atomic native feature
registration.

`Page.job(...)` mounts the registered native flow. Native status/cancel/result handles share the
same `JobScope`, and polling/fallback/terminal behavior is native. The result callback executes in a
fresh output frame only when the native job result boundary has authorized and validated it.

### Downloads

`Download` is a frozen opaque identifier value, not a path. `download_button` either passes bounded
bytes plus explicit metadata to the native download control or resolves the identifier through a
registered authorized provider. Edron never opens an identifier as a filesystem path, stores large
bytes in session/output metadata, or turns job IDs into download authorization.

## Styling implementation

`theme(...)` validates the small Edron inputs and calls the native brand/design-system compiler. It
returns the exact native `DesignSystem`; it does not cache/register a separate Edron theme.

Variants resolve through native recipe-family metadata frozen by the upstream enablement. Edron may
cache the native resolution per sealed registry/version, but it cannot maintain a divergent mapping
that tooling/runtime interpret independently. `variant` and `recipe` conflicts fail during request
plan finalization or earlier static analysis.

`style_scope(...)` creates native scope/context nodes. `App.styles(...)` delegates directly to the
native application API and returns its exact `ApplicationStyleMeta`. CSS reading, roots, cascade,
CSP, assets, hooks, reports, and registration seal are native behavior.

Edron source provenance is attached as an opaque/native-supported source reference so style
explain/diff can point back to the facade call. Edron does not fork native report schemas. Shared
theme behavior for data/chart/map packages ships only after upstream cross-package evidence passes.

## Optional capability implementation

`packages/edron/capabilities.toml` is the machine-readable capability source used at build/release
and loaded lazily for capability calls/doctor. `pyproject.toml`, docs, owning adapter ranges, and
built metadata are checked against it; the runtime does not infer capabilities from requested
extras.

Resolution uses the packaging contract's fixed sequence:

1. canonical `importlib.metadata` distribution lookup;
2. accepted version/marker validation with `packaging`;
3. hard-coded owning adapter and third-party import probe;
4. native adapter/catalog resolution; and
5. available/missing/incompatible/broken result with safe remediation.

The manifest is not read by root import. It is bounded, immutable for the process, contains no
arbitrary executable entry points, and is never selected by request data. Compatible direct and
extra-installed environments use the same adapter path. Environment changes require restart; Edron
never invokes `pip`, `uv`, a shell, or a package index.

Optional Edron entry points are always defined. Method-backed capabilities call one resolver, then
delegate to the owning native adapter; registry-only capabilities such as the curated SQLAlchemy
source remain available through documented native composition and doctor. Explicit backend methods
never catch a capability error and silently choose another backend.

## Native interoperability implementation

The native projection is the implementation, not an export copy:

- `app.hedron` is the exact native application;
- `App.__call__` delegates to it;
- `include` passes exact native renderables into the output plan;
- native action/fragment handles normalize through their existing registries;
- native outcomes/responses pass through supported native conversion;
- identity re-exports use direct assignments/imports and pass `is` tests;
- `App.include` uses native feature inclusion;
- `App.styles` uses native style registration; and
- `app.native` asks the native source-projection registry for the exact handle.

Edron never reconstructs a native object from serialized metadata. Cross-app/stale/sealed/collision
errors fail under native ownership checks. Differential tests compare Edron fixtures with explicit
native lowerings for descriptors, routes, methods, dependencies, targets, effects, assets, styles,
HTTP behavior, and traces.

## CLI and source tooling implementation

The `edron` console script uses a small argument dispatcher with no plugin-command auto-discovery in
0.1. Application references are normalized as file-with-`app` or `module:attribute`; unsafe path,
attribute, and import errors receive structured diagnostics.

### Static `check`

Plain `edron check` parses trusted source text with the standard AST and an explicit Edron rule
visitor. It may verify literal decorator/method shapes, direct subclass declarations, obvious
duplicate names, forbidden vocabulary, and source-level contract rules. It does not import the app,
evaluate annotations/defaults, run callbacks, resolve dependencies, load optional adapters, or
claim dynamic registration success.

`--register` is a clearly separate trusted import path. It imports the application, compiles/seals
the native registries, and combines native diagnostics with the static source index. Neither mode
rewrites source.

### `explain` and `doctor`

`explain` imports/seals a trusted app and projects native screen/handle/interaction/style/asset/
dependency registries with Edron source mapping. Dynamic request-emitted controls/output are labeled
static hints or observed traces; explanation does not execute render/action/dependency callbacks to
manufacture them.

`doctor` reads installed distribution metadata and performs only the declared bounded import probes
needed to distinguish broken capabilities. When an `APP` is supplied, the trusted import boundary
is disclosed. Doctor never resolves/installs/upgrades packages.

### Style commands and reports

Style check/preview/explain/diff delegate to native validators/renderers/reports. Preview uses fixed
synthetic content and no app callbacks/data. Text, JSON, and SARIF outputs use versioned shared
diagnostic/report records; renderer-specific formatting is presentation only.

## Diagnostics and source mapping

`EdronError` subclasses contain a read-only `EdronDiagnostic` compatible with the shared native
diagnostic projection. Private validation helpers create stable documented codes and attach:

- concise title/explanation/remediation;
- Edron source surface and location where statically/runtime known;
- exact native descriptor/diagnostic identity after registration;
- bounded related facts and truncation; and
- safe causal chain.

Static source locations come from AST tokens. Decorator/descriptor locations are captured from the
imported callable/class without executing it. Request-emitted calls receive the owning method plus a
bounded ordinal; exact per-call source is included only when obtained without unbounded stack
inspection and is not required for correctness.

Production HTTP errors redact installation commands, private paths, dependency/session/form values,
secrets, bound identifiers, job/download IDs, and unrestricted exception text. CLI/development
audiences may receive exact safe remediation. Edron does not relabel native errors merely to make
all codes begin with `EDR`.

## Core implementation requirements

The detailed behavior above is locked by these traceable requirement families.

### Package and authority (`EDR-IMPL-PKG-*`)

- **EDR-IMPL-PKG-001:** `edron` is a separately built typed distribution in `packages/edron` with
  the exact root/CLI/package-data contract and no copied Hedron source or asset tree.
- **EDR-IMPL-PKG-002:** workspace/build/lint/type/test configuration includes Edron without adding
  an Edron dependency to any Hedron distribution or a workspace/path dependency to artifacts.
- **EDR-IMPL-PKG-003:** base/optional requirements, Python/platform support, wheel/sdist contents,
  assets, license/provenance, and clean-install behavior satisfy every `EDR-PKG-*` gate.
- **EDR-IMPL-PKG-004:** no import, registration, request, CLI, or optional path installs/mutates the
  environment, contacts an index, or treats extras as runtime flags.
- **EDR-IMPL-PKG-005:** private modules/records are not public schemas or dependencies of native
  packages; root exports and public diagnostic records alone receive compatibility protection.
- **EDR-IMPL-PKG-006:** base package corruption/incompatible trains fail clearly; no degraded Edron
  replacement hides a missing required native implementation.

### Definition compilation and descriptors (`EDR-IMPL-COMP-*`)

- **EDR-IMPL-COMP-001:** discovery inspects only direct declared class metadata/descriptors in
  deterministic source order and invokes no callback, provider, service, or dynamic attribute.
- **EDR-IMPL-COMP-002:** class/signature/path/dependency/binding/effect/source/limit validation
  completes before one atomic native registration commit; failure leaves no partial artifacts.
- **EDR-IMPL-COMP-003:** page/fragment/action definitions produce exactly one native screen/handle
  projection per app with stable facade provenance and app-local collision/ownership checks.
- **EDR-IMPL-COMP-004:** page registration returns the identical class, supports only the frozen
  direct-subclass/no-custom-constructor rules, and installs no process-global app/class owner.
- **EDR-IMPL-COMP-005:** `Fragment`, `Action`, `Dependency`, and bound descriptors preserve wrapped
  signature/annotations/docs/source and normal class/instance descriptor introspection.
- **EDR-IMPL-COMP-006:** descriptors contain definitions/bindings only; they own no endpoint
  dispatcher, DI solver, request synthesizer, mutation authority, registry, or persistent state.
- **EDR-IMPL-COMP-007:** static AST facts, trusted registration facts, request-dynamic plans, and
  observed trace facts remain explicitly distinct in diagnostics/explanation.
- **EDR-IMPL-COMP-008:** every `Enable` dependency resolves to an accepted/shipped native seam before
  its compiler branch or public surface is implemented.

### Execution and output (`EDR-IMPL-EXEC-*`)

- **EDR-IMPL-EXEC-001:** full page, fragment, and action requests construct distinct fresh page
  instances/frames and execute only the author methods defined by their lifecycle contract.
- **EDR-IMPL-EXEC-002:** the private ContextVar frame is app/page/request/phase bound, propagates
  across accepted await/thread seams, resets in `finally`, and rejects closed/foreign/detached use.
- **EDR-IMPL-EXEC-003:** page/container output is ordered, bounded, request-local, exception-safe,
  and discarded before response emission on author/lowering failure.
- **EDR-IMPL-EXEC-004:** containers restore the exact prior target after normal/exceptional exit and
  cannot be cached, shared, concurrently entered, or reused across frames.
- **EDR-IMPL-EXEC-005:** each explicit display method produces one documented native node/adapter
  result and returns `None`; unknown values never fall through magic repr/HTML/JSON/plugin dispatch.
- **EDR-IMPL-EXEC-006:** native renderables retain exact identity/trust/assets and one native
  renderer/response pass follows one bounded Edron lowering pass.
- **EDR-IMPL-EXEC-007:** first-party data/chart/map lowering uses owning package coercion, limits,
  provenance, maturity, theme, asset, and accessibility contracts.
- **EDR-IMPL-EXEC-008:** output/input/container calls in invalid phases fail with stable Edron codes
  before application mutation or partial output.

### Filters and unsafe interactions (`EDR-IMPL-INT-*`)

- **EDR-IMPL-INT-001:** safe controls use explicit names and native typed codecs to return the
  current query/default value; labels/formatters never parse, identify, or authorize input.
- **EDR-IMPL-INT-002:** request finalization sends the complete emitted control-target graph to the
  native coherent GET plan and rejects duplicate/ambiguous/nested/conflicting groups before output.
- **EDR-IMPL-INT-003:** canonical URL/history/latest-generation/target/fallback behavior is native
  and identical in authoritative meaning under HTMX and ordinary HTTP.
- **EDR-IMPL-INT-004:** fragment/action/bound values resolve exact active-app native handles and
  cannot invoke routes/DI or authorize client-bound values themselves.
- **EDR-IMPL-INT-005:** actions/forms retain unsafe method, CSRF, body/model validation, authz,
  idempotency/revision, effects, status, redirect, and PRG/fallback policy.
- **EDR-IMPL-INT-006:** button/form/confirmation controls are native, return `None`, and never turn
  browser presentation/click/confirmation into server authority.
- **EDR-IMPL-INT-007:** refresh/update targets are exact registered/bound native references with
  bounded deterministic fan-out and no selector/endpoint string authority.
- **EDR-IMPL-INT-008:** `Outcome`, success, refresh, patch, and supported response returns preserve
  exact native object/status/effect meaning; arbitrary values/Boolean results are not guessed.
- **EDR-IMPL-INT-009:** stale/cancelled/conflict/timeout/disconnect behavior prevents invalid swaps
  without pretending to roll back application mutations.
- **EDR-IMPL-INT-010:** interaction tests prove enhanced/no-JS parity, fresh lifecycles,
  concurrency/idempotency/revision behavior, and native differential equivalence.

### Dependencies, cache, jobs, and downloads (`EDR-IMPL-STATE-*`)

- **EDR-IMPL-STATE-001:** `Dependency.__get__` only retrieves a value already resolved by native DI
  for the active descriptor/page/frame; native caching/override/async cleanup remains authoritative.
- **EDR-IMPL-STATE-002:** `cache_data` delegates to one bounded native cache with explicit scope/key/
  invalidation and creates no resource, transaction, persistence, or unbounded module dictionary.
- **EDR-IMPL-STATE-003:** Edron implements no session/durable/browser state store; typed sessions,
  domain state, preferences, and ownership follow the state contract/native/application providers.
- **EDR-IMPL-STATE-004:** `JobFlow` compiles to one native feature and owns no backend/worker/queue/
  operation store/polling state/scope; native job lifecycle and application authorization remain.
- **EDR-IMPL-STATE-005:** job result output receives a fresh authorized frame and no backend result,
  ID, scope, or download capability leaks through page/session/browser metadata.
- **EDR-IMPL-STATE-006:** downloads are bounded bytes or opaque provider IDs; Edron opens no path,
  infers no authorization, and delegates headers/ranges/disposition/response policy natively.

### Styling (`EDR-IMPL-STYLE-*`)

- **EDR-IMPL-STYLE-001:** `theme` returns the exact native design system and creates no Edron theme,
  token, compiler, preference, or registry authority.
- **EDR-IMPL-STYLE-002:** variants resolve from accepted native recipe-family metadata; explicit
  recipes/props/scopes and native precedence remain authoritative and inspectable.
- **EDR-IMPL-STYLE-003:** `style_scope` and `App.styles` create/return exact native style values and
  retain native roots, cascade, hooks, CSP, assets, seal, diagnostics, and source provenance.
- **EDR-IMPL-STYLE-004:** core/data/chart/map shared theming ships only after the cross-package native
  evidence passes; optional adapters retain honest limitations/maturity.
- **EDR-IMPL-STYLE-005:** style tooling projects native reports and fixed synthetic previews without
  executing application callbacks or maintaining a duplicate report schema.

### Capabilities and native interoperability (`EDR-IMPL-CAP-*`)

- **EDR-IMPL-CAP-001:** one bounded manifest supplies canonical distribution/range/import/owner/
  maturity/remediation facts and is checked against build metadata, docs, doctor, and native owners.
- **EDR-IMPL-CAP-002:** optional resolution distinguishes missing/incompatible/broken/available in
  the frozen metadata→version→import→native order and preserves safe broken causes.
- **EDR-IMPL-CAP-003:** compatible direct and shortcut installs execute the identical native adapter;
  explicit backend failure never silently selects another backend.
- **EDR-IMPL-CAP-004:** capability metadata/imports are lazy, process-bounded, fixed by manifest,
  unaffected by request input, and require restart after environment mutation.
- **EDR-IMPL-CAP-005:** `app.hedron`, native includes/handles/outcomes/features/styles, identity
  re-exports, and `app.native` retain exact object/registry/route/effect/asset identity.
- **EDR-IMPL-CAP-006:** installing/removing Edron does not alter or disable direct public native
  package use; native-only capabilities do not become undocumented Edron exports.

### CLI and diagnostics (`EDR-IMPL-CLI-*`)

- **EDR-IMPL-CLI-001:** root CLI dispatch is bounded/deterministic and performs no plugin-command or
  arbitrary app discovery; file/module references follow the frozen loader contract.
- **EDR-IMPL-CLI-002:** static check uses AST/source only, executes/imports nothing, reports only
  conservative facts, and never rewrites source.
- **EDR-IMPL-CLI-003:** trusted register/explain/app-doctor paths disclose import execution and
  invoke no render/fragment/action/dependency/job/data/network callback for explanation.
- **EDR-IMPL-CLI-004:** doctor performs only manifest-declared metadata/import probes and never
  resolves, installs, upgrades, downloads, or mutates an environment.
- **EDR-IMPL-CLI-005:** style commands delegate to native validation/render/report authorities and
  preview only fixed synthetic content.
- **EDR-IMPL-CLI-006:** text/JSON/SARIF exit status/schema/version/redaction behavior matches the
  public CLI and shared diagnostic contracts.
- **EDR-IMPL-DIAG-001:** every Edron error uses one stable semantic code/factory and safe source/
  native cause/remediation projection; consumers never branch on rendered prose.
- **EDR-IMPL-DIAG-002:** native `HED-*` errors retain type/code/cause/remediation and are not
  indiscriminately caught/reclassified.
- **EDR-IMPL-DIAG-003:** source/trace/report facts are bounded, redacted, versioned, and labeled
  static/registered/dynamic/observed without executing callbacks to fill gaps.
- **EDR-IMPL-DIAG-004:** production versus trusted CLI/development audiences receive the contracted
  redaction/remediation detail without leaking private installation/application state.

## Security requirements (`EDR-IMPL-SEC-*`)

- **EDR-IMPL-SEC-001:** every client value crosses an existing typed native path/query/body/form/
  binding boundary; facade descriptors/hidden fields/source metadata never grant authorization.
- **EDR-IMPL-SEC-002:** unsafe methods retain native CSRF, auth dependencies, body/content limits,
  idempotency/revision, target/effect, redirect, and response policy.
- **EDR-IMPL-SEC-003:** app/page/container/handle/frame ownership is checked by exact registry/frame
  identity; cross-app, stale, closed, or detached values fail before output/mutation.
- **EDR-IMPL-SEC-004:** raw HTML/CSS/path/download/import/plugin/package/selector/URL trust cannot be
  obtained through generic strings or request-selected names.
- **EDR-IMPL-SEC-005:** capability resolution uses only the sealed manifest and fixed imports; no
  runtime installer, shell, package index, arbitrary entry point, or request-derived import exists.
- **EDR-IMPL-SEC-006:** output, controls, bindings, forms, targets/effects, source facts, traces,
  cache/session/job/download values, assets, and diagnostics are bounded/redacted before emission.
- **EDR-IMPL-SEC-007:** dependency overrides/cleanup and application transactions remain native/
  application-owned; Edron neither commits nor retains resources implicitly.
- **EDR-IMPL-SEC-008:** adversarial tests cover tampering, collision, traversal, dependency
  shadowing, cache/scope bleed, stale/replay, import confusion, XSS/CSS/CSP, redirects, jobs, and
  downloads across HTMX and ordinary HTTP.

## Accessibility requirements (`EDR-IMPL-A11Y-*`)

- **EDR-IMPL-A11Y-001:** each Edron method selects an existing semantic native component; styling
  and variants cannot change role/name/state/order or provide the only interaction meaning.
- **EDR-IMPL-A11Y-002:** labels, descriptions, validation/error summaries, required/invalid state,
  safe-value retention, focus, keyboard, busy, status, and announcement behavior remain native.
- **EDR-IMPL-A11Y-003:** layouts/containers/tabs/expanders preserve keyboard operation, source/DOM
  order, landmarks/headings, reflow/zoom, RTL, print, forced colors, reduced motion, and no-JS use.
- **EDR-IMPL-A11Y-004:** action confirmation, failure/conflict/stale/delete focus recovery, and job
  polling announcements follow the accepted native interaction contracts.
- **EDR-IMPL-A11Y-005:** first-party charts/maps require descriptions and accessible data/semantic
  alternatives for Supported claims; optional adapters retain native limitations/maturity.
- **EDR-IMPL-A11Y-006:** Edron themes/recipes/CSS pass contrast/mode/motion/focus and package
  composition evidence without claiming that a theme repairs inaccessible application content.
- **EDR-IMPL-A11Y-007:** automated semantic/browser/axe evidence plus the scoped human protocol
  covers all golden/focused fixtures and does not overstate untested screen-reader/platform claims.

## Performance and resource requirements (`EDR-IMPL-PERF-*`)

- **EDR-IMPL-PERF-001:** class compilation is deterministic and at most linear in declared page
  surfaces plus native validation; it invokes no author callback/service.
- **EDR-IMPL-PERF-002:** request lowering is at most linear in emitted nodes, controls, bindings,
  and declared target edges within frozen limits; it does not re-execute author methods.
- **EDR-IMPL-PERF-003:** there is one Edron lowering and one native render/response pass; no copied
  component tree, HTML parse/rewrite, or duplicated asset planning occurs.
- **EDR-IMPL-PERF-004:** reflection/signature/native projection work is cached per immutable
  app/class registration, not repeated per output call/request.
- **EDR-IMPL-PERF-005:** root import is bounded and does not load first-party subtrees unnecessarily
  or any optional ecosystem; capability metadata/import probes are lazy and bounded.
- **EDR-IMPL-PERF-006:** ContextVar frames/buffers/traces/source facts are request-bounded and fully
  released; caches use explicit native scope/limits and optional negative facts cannot grow by
  request input.
- **EDR-IMPL-PERF-007:** native-versus-Edron differential benchmarks freeze import, registration,
  page/fragment/action latency, allocation/node, HTML/metadata/assets, CLI, and package size budgets
  before acceptance.

## Testing implementation

Every requirement maps to a test/fixture and acceptance-manifest entry. The minimum lanes are:

| Lane | Required implementation evidence |
|---|---|
| unit | descriptors, class validation, definitions, frames, buffers, containers, source mapping, lowering, codes, capability classification |
| integration | fresh full/fragment/action requests, DI/cleanup, forms, outcomes, fallback, filters, jobs, downloads, styles/assets |
| differential | explicit native lowerings produce equivalent registrations/policies/HTTP meaning |
| typing | root exports, method returns, generic inputs, descriptors/bindings, dependencies, native handles, identity re-exports |
| security | all `EDR-IMPL-SEC-*` adversarial fixtures, redaction, package/import attacks |
| accessibility | semantic snapshots, keyboard/focus/status, axe/browser modes, no-JS, human protocol |
| concurrency | parallel requests, await/thread context propagation, cancellation, late responses, duplicate submits/polls, cleanup/no leakage |
| capabilities | absent/direct/extra/incompatible/broken for every curated adapter with exact native identity/output |
| packaging | wheel/sdist/metadata/assets/typing/CLI/clean install/offline import/version train/upgrade/rollback |
| performance | frozen numeric import/compile/request/allocation/asset/package/CLI budgets against native fixtures |
| goldens | all six applications plus focused map/editor/native/CLI/state/optional fixtures from the inventories |

Tests never call private functions as the sole proof of HTTP/security behavior. Request tests use
the normal ASGI/native routes. Scenario helpers may improve clarity but retain raw method/status/
headers/body assertions. Multi-worker/process restart evidence is required for claims that cross a
single process.

### Static/type/API checks

- AST/source check fixtures contain positive, invalid, dynamic, imported-alias, and unsupported
  patterns and prove that static output is conservative.
- API snapshots verify exact root `__all__`, signatures, annotations, descriptor introspection,
  docs, diagnostic codes, and no accidental private re-exports.
- Supported type-checker lanes verify golden source and negative misuse without plugins that hide
  runtime/API problems.
- import-budget tests record imported modules and patch network/file/process functions to prove
  inert root import.

### Browser and fallback checks

Every interaction fixture runs enhanced and no-JavaScript paths. Browser tests cover supported
engines and native HTMX extension present/absent behavior, but raw HTTP remains the correctness
authority. Focus/busy/history/stale/OOB/asset cleanup and rapid interaction races are explicit.

## Work breakdown

### Stage 0 — design and native audit (current; no runtime code)

1. Approve RFC/API/state/packaging/inventory/specification documents together.
2. Freeze numeric limits/performance budgets, Python/platform matrix, package requirements, and
   public maturity policy.
3. Assign every `UP-001`–`UP-011` row to an Existing public authority or a separately accepted
   Hedron contract/owner/evidence plan.
4. Create the machine-readable Edron capability, upstream, package, and release-gate manifests.
5. Approve golden/focused fixture sources and security/accessibility/human protocols.

Exit requires Decision A in the acceptance packet. It accepts the design and may authorize the
independent native work in Stage 1; it does not authorize `packages/edron` runtime code.

### Stage 1 — reusable Hedron enablement

Implement unresolved native contracts in owning Hedron packages under their own requirements,
tests, changelogs, and release decisions. Work is independently useful and contains no import/runtime
dependency on Edron. Freeze the first shipped compatible Hedron train only after all required
native evidence passes.

Stage 1 also completes the package/API/lowering/state/fixture/performance locks, checker/CI lanes,
security corpus, accessibility protocol, and exact implementation-entry review. Exit requires
Decision B; satisfying only one Edron surface's native prerequisite cannot authorize a partial
facade runtime.

### Stage 2 — Edron package foundation

- add workspace/build/typing/CLI skeleton and clean artifact metadata;
- implement root export allowlist, exceptions/diagnostics/source records;
- implement inert import and lazy capability manifest/resolver;
- add `App` construction/from-native delegation and baseline native identity tests; and
- establish unit/type/artifact/security/performance harnesses.

No interaction facade is exported until its native prerequisites and slice tests pass.

### Stage 3 — definitions, class compiler, and static output

- implement `Page`, containers/output frame, descriptors, class inspection, source index;
- integrate the accepted native class/source projection compiler atomically;
- implement text/feedback/layout/metric/Markdown/basic table plus native `include`;
- implement `app.native`, `app.hedron`, native feature/style delegation; and
- land hello/native-composition goldens and differential registration tests.

### Stage 4 — safe and unsafe interactions

- implement safe inputs/filter scopes through the native coherent GET plan;
- implement fragment/action descriptors, bindings, request execution phases;
- implement button/confirmation/Pydantic forms/outcomes/effects/idempotency/fallback;
- implement dependency descriptor, cache wrapper, typed session composition; and
- complete HTTP/HTMX/no-JS/concurrency/security/accessibility interaction suites.

### Stage 5 — first-party batteries, optional adapters, and styling

- implement tables/dataframe coercion and first-party chart/map methods;
- verify native data-editor access without adding an Edron editor surface;
- implement Plotly/Altair/Matplotlib methods and data/SQLAlchemy capability resolution paths;
- implement theme/variants/recipes/scopes/CSS package-wide behavior; and
- complete optional/base clean installs, assets, visual/a11y, and styling tooling fixtures.

### Stage 6 — jobs, downloads, CLI, and explanation

- implement `JobFlow`, job mount/result output, and production-backend gate;
- implement opaque/bytes download paths;
- complete run/check/register/explain/doctor/style commands and report schemas; and
- complete golden jobs plus focused CLI/state/native/package fixtures.

### Stage 7 — hardening and release cut

- run full Python/platform/browser/wheel/sdist/upgrade/rollback matrices;
- freeze all numeric budgets, resolved dependency locks, assets/licenses/advisories/provenance;
- complete human accessibility/security/release review and docs/tutorial/deployment/migration guides;
- build artifacts from the tag and verify hashes in clean external environments; and
- publish `0.1.0` only when every release-gate row is Verified.

Stages may be split into smaller PRs, but dependency order and authority boundaries cannot be
reordered for convenience. A merged internal slice does not create a public availability claim.

## Required acceptance artifacts

Before Edron runtime implementation begins, Stages 0 and 1 create and verify versioned
machine-readable artifacts equivalent to:

| Artifact | Required contents |
|---|---|
| Edron release gate | every normative RFC/API/state/package/inventory/spec requirement and evidence owner/status |
| capability manifest | base/optional/native/deferred IDs, distribution ranges, imports, owners, maturity, diagnostics |
| upstream lock | `UP-001`–`UP-011`, native contract/symbol/version/tests/owner/rollback disposition |
| package lock | Python/platform matrix, required/optional resolved requirements, wheel/sdist/assets/licenses |
| public API snapshot | root exports, signatures, annotations, return/identity rules, diagnostic codes |
| lowering matrix | Edron surface → exact native descriptor/node/route/policy/assets/source projection |
| state/interaction matrix | owners, lifetimes, methods, targets, concurrency, fallback, security, a11y |
| golden/focused fixture lock | source hashes, expected native lowering, evidence lanes, maturity/limitations |
| performance lock | numeric import/compile/request/allocation/output/asset/package/CLI budgets |
| human protocol | scoped keyboard/screen-reader/visual-mode/no-JS/security review and evidence limits |

Generated/checking scripts may derive reports from these artifacts, but there is one authority per
fact and CI fails drift. Release status is never inferred from document prose or test filenames.

## Traceability requirements

- **EDR-IMPL-TRACE-001:** every public API/inventory capability maps to implementation requirements,
  owning modules, native projection, tests, docs, and release-gate evidence.
- **EDR-IMPL-TRACE-002:** every `Enable` capability maps to one existing/shipped native contract;
  no Edron module is accepted as substitute evidence.
- **EDR-IMPL-TRACE-003:** every stable diagnostic code has one factory/category, test matrix,
  source/redaction policy, and JSON/SARIF fixture.
- **EDR-IMPL-TRACE-004:** built metadata/capability manifest/docs/doctor/optional errors and owning
  adapter ranges are mechanically compared.
- **EDR-IMPL-TRACE-005:** public identity re-exports/native projections have `is`/registry/asset/
  route/effect differential evidence rather than name/shape similarity.
- **EDR-IMPL-TRACE-006:** every Deferred item has a negative API/static/typing test preventing
  accidental exposure.

## Completion criteria

The implementation specification is satisfied only when:

- every RFC and companion acceptance criterion is Verified in the release gate;
- every `EDR-IMPL-SEC-*`, `EDR-IMPL-A11Y-*`, `EDR-IMPL-PERF-*`, and
  `EDR-IMPL-TRACE-*` requirement has passing evidence;
- all required upstream Hedron contracts are shipped in the frozen compatible train;
- every inventoried public/conceptual declaration and the exact root export allowlist pass
  API/typing tests;
- all golden/focused, HTTP/HTMX/no-JS, native differential, capability, concurrency, security,
  accessibility, performance, upgrade, and artifact matrices pass;
- built wheel/sdist clean installations behave identically to the accepted workspace behavior; and
- release review finds no private native dependency, duplicated authority, hidden optional gate,
  runtime installer, global state leak, callback-at-registration, or unsupported maturity claim.

## See also

- [RFC-0094](../rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)
- [Edron public API](../api/EDRON.md)
- [Edron state and interaction](../api/EDRON_STATE_INTERACTION.md)
- [Edron packaging](../api/EDRON_PACKAGING.md)
- [Edron capability inventories](EDRON_CAPABILITY_INVENTORIES.md)
- [Edron golden applications](EDRON_GOLDEN_APPS.md)
- [Edron acceptance packet](../acceptance/EDRON_001.md)
- [Hedron refreshable views and commands](../api/REFRESHABLE_VIEWS.md)
- [Hedron type-driven authoring](../api/TYPE_DRIVEN_AUTHORING.md)
- [Hedron package-native workflows](../api/PACKAGE_WORKFLOWS.md)
- [Hedron application styling](../api/APPLICATION_STYLING_065.md)
- [Hedron state](../api/STATE.md)
- [Hedron jobs](../api/JOBS.md)
