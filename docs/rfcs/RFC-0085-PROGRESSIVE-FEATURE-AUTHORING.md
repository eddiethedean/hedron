# RFC-0085: Progressive feature authoring and inspectable lowering

**Status:** Accepted  
**Target phase:** 0.58 (`v0.58.0`)  
**Decision:** D-101  
**Stage 0 contract refine:** D-102  
**Required predecessor:** Published and Verified in-tree `v0.57.0` (satisfied; tag/PyPI deferred)  
**Planning baseline:** Published/Verified in-tree `v0.57.0`  
**Tracking:** `docs/acceptance/progressive-tracking-058.toml`

**Revision:** 2026-08-21 — D-102 Stage 0 refine accepted against the completed in-tree 0.57 cut.
The acceptance packet freezes signatures, schemas, diagnostics, dispositions, budgets, scaffolds,
starter adoption, tracking, gates, and upgrades without runtime or version changes.

## Summary

Phase 0.58 adds a beginner-facing, feature-level authoring layer for common Hedron applications
while preserving the existing explicit APIs as the runtime authority. The new layer covers screens,
form commands, data workspaces, durable task UI, dashboards, session login plumbing, and upload
flows. Each facade lowers to ordinary `Page`, `FragmentHandle`, `ActionHandle`, `FeatureBundle`,
`InteractionCatalog`, security, job, upload, and presentation contracts already shipped in
0.43–0.57.

This is progressive disclosure, not a second framework. An author can move down one rung at a time:

1. start from a scaffold or feature facade;
2. access and replace named generated surfaces;
3. inspect the complete lowering and policy graph;
4. eject reviewable explicit Python for one surface or a whole feature; or
5. use `@app.page`, `@app.command`, `@app.refreshable`, native components, HTML, responses, and
   FastAPI directly.

Authorization, persistence, transactions, tenancy, destructive meaning, durable workers, storage,
malware scanning, identity verification, and external exposure remain explicit application-owned
boundaries.

## Motivation

Hedron's low-level and mid-level contracts are capable, but a beginner must currently cross too
many boundaries at once. A small form-driven application can require `Page`, layout components,
Pydantic `Annotated` metadata, `FormBody`, `Control`, generated form handles, refresh effects,
fallbacks, CSRF behavior, and route knowledge. Durable work adds backend submission, scope
repetition, a status route, `ComponentRef`, polling, terminal behavior, and result presentation.
Authenticated CRUD or dashboard assembly adds still more interaction and shell concepts before the
application's domain behavior becomes visible.

The repository already contains the required lowering architecture:

- 0.43: refreshable views, command handles, hosts, updates, and generated routes;
- 0.44: Pydantic boundaries, generated forms, controls, effects, and outcomes;
- 0.45: the read-only interaction catalog and package projections;
- 0.46: `FeatureProvider`, atomic `FeatureBundle`, `DataWorkspace`, overrides, and feature ejection;
- 0.54–0.57: application chrome, workflow security, upload controls, the security control plane,
  and a complete default presentation vocabulary.

0.58 composes those contracts into coherent user intentions. It does not replace or fork them.

## Design principles

1. **One runtime.** Facades lower to existing public Hedron/FastAPI contracts.
2. **Mechanics may be inferred; authority may not.** Layout, CSRF field placement, form encoding,
   target wiring, polling markup, and catalog descriptions may be derived. Business authorization,
   persistence, destructive meaning, transaction boundaries, external exposure, and trust may not.
3. **The lowering is observable.** Generated routes, handles, schemas, effects, policies, assets,
   dependencies, limitations, and source provenance are inspectable without invoking handlers.
4. **Graduation is local.** Replacing or ejecting one generated surface does not require rewriting
   the feature or changing application mode.
5. **No beginner namespace or mode switch.** High-level APIs live beside existing APIs and may be
   mixed in one application.
6. **Useful without JavaScript.** Screens, forms, task status, auth, uploads, and workspace actions
   retain ordinary HTTP paths and accessible native markup.
7. **Finite, bounded defaults.** Fan-out, fields, routes, generated surfaces, payloads, polling,
   uploads, and descriptions consume existing limits or Stage 0 locks; no unbounded discovery.
8. **No hidden I/O during render.** Feature loaders and mutation handlers remain explicit request
   boundaries. Rendering remains deterministic.

## Authoring ladder

| Level | Author experience | Runtime representation |
|---|---|---|
| Scaffold | `hedron new --template minimal|crud|dashboard|task` | Ordinary checked-in Python |
| Intent | `@app.screen`, `@app.form_command`, feature providers | Existing page/handle/bundle contracts |
| Surface override | Replace a named screen/view/command/form/panel | Ordinary explicit handler/component |
| Ejection | `hedron eject features:<id>` or a named surface | Reviewable Python plus source map/tests |
| Primitive | Existing pages, handles, regions, components, responses, FastAPI | No facade dependency |

The high-level API remains valid indefinitely; ejection is not required for production and is not a
deprecation path. The ladder exists so complexity can be adopted when it earns its place.

## Common lowering and explanation contract

`FeatureProvider.to_bundle()` remains the only feature compilation seam. 0.58 does not add a
parallel workflow runtime, mutable graph, registry, or manifest. New providers compile into an
ordinary atomic `FeatureBundle`; screen/form decorators compile directly into existing page and
handle descriptors.

The catalog and descriptors remain authoritative. A new read-only explanation projection may make
them approachable:

```python
explanation = app.explain_feature(orders)

explanation.logical_id
explanation.surfaces       # named pages, views, commands, forms, and panels
explanation.routes         # methods, paths, fallbacks, dependencies
explanation.effects        # refresh/update relationships
explanation.security       # CSRF/auth/scope facts, redacted
explanation.limitations    # declared non-capabilities
explanation.source         # facade/provider provenance
```

Conceptual rules:

- the explanation is compiled from registered descriptors, `TypeSchema`, bundle metadata, and the
  interaction catalog; it never becomes a second source of truth;
- explanation is static/read-only and must not call data sources, authorization hooks, handlers,
  workers, remote services, or user callbacks;
- sensitive values and callable representations follow 0.56 redaction/provenance contracts;
- every facade-owned surface has a stable name suitable for override, scenario, explanation, and
  ejection;
- generated source records a source map back to the facade configuration and passes a behavioral
  parity scenario before it is presented as a successful ejection;
- ejection never overwrites by default and writes only inside the selected project root.

CLI projection:

```text
hedron --app app:app explain features:orders
hedron --app app:app graph --level feature
hedron --app app:app eject features:orders --surface list
hedron --app app:app check --features
```

Exact command spelling and serialized schema are locked at Stage 0.

## `Hedron.screen`

`@app.screen` is the beginner page decorator. It registers one normal navigable page and returns a
`ScreenHandle` suitable for links, navigation, inspection, and tests.

```python
@app.screen("/", title="Home")
def home():
    return [
        Text("Hello"),
        status(),
        status.refresh_button(),
    ]
```

Conceptual signature:

```python
def screen(
    path: str,
    *,
    title: str,
    layout: Literal["stack", "grid", "plain"] = "stack",
    shell: object | None = None,
    navigation: object | None = None,
    dependencies: Sequence[Depends] | None = None,
    **page_options: object,
) -> Callable[[Callable[..., NodeLike | Sequence[NodeLike] | Page]], ScreenHandle]: ...
```

Contract:

- `title` is required; it is not guessed from a function name or URL.
- A node or bounded sequence is wrapped in the selected 0.57 layout and a `Page`.
- Returning an explicit `Page` is an immediate escape hatch. Conflicting decorator/page metadata
  fails registration rather than silently choosing one.
- `ScreenHandle` exposes `path`, `name`, `title`, `handler`, `link()`, and read-only descriptor
  facts. It does not make arbitrary nested components addressable.
- Shell/navigation configuration consumes 0.54/0.57 chrome; domain authorization for a screen
  remains an explicit dependency.
- `@app.page` stays unchanged and canonical for full document control.

An app-level shell/navigation helper may accept only explicit `ScreenHandle`/link values. Route
discovery never invents a navigation tree and hidden/unauthorized pages are not inferred.

## `Hedron.form_command`

`@app.form_command` makes “a typed native form submits this command” explicit at the decorator,
removing the need for a beginner to spell `Annotated[Model, FormBody()]`.

```python
class NoteInput(BaseModel):
    body: str = Field(min_length=1, title="Note")


@app.form_command(
    "/notes",
    refreshes=(notes,),
    success="Note added",
    fallback="/",
)
def create_note(data: NoteInput):
    save_note(data)
```

Contract:

- exactly one supported Pydantic input model is the form boundary; all other parameters must be
  documented dependencies/request context;
- the decorator supplies the existing `FormBody` marker and compiles through the 0.44 type
  authoring path—there is no second parser or validator;
- Pydantic field title/description/constraints provide conservative controls; explicit 0.44
  `Control` metadata or form-control overrides remain available;
- the returned value is the ordinary `ActionHandle`, including `.form()` and `.button()`;
- `refreshes`, `updates`, success presentation, outcomes, authorization dependencies, fallback,
  encoding, and limits are declarative mechanics and appear in descriptors;
- contradictory handler-return effects and decorator effects fail clearly. An explicit
  `InteractionResult`, response, or effect uses `@app.command` when it exceeds the facade contract;
- JSON, arbitrary bodies, transactions, commits, retries, idempotency, authorization, and
  destructive meaning are never inferred;
- unsafe methods retain the active CSRF strategy and native forms retain an ordinary fallback.

`@app.command` plus `Annotated[..., FormBody()]` remains the advanced spelling and receives no
behavior change.

## Data workspace screens

0.58 evolves the existing `hedron_data.DataWorkspace` instead of introducing a competing
`Resource`/CRUD runtime. A workspace may opt into complete page composition:

```python
orders = DataWorkspace(
    name="orders",
    model=Order,
    source=authorized_orders,
    policy=DataWorkspacePolicy(
        can_read=can_read_orders,
        can_create=can_create_order,
        can_edit=can_edit_order,
    ),
).with_screen(path="/orders", title="Orders")

app.include_feature(orders)
```

The generated named surfaces are at least:

- `screen`;
- `list_view` and `detail_view`;
- `create_command` and `edit_command` when authorized by explicit policy;
- `create_form` and `edit_form` projections;
- filter/search/pagination controls backed by the existing bounded data query;
- declared empty, validation, not-found, forbidden, and conflict states.

Deletion remains disabled unless all existing destructive requirements are supplied. The
workspace never discovers an ORM, ambient manager, relationship graph, tenant scope, transaction,
or authorization rule. Existing `list_override`, `detail_override`, `create_override`,
`edit_override`, and ejection remain the per-surface graduation path. Stage 0 decides whether a
typed immutable override object replaces the current loose override keyword inventory; either
choice must preserve source compatibility.

## `TaskFlow`

`hedron.jobs.TaskFlow` owns the repetitive HTTP/UI mechanics around an application-operated durable
job backend. It does not run workers or become a scheduler.

```python
reports = TaskFlow(
    name="report",
    input_model=ReportRequest,
    job_type="build-report",
    payload=report_payload,
    scope=current_job_scope,
    authorize_submit=can_build_report,
    result=report_result,
)

app.include_feature(reports)
```

Generated surfaces:

- `submit_command` and generated form;
- an opaque task ticket/result carrying the job id without exposing backend internals;
- `status_view` using the configured `JobBackend` and exact stored subject/tenant scope;
- bounded `Poll` presentation that stops on terminal states;
- optional explicitly authorized `cancel_command`;
- queued, running, succeeded, failed, cancelled, missing, forbidden, and backend-unavailable states.

Contract:

- `JobBackend`, worker registration, retry policy, retention, payload durability, result storage,
  and backend-unavailable behavior remain application/backend-owned;
- one typed `JobScope` provider supplies subject/tenant identity consistently to submit, status,
  cancel, and result paths; it is evaluated per request and never copied into generated source;
- result rendering receives an already-authorized terminal result; downloads use existing safe
  response helpers;
- polling is the Supported default; SSE remains an explicit Experimental replacement;
- task status URLs are addressable only through declared generated routes and do not expose
  unscoped job enumeration;
- payload/result sizes, polling frequency, fan-out, cancellation, and disconnect cleanup use
  existing budgets or Stage 0 locks.

## `DashboardWorkspace`

`hedron.dashboard.DashboardWorkspace` composes explicit typed filters, one request-bound loader,
and named render-only panels. It is not a client state store or callback graph runtime.

```python
sales = DashboardWorkspace(
    name="sales",
    path="/sales",
    title="Sales",
    filters=SalesFilters,
    load=load_sales,
    panels={
        "summary": render_summary,
        "trend": render_trend,
        "orders": render_orders,
    },
)

app.include_feature(sales)
```

Contract:

- filter state is represented by an explicit typed URL/query boundary by default; sensitive fields
  are rejected from public URLs;
- `load` is an explicit request/I/O boundary; panel rendering is deterministic and performs no
  hidden I/O;
- named panels become ordinary refreshable/bound views and may return charts, tables, maps, or any
  `NodeLike` without importing optional packages into `hedron`;
- filter submission compiles to a bounded refresh/update set and optional history URL;
- fan-out, cycles, query size, panel count, payload, caching, stale requests, and errors use existing
  graph/update/cache policies and are visible in explanation;
- a panel can be replaced or ejected independently; advanced linked interactions use the existing
  `InteractionGraph`, `ChartInteraction`, patches, or explicit handles.

## `SessionAuthFlow`

`hedron.auth.SessionAuthFlow` composes login/logout/session page plumbing around explicit
application identity operations. It is not an identity provider, user database, password hasher,
role system, or authorization framework.

```python
auth = SessionAuthFlow(
    credentials=LoginInput,
    authenticate=authenticate_user,
    serialize_principal=principal_to_session,
    load_principal=principal_from_session,
    login_path="/login",
    after_login="/",
)

app.include_feature(auth)
```

Contract:

- authentication success/failure is returned through a closed typed result, not exception/string
  guessing;
- login CSRF, generic failure presentation, safe local redirects, session rotation, cache policy,
  logout, and existing session timeout hooks are composed from shipped security contracts;
- rate-limit and credential-validation authority must be explicit; production configuration fails
  if required controls are absent;
- session contents use an explicit bounded serializer and never store arbitrary principal objects;
- authorization remains ordinary dependencies/policies supplied to screens and commands;
- OIDC/provider discovery, account recovery, registration, MFA, password storage, and role/tenant
  inference are outside 0.58.

## `UploadFlow`

`hedron.files.UploadFlow` composes a secure upload form, accepted-result view, and optional durable
processing task from explicit application storage and authorization hooks.

```python
documents = UploadFlow(
    name="documents",
    field=document_upload_field,
    authorize=can_upload_document,
    store=store_quarantined_document,
    result=document_result,
)

app.include_feature(documents)
```

Contract:

- upload limits, media/extension policy, parser reservation, cleanup, filenames, and CSRF reuse the
  0.55/0.56 authorities; display and enforcement cannot drift;
- application callbacks own storage, tenancy, malware scanning, quarantine release, retention,
  deduplication, and downstream processing;
- raw paths, storage credentials, temporary locations, and untrusted filenames never enter public
  markup or explanation;
- progress is ordinary bounded status/polling unless an explicit Experimental transport replaces
  it;
- download is a separate explicitly authorized result surface;
- native multipart submission and useful validation/error pages remain available without HTMX.

## Scenarios, scaffolds, and teaching path

Every 0.58 facade ships at least one deterministic `AppScenario` recipe covering its ordinary
success, validation, authorization denial, CSRF denial where applicable, native HTTP fallback,
HTMX path, and generated/ejected parity. Providers attach scenarios to their `FeatureBundle` rather
than introducing a scenario runtime.

The scaffold inventory becomes finite:

```text
hedron new my-app --template minimal
hedron new my-app --template crud
hedron new my-app --template dashboard
hedron new my-app --template task
```

Templates generate ordinary small Python projects with bounded dependency pins. They do not add a
project generator DSL. `minimal` teaches `screen` and one refreshable view; `crud` teaches
`DataWorkspace`; `dashboard` teaches typed filters/panels; `task` uses a test/development backend
with a visible production replacement note. Generated production startup remains governed by
existing gates.

The documentation learning path teaches one concept per step:

1. screen and static components;
2. refreshable view;
3. form command;
4. workspace or dashboard;
5. inspect a lowering;
6. override one surface;
7. eject and compare explicit code;
8. production authorization, persistence, jobs, uploads, and deployment.

### Starter-example adoption policy

At the 0.58 cut, every maintained documentation example identified as **starter**,
**beginner**, **quick start**, **golden path**, **minimal**, **first app**, or generated
**scaffold** uses the highest applicable 0.58 abstraction. This includes the root and flagship
README first-app examples, getting-started pages, beginner cookbook/recipe entries, starter
single-file examples, scaffold snapshots, and package quick starts that demonstrate an affected
workflow.

The teaching order is normative:

1. show `screen`, `form_command`, or the applicable workspace/flow facade first;
2. show the compiled or ejected explicit equivalent afterward when it helps understanding; and
3. link to the existing primitive API for customization.

A document whose purpose is specifically to teach `Page`, `FormBody`, handles, regions,
`InteractionResult`, raw HTML, responses, or host-native integration may use the explicit API, but
it must be labeled **Advanced**, **Explicit**, **Lower-level**, or **Under the hood** and must not be
presented as a starter path. Historical release notes and migration fixtures retain historically
accurate code. Stage 0 freezes a machine-readable starter-example inventory; `DX-058` fails if an
inventoried starter remains on a lower-level spelling without a recorded purpose and destination.

## Adapter and package behavior

FastAPI flagship facades are the initial authoring surface. Portable components, bundle metadata,
and explanations remain framework-neutral where their existing authorities are portable.

- Flask/Django do not receive fake `@app.screen`/`@app.form_command` parity unless their native
  adapters can preserve routing, form, dependency, session, and CSRF authority.
- Stage 0 records each facade as Supported, composition-only, explicit-adapter spelling, or
  Deferred per host.
- `DataWorkspace` retains its current cross-host source/component contracts; FastAPI-only screen
  composition must not change portable behavior.
- optional packages remain package-local and add no imports/assets/startup cost when absent.
- MCP/Gradio exposure stays separate and deny-by-default; including a facade never publishes it to
  another protocol.

## Errors and diagnostics

Stage 0 reserves and locks diagnostic families without renumbering existing codes:

- screen metadata/return conflicts;
- form-boundary ambiguity and effect conflicts;
- feature surface naming/override/ejection conflicts;
- task scope/backend/status/result failures;
- dashboard filter/panel/fan-out/stale-request failures;
- auth configuration/session/result failures; and
- upload storage/result/policy composition failures.

Diagnostics identify the high-level intent and the lowered primitive that failed, include a
concrete advanced spelling or override when useful, and remain redacted under 0.56. Exceptions from
application callbacks preserve their existing security/HTTP behavior and are not broadly converted
into facade-specific success states.

## Package ownership

| Package/module | 0.58 responsibility |
|---|---|
| `hedron-core` | Portable explanation schema derived from existing bundle/catalog facts; no FastAPI imports or second registry |
| `hedron.app` | `screen`, `ScreenHandle`, `form_command`, page/form lowering |
| `hedron.features` | Read-only explanation, stable named-surface/source-map helpers, ejection parity |
| `hedron.jobs` | `TaskFlow`, task tickets, scoped status/cancel/result composition |
| `hedron.dashboard` | Typed filters, request loader boundary, named panel feature provider |
| `hedron.auth` | `SessionAuthFlow` over existing session/security contracts |
| `hedron.files` | `UploadFlow` over existing upload/download/security contracts |
| `hedron-data` | `DataWorkspace.with_screen`, complete workspace composition and overrides |
| CLI / Explorer | Explain, graph, check, preview, and eject the same catalog facts |
| adapters/conformance/sim | Explicit capability disposition and portable evidence only |

No new distribution is authorized by this phase.

## Delivery workstreams

| Workstream | Deliverable | Depends on |
|---|---|---|
| W0 | Stage 0 contract, inventories, diagnostic families, host dispositions | Published/Verified 0.57 |
| W1 | Shared explanation/named-surface/source-map projection | W0; 0.45/0.46 catalog/bundles |
| W2 | `screen`, `ScreenHandle`, shell/navigation composition | W0; 0.54/0.57 presentation |
| W3 | `form_command` and effect-conflict rules | W0; 0.43/0.44 handles/types |
| W4 | `DataWorkspace.with_screen` and CRUD scaffold | W1–W3 |
| W5 | `TaskFlow`, scope, polling, cancel/result surfaces | W1, W3; jobs/security |
| W6 | `DashboardWorkspace`, filters/load/panels/history | W1–W3; interaction graph |
| W7 | `SessionAuthFlow` | W1–W3; 0.56 security |
| W8 | `UploadFlow` | W1, W3, W5; 0.55/0.56 uploads |
| W9 | CLI/Explorer explain, preview, per-surface override/ejection | W1–W8 |
| W10 | Four scaffolds, all starter-example migrations, learning path, migration recipes | W2–W9 |
| W11 | Adapter/conformance/sim dispositions and scenarios | W2–W10 |
| W12 | Security, a11y, browser, performance, regression, packaging evidence | all |

W2 and W3 are the minimum coherent vertical slice. W4–W8 may develop in parallel only after W1
contracts are frozen. A facade that cannot satisfy its security, native fallback, explanation, and
ejection requirements moves to a named later phase rather than weakening the common contract.

## Gate plan

| Gate | Verified means |
|---|---|
| `CONTRACT-058` | Accepted public symbols, lowering rules, named surfaces, diagnostics, host dispositions, and finite inventories |
| `LOWER-058` | Every facade lowers only to shipped authorities; descriptor/catalog/explanation parity and no second runtime |
| `SCREEN-058` | Screen wrapping, explicit `Page` escape, shell/navigation, metadata conflicts, and native page evidence |
| `FORM-058` | One-model form boundary, controls, validation, CSRF, effects, outcomes, native/HTMX parity |
| `RESOURCE-058` | Complete bounded `DataWorkspace` screen, deny-by-default mutations, overrides, and CRUD scaffold |
| `TASK-058` | Scoped durable submit/status/cancel/result UI, terminal polling, backend failures, and no enumeration |
| `DASH-058` | Typed URL filters, loader/panel separation, bounded refresh/history, chart/table neutrality, stale/error behavior |
| `FLOW-058` | Session auth and upload flows preserve explicit trust/storage/authorization ownership and native fallback |
| `EXPLAIN-058` | Static redacted explain/graph/check plus safe source-mapped per-surface/feature ejection and parity |
| `A11Y-058` | Keyboard, screen reader semantics, focus/error/status announcements, no-JS, zoom, motion/color, and 0.57 presentation adoption |
| `SECURITY-058` | CSRF, auth/tenant scope, redirects, sensitive URL rejection, uploads, ejection paths, and exposure separation adversarial evidence |
| `ADAPTER-058` | FastAPI Supported claims plus explicit Flask/Django/conformance/sim dispositions with no false parity |
| `REGRESS-058` | Existing page/command/workspace/job/auth/upload APIs and 0.43–0.57 fixtures remain compatible |
| `DX-058` | Four runnable scaffolds; every inventoried starter example uses the highest applicable 0.58 abstraction; labeled explicit equivalents and measured learning/ejection outcomes |
| `PKG-058` | Wheels, optional-dependency isolation, docs, exports, inventories, upgrade fixtures, metadata, and release rehearsal |

Stage 0 creates machine-readable inventories for public symbols/surfaces, lowering/host
dispositions, explanation/ejection formats, facade security requirements, scaffolds, and upgrade
fixtures. D-101 does not claim those locks exist yet.

## Security implications

The primary risk is that convenience accidentally creates authority. Required adversarial coverage
includes:

- a rendered component or included facade becoming addressable/external without declaration;
- omitted authorization on CRUD mutation, task status/cancel/result, auth routes, or upload result;
- actor/tenant mismatch between task submission and observation;
- sensitive form/filter values entering a URL, catalog, explanation, generated source, log, or
  diagnostic;
- open redirects or untrusted host use after login and form completion;
- CSRF bypass through generated forms, enhanced elements, or native fallback;
- unbounded dashboard fan-out, job polling, data query, form fields, or generated routes;
- upload limit/display drift, parser budget reset, path traversal, filename injection, incomplete
  cleanup, and unauthorized download;
- ejection outside the project, overwrite without opt-in, generated secret material, or generated
  code that widens policy;
- MCP/Gradio/browser exposure inferred from feature inclusion.

Security controls reuse 0.55/0.56 policy, provenance, budgets, signed-intent, egress, redirect,
upload, and redaction authorities. Facades cannot downgrade a host policy.

## Accessibility implications

All facades inherit 0.19 accessibility and 0.57 presentation contracts. Release evidence covers:

- correct document titles, landmarks, headings, navigation labels, and current-page state;
- native labels, descriptions, constraints, retained safe values, field-path errors, error summary,
  focus transfer, and announcements for form commands;
- workspace list/detail/action semantics without illegal nested interactive controls;
- dashboard filter/panel reading order, loading/error status, keyboard equivalence, and tabular/chart
  alternatives;
- queued/running/terminal task state that is not color- or motion-only and does not announce every
  poll noisily;
- generic auth failure, login focus, logout, session timeout, and native redirect behavior;
- upload selection/progress/error/result semantics and keyboard operation;
- native HTTP paths, failed-upgrade behavior, 200% zoom, narrow viewports, reduced motion, forced
  colors, RTL, long content, and fragment replacement.

Generated code and explanations use plain language suitable for a beginner and identify advanced
terms only when they solve the current problem.

## Performance implications

Facades add registration-time compilation and read-only metadata, not an application request
runtime. Equivalent explicit and facade-generated paths have the same rendering/interaction
authorities. Stage 0 sets representative budgets for:

- import and registration overhead with no optional features installed;
- descriptor/explanation size and static inspection time;
- route/surface/form-field/panel counts;
- dashboard load and bounded fan-out;
- polling amplification and terminal shutdown;
- ejection time/output size;
- generated versus explicit render/response parity.

Optional packages remain lazy. Explanation may be cached from sealed descriptors but must
invalidate under the existing catalog/registry lifecycle. No facade may perform data I/O during
import, registration, explanation, schema generation, or ejection.

## Alternatives considered

### A separate `hedron.easy` package or runtime

Rejected. It creates two mental models, a migration cliff, duplicate documentation, and pressure
for semantic drift. Method decorators and package-local feature providers add few root imports and
lower to the existing runtime.

### `simple=True` on the app

Rejected. Complexity is feature-local, not application-wide. Authors must be able to mix a simple
dashboard with one explicit low-level interaction.

### Universal ORM CRUD discovery

Rejected. It violates explicit authorization, tenancy, transaction, and destructive-operation
ownership. `DataWorkspace` continues to require an authorized source and explicit policy.

### Make every callable or component automatically routable

Rejected. Addressability and exposure remain explicit.

### Generate code only; add no runtime facades

Rejected as the sole approach. Scaffolds help the first minute but duplicated generated machinery
still burdens maintenance. Facades plus safe ejection give both a compact maintained path and
reviewable explicit ownership.

### Infer form commands from every `@app.command` signature

Rejected. A distinct decorator clearly declares the form source and avoids changing existing JSON,
dependency, or explicit command behavior.

### Hide job/auth/upload policy behind presets

Rejected. Presentation/mechanics may have presets, but identity, authorization, durable backend,
storage, scanning, retention, and destructive intent remain visible inputs.

## Compatibility and migration

- All 0.58 public APIs begin `beta`.
- `Hedron`, `@app.page`, `@app.refreshable`, `@app.command`, `FormBody`, explicit forms, regions,
  interactions, `DataWorkspace`, jobs, auth helpers, and uploads keep their behavior.
- No existing application is auto-rewritten or auto-opted into a facade.
- Existing `DataWorkspace` overrides remain accepted; any typed override API is additive.
- Existing feature ejection remains accepted; 0.58 may add source maps, surface selection, and
  parity verification without changing the no-overwrite/project-root safety contract.
- Root-facade growth is minimal: app methods need no imports; feature classes remain in
  `hedron.jobs`, `hedron.dashboard`, `hedron.auth`, `hedron.files`, and `hedron_data`.
- Flask/Django behavior changes only where a host-specific supported spelling is explicitly
  accepted at Stage 0.
- Upgrade fixtures start from Published/Verified in-tree `v0.57.0`; its deferred registry upload
  does not change the source baseline.

## Resolved questions (D-101)

1. **Second runtime?** No. Existing handles, bundles, catalog, components, and host routes remain
   authoritative.
2. **Beginner namespace/mode?** No. Use additive app methods and package-local feature providers.
3. **Primary page facade?** `@app.screen`, with required title and explicit `Page` escape.
4. **Primary form facade?** `@app.form_command`, with exactly one Pydantic model boundary compiled
   through existing `FormBody` behavior.
5. **New CRUD runtime/name?** No. Extend `DataWorkspace` with complete screen composition.
6. **Jobs?** `TaskFlow` composes durable-job UI; it does not ship workers or a scheduler.
7. **Dashboard state?** Typed URL/query filters by default; no hidden global/client store.
8. **Authentication scope?** Session login/logout plumbing around explicit application callbacks;
   no IdP/user database/roles/OIDC product.
9. **Uploads?** Compose existing security/upload authorities; storage/scanning remain application
   callbacks.
10. **Graduation path?** Named overrides, static explanation, per-surface ejection, and explicit API
    coexistence.
11. **External exposure?** Never inferred from inclusion.
12. **Predecessor?** Published and Verified in-tree `v0.57.0`, now satisfied; Stage 0 uses that
    exact source baseline.

## Resolved questions (D-102)

1. Schemas are `hedron.feature-explanation/1` and `hedron.feature-source-map/1`.
2. `ScreenHandle[P]` is generic over handler parameters; navigation remains explicit.
3. `form_command` locks effects/outcomes/fallback/encoding/controls/dependencies; explicit
   effect-bearing responses conflict rather than merge.
4. Existing DataWorkspace override keywords remain; immutable `FeatureOverrides` is additive.
5. `JobScopeProvider` is evaluated per submit/status/cancel/result request; unavailable fails closed.
6. `DashboardWorkspace[FiltersT, DataT]` uses typed URL filters, one loader, render-only panels,
   and replace-history by default.
7. Supported session auth requires explicit rate limiting and login rotation.
8. Upload storage receives a bounded `UploadHandle`; processing composes `TaskFlow`; downloads are
   separately authorized.
9. FastAPI owns Supported facade claims; Flask/Django use explicit native spelling or composition.
10. `progressive-budgets-058.toml` locks reject-not-slice limits and benchmark targets.

## Acceptance criteria

Phase 0.58 may cut only when:

- Published and Verified in-tree `v0.57.0` is the frozen upgrade source;
- a Stage 0 refine decision resolves every open question and locks finite inventories;
- every facade lowers to existing public authorities with catalog/descriptor/explanation parity;
- all generated surfaces are named, inspectable, replaceable, testable, and safely ejectable;
- authorization, persistence, transactions, tenancy, durable workers, storage, scanning,
  destructive meaning, and external exposure remain explicit;
- native HTTP, HTMX, failed-upgrade, accessibility, strict-CSP, security, adapter-disposition,
  performance, and upgrade evidence pass;
- `minimal`, `crud`, `dashboard`, and `task` scaffolds are runnable from clean wheels and teach the
  intended authoring ladder;
- every inventoried starter/beginner/quick-start/golden-path/minimal/first-app documentation example
  uses the highest applicable 0.58 abstraction, with lower-level spellings confined to clearly
  labeled advanced/explicit/under-the-hood material;
- existing explicit APIs and 0.43–0.57 fixtures remain compatible;
- all `*-058` release gates are Verified with zero Deferred; and
- package/version/release metadata truthfully identifies new APIs as Beta and does not schedule
  1.0.
