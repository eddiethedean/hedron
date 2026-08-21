# RFC-0085: Progressive feature and styling authoring with inspectable lowering

**Status:** Accepted  
**Target phase:** 0.58 (`v0.58.0`)  
**Decision:** D-101  
**Stage 0 contract refine:** D-102 / D-105

**Required predecessor:** Published and Verified in-tree `v0.57.0` (satisfied; tag/PyPI deferred)  
**Planning baseline:** Published/Verified in-tree `v0.57.0`  
**Tracking:** `docs/acceptance/progressive-tracking-058.toml`

**Revision:** 2026-08-21 — D-105 integrates the progressive-styling exploration previously
recorded by superseded D-103/D-104/RFC-0086 into the D-101/D-102 0.58 phase. The single acceptance
packet freezes feature and styling signatures, schemas, precedence, diagnostics, dispositions,
budgets, scaffolds, starter adoption, tracking, gates, and upgrades against the completed in-tree
0.57 cut, without runtime or version changes.

## Summary

Phase 0.58 adds one beginner-facing authoring layer for both application features and presentation,
while preserving the existing explicit APIs as the runtime authority. It covers screens, form
commands, data workspaces, durable task UI, dashboards, session login plumbing, upload flows,
built-in looks, generated brands, semantic style recipes, and explicit local style scopes. Feature
facades lower to ordinary `Page`, handles, bundles, catalogs, security, job, upload, and
presentation contracts; styling facades lower to the existing `Theme`, component props/markers,
style contracts, CSS compiler, cascade, assets, and CSP authorities shipped in 0.43–0.57.

This is progressive disclosure, not a second framework. An author can move down one rung at a time:

1. start from a scaffold using a built-in theme and feature facade;
2. add a generated brand or semantic recipe when distinct intent appears;
3. access and replace a named feature surface or explicit style scope;
4. inspect the complete feature, policy, design, asset, and provenance graph;
5. eject one surface/recipe/group or the complete feature/design; or
6. use explicit pages, commands, components, `Theme`, props, scoped CSS, style contracts, HTML,
   responses, and FastAPI directly.

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
application's domain behavior becomes visible. Styling has the same problem: the first custom look
currently exposes palette compilation, semantic token maps, modes, variants, shape/elevation/
density/navigation groups, component appearance props, scoped selectors, style contracts, build
manifests, cascade layers, and CSP policy before a beginner can express “use this brand accent” or
“make this data region compact.”

The repository already contains the required lowering architecture:

- 0.43: refreshable views, command handles, hosts, updates, and generated routes;
- 0.44: Pydantic boundaries, generated forms, controls, effects, and outcomes;
- 0.45: the read-only interaction catalog and package projections;
- 0.46: `FeatureProvider`, atomic `FeatureBundle`, `DataWorkspace`, overrides, and feature ejection;
- 0.54–0.57: application chrome, workflow security, upload controls, the security control plane,
  and a complete default presentation vocabulary.
- 0.57 styling: built-in themes, `compile_palette`, semantic tokens, closed appearance markers,
  `StyleSymbols`, scoped CSS/style contracts, the AST compiler, asset manifests, cascade layers,
  visual checks, and zero-application-CSS evidence.

0.58 composes all of those contracts into coherent feature and design intentions. It does not
replace or fork them.

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
9. **One styling authority.** `DesignSystem`, recipes, and scopes compile to the current `Theme`,
   props, markers, style contracts, asset policy, and CSS build; they add no registry or cascade.
10. **No semantic behavior from style.** Styling cannot grant authorization, expose a route, choose
    destructive meaning, reorder DOM, hide an authoritative value, or infer application state.
11. **Accessibility and CSP are compiler obligations.** Generated measurable color pairs meet the
    locked targets, adjustments are disclosed, and output remains external/finite/strict-CSP-safe.

## Authoring ladder

| Level | Author experience | Runtime representation |
|---|---|---|
| Scaffold | `hedron new --template minimal|crud|dashboard|task` with a built-in look | Ordinary checked-in Python plus registered `Theme` |
| Intent | Feature facade plus optional `DesignSystem.brand(...)` | Existing page/handle/bundle and `Theme` contracts |
| Reuse | Named semantic style recipe on a generated role or explicit component | Existing family-specific component props/markers |
| Local override | Replace a named feature surface or add an explicit theme/mode/density scope | Explicit handler/component or marker boundary |
| Inspect | Explain/preview/diff the feature and design lowering | Catalog, descriptors, plan, manifests, provenance |
| Ejection | Eject a surface/feature or recipe/group/design | Reviewable Python/CSS/manifests/source maps/tests |
| Primitive | Pages, handles, components, responses, `Theme`, props, style contracts, scoped CSS, FastAPI | No facade dependency |

The high-level API remains valid indefinitely; ejection is not required for production and is not a
deprecation path. The ladder exists so complexity can be adopted when it earns its place.

## Common lowering and explanation contract

`FeatureProvider.to_bundle()` remains the only feature compilation seam. 0.58 does not add a
parallel workflow runtime, mutable graph, registry, or manifest. New providers compile into an
ordinary atomic `FeatureBundle`; screen/form decorators compile directly into existing page and
handle descriptors.

`DesignSystem.to_theme()` is the styling compilation seam. It resolves to an ordinary registered
`Theme`; recipes resolve before render to existing optional component props; `StyleScope` resolves
to an explicit marker boundary; CSS and assets continue through the existing compiler/manifests.
The design plan is read-only metadata, not a runtime styling registry. Feature surfaces link to
design-plan targets through stable logical IDs so the two lowerings can be traversed without
duplicating or merging their authorities.

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
- every generated presentation node with a style default has a finite semantic role and provenance
  link; explicit props and named-surface replacements remain stronger;
- generated source records a source map back to the facade configuration and passes a behavioral
  parity scenario before it is presented as a successful ejection;
- ejection never overwrites by default and writes only inside the selected project root.

CLI projection:

```text
hedron --app app:app explain features:orders
hedron --app app:app graph --level feature
hedron --app app:app eject features:orders --surface list
hedron --app app:app check --features
hedron --app app:app style explain --format human
hedron --app app:app style preview --output .hedron/preview --mode all
hedron --app app:app style diff BASE CANDIDATE --format human
hedron --app app:app style eject NAME --recipe primary_action --output generated
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

## Progressive styling abstractions

The styling side uses the same rule as feature authoring: begin with a bounded expression of intent,
show exactly how it lowers, and allow local graduation without an application-wide mode switch.
`Theme`, semantic tokens, component props, appearance markers, `StyleSymbols`, scoped CSS, style
contracts, the AST compiler, cascade layers, assets, and CSP remain authoritative.

### Built-in looks and `DesignSystem.brand`

The zero-config path remains an existing registered theme:

```python
app = Hedron(theme="aurora")
```

The smallest custom-design path is one trusted brand accent plus finite choices:

```python
design = DesignSystem.brand(
    name="acme",
    accent="#2f6fed",
    density="comfortable",
    geometry="soft",
    typography="system-sans",
)

app = Hedron(theme=design)
```

`DesignSystem.brand`, `from_theme`, `to_theme`, `with_recipes`, `apply`, and `explain` live in
`hedron_core.design_system`. `Hedron(theme=...)` accepts `str | Theme | DesignSystem | None`, but
always normalizes to the existing registered theme-name authority before lifespan composition.
There is no second app-state design authority or theme registry.

The `hedron.brand-palette/1` compiler accepts only 3/6-digit hex in v1, compiles coordinated light
and dark semantic sets together, validates locked foreground/background and focus pairs, and
records seed, inherited, generated, preset, override, and adjustment provenance. An unsafe or
unsatisfied result fails with remediation or uses a deterministic adjusted derivative and reports
it; it never silently publishes a failing pair. Compilation performs no network, filesystem,
request, platform-dependent color-engine, callback, or remote-asset work.

Finite design groups replace raw maps only on the beginner path:

| Group | Choices in 0.58 | Existing lowering target |
|---|---|---|
| Brand | 3/6-digit hex accent | `Theme.tokens`, `modes`, `palette` |
| Typography | system sans/serif/mono | semantic font/size/line tokens |
| Geometry | square/soft/rounded | `Theme.shape` |
| Density | compact/comfortable/spacious | current density vocabulary/markers |
| Elevation | flat/subtle/layered | current elevation/overlay tokens |
| Motion | standard/calm/none | motion tokens plus reduced-motion behavior |
| Navigation | compact/default/wide | validated `nav_width`/shell tokens |

Unknown groups and combinations reject. Custom fonts, arbitrary token maps, and values outside the
finite vocabulary remain explicit `Theme`/asset-policy work.

### Semantic style recipes and generated feature roles

Recipes capture repeated presentation intent without becoming a CSS language:

```python
design = DesignSystem.brand(name="acme", accent="#2f6fed").with_recipes(
    StyleRecipe.control(
        "primary_action",
        emphasis="primary",
        appearance="solid",
        size="md",
    ),
    StyleRecipe.surface(
        "data_surface",
        appearance="raised",
        density="compact",
        padding="md",
    ),
)

submit = design.apply("primary_action", Button("Save"))
```

Families are exactly control, surface, data, status, and content. A recipe is immutable, named,
family-scoped, serializable, and contains only catalogued semantic values for existing optional
component props whose default is `None`. Application occurs before render by cloning the same
component type; the original is unchanged, explicit non-`None` component values win, and an
incompatible family or unlisted field rejects. Inheritance is same-family, acyclic, and bounded to
four levels. Recipes add no wrapper DOM, runtime lookup, selector, class, CSS declaration, URL,
callback, authorization, semantic state, or destructive meaning.

The ten built-in recipes are `primary_action`, `secondary_action`, `destructive_action`,
`page_surface`, `form_surface`, `data_surface`, `dashboard_panel`, `dense_data`, `inline_status`,
and `metadata`. Generated screen/form/workspace/dashboard/task/auth/upload surfaces declare the
matching finite role. Those defaults remain weaker than explicit facade configuration,
`FeatureOverrides`, component props, application CSS, and a complete named-surface replacement.
Styling cannot add a route/effect, change authorization, infer state, or make an action destructive.

### Explicit `StyleScope`

`StyleScope` is a visible subtree boundary limited to theme, color mode, and density:

```python
StyleScope(
    report_table,
    theme="aurora",
    color_mode="dark",
    density="compact",
)
```

It lowers to one explicit `div` plus stable current markers and inherited theme variables. The
nearest explicit ancestor wins, with an explicit child marker stronger. Scope-wide recipe defaults,
raw variables, ambient context, DOM reordering, content hiding, and lifecycle JavaScript are
deferred because they would create hidden descendant mutation or specificity authority.

### Unified precedence

Strongest to weakest:

1. explicit component prop, explicit named-feature-surface replacement, or application-owned
   scoped CSS;
2. the explicitly applied component recipe;
3. nearest explicit scope theme/color-mode/density;
4. application `DesignSystem` default;
5. resolved existing `Theme`; and
6. first-party baseline CSS.

Equal-level conflicts reject unless an explicit replacement operation exists. Mapping/import order
and accidental selector specificity are never authorities. Feature explanation records the winning
source and the suppressed default.

### Inspect, preview, diff, check, and eject

`DesignSystem.explain()` returns canonical `hedron.design-system-plan/1`; CLI and Explorer consume
the same plan. Companion schemas are `hedron.design-system-diff/1`,
`hedron.design-system-preview/1`, and `hedron.design-system-source-map/1`. They contain canonical
logical IDs, inputs, resolved themes/groups/recipes, provenance, adjustments, assets,
compatibility, limitations, digests, and project-relative source maps—never request/user data,
secrets, callback representations, absolute paths, or runtime values.

Preview renders only the fixed versioned gallery with synthetic content. Diff is semantic across
inputs/tokens/groups/recipes/components/assets/emitted output, not a minified CSS diff. Check
combines theme, contrast, recipe, scope, style-contract, asset/CSP, budget, and zero-application-CSS
diagnostics. Static tooling does not invoke routes, loaders, components, callbacks, network, or
application data.

Ejection targets the whole design or one group, recipe, or component and writes public `Theme`
Python, explicit props/markers, public style-contract scoped CSS, manifests, source maps, and parity
tests. It is project-root-only, no-overwrite by default, budgeted, deterministic, and rejects path
traversal, symlink escape, hostile names, private selectors/markup, and captured runtime values.
Feature ejection explicitly selects either preserved recipe references or fully resolved explicit
props; both forms must preserve route/effect/security/accessibility/build and scenario parity.

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

The documentation learning path teaches one integrated concept per step:

1. built-in theme, screen, and static components;
2. refreshable view and typed form command;
3. optional generated brand when a distinct visual identity is needed;
4. workspace/dashboard/task plus built-in semantic roles;
5. a named recipe when presentation intent repeats;
6. inspect/preview the unified lowering;
7. override one feature surface or explicit style scope;
8. eject and compare explicit feature/`Theme`/prop/CSS code; and
9. production authorization, persistence, jobs, uploads, assets/CSP, and deployment.

### Starter-example adoption policy

At the 0.58 cut, every maintained documentation example identified as **starter**,
**beginner**, **quick start**, **golden path**, **minimal**, **first app**, **theming**, or generated
**scaffold** uses the highest applicable 0.58 feature and styling abstractions. This includes the
root and flagship README first-app examples, getting-started pages, beginner cookbook/recipe
entries, starter single-file examples, theme examples, scaffold snapshots, and package quick starts
that demonstrate an affected workflow or styling path.

The teaching order is normative:

1. show the applicable feature facade with a built-in theme first;
2. introduce `DesignSystem.brand` only when customization is relevant, then semantic recipes only
   when intent repeats;
3. show inspect/preview, an explicit scope/override, and the compiled/ejected equivalent afterward
   when they help understanding; and
4. link to existing feature primitives and advanced `Theme`/prop/style-contract/CSS APIs.

A document whose purpose is specifically to teach `Page`, `FormBody`, handles, regions,
`InteractionResult`, raw HTML, responses, `Theme`, component appearance props, style contracts,
scoped CSS, cascade/compiler internals, or host-native integration may use the explicit API, but
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
- portable `DesignSystem`/recipe/scope values live in `hedron-core`; FastAPI accepts them through
  `Hedron`, while Flask/Django/Jinja/elements consume compiled themes/markers only through their
  explicitly documented seams;
- Explorer styling preview remains development/secured, sim covers only a fixed declared gallery,
  and conformance owns schema/disposition fixtures rather than claiming a CSS renderer.

## Errors and diagnostics

Stage 0 reserves and locks diagnostic families without renumbering existing codes:

- screen metadata/return conflicts;
- form-boundary ambiguity and effect conflicts;
- feature surface naming/override/ejection conflicts;
- task scope/backend/status/result failures;
- dashboard filter/panel/fan-out/stale-request failures;
- auth configuration/session/result failures; and
- upload storage/result/policy composition failures;
- design/brand input, contrast/adjustment, and theme-normalization failures;
- recipe family/field/inheritance/collision and scope-marker failures; and
- style plan/preview/diff/ejection/CSP/asset/budget failures.

Diagnostics identify the high-level intent and the lowered primitive that failed, include a
concrete advanced spelling or override when useful, and remain redacted under 0.56. Exceptions from
application callbacks preserve their existing security/HTTP behavior and are not broadly converted
into facade-specific success states.

## Package ownership

| Package/module | 0.58 responsibility |
|---|---|
| `hedron-core` | Portable feature/design schemas, `DesignSystem`, recipes, `StyleScope`, brand compiler; no FastAPI imports or second registry/cascade |
| `hedron.app` | `screen`, `ScreenHandle`, `form_command`, page/form lowering |
| `hedron.features` | Read-only explanation, stable named-surface/source-map helpers, ejection parity |
| `hedron.jobs` | `TaskFlow`, task tickets, scoped status/cancel/result composition |
| `hedron.dashboard` | Typed filters, request loader boundary, named panel feature provider |
| `hedron.auth` | `SessionAuthFlow` over existing session/security contracts |
| `hedron.files` | `UploadFlow` over existing upload/download/security contracts |
| `hedron-data` | `DataWorkspace.with_screen`, complete workspace composition and overrides |
| CLI / Explorer | Explain, graph, check, preview, diff, and eject the same feature/design plans |
| adapters/conformance/sim | Explicit capability disposition and portable evidence only |

No new distribution is authorized by this phase.

## Delivery workstreams

| Workstream | Deliverable | Depends on |
|---|---|---|
| W0 | Unified contracts, inventories, schemas, precedence, diagnostics, budgets | Published/Verified 0.57 |
| W1 | Shared explanation/named-surface/design-plan/provenance/source-map substrate | W0; existing catalogs/build manifests |
| W2 | `screen`, `ScreenHandle`, shell/navigation composition | W0; 0.54/0.57 presentation |
| W3 | `form_command` and effect-conflict rules | W0; 0.43/0.44 handles/types |
| W4 | `DataWorkspace.with_screen` and CRUD scaffold | W1–W3 |
| W5 | `TaskFlow`, scope, polling, cancel/result surfaces | W1, W3; jobs/security |
| W6 | `DashboardWorkspace`, filters/load/panels/history | W1–W3; interaction graph |
| W7 | `SessionAuthFlow` | W1–W3; 0.56 security |
| W8 | `UploadFlow` | W1, W3, W5; 0.55/0.56 uploads |
| W9 | `DesignSystem`, brand compiler, typed groups, `Theme` bridge | W0; 0.57 styling authorities |
| W10 | Semantic recipes, generated-feature roles, `StyleScope`, precedence | W9; stable component props |
| W11 | Unified CLI/Explorer explain, preview, diff, check, and eject | W1, W9–W10 |
| W12 | Feature↔styling plan, precedence, role, and ejection integration | W2–W11 |
| W13 | Four scaffolds, both starter inventories, one learning path | W11–W12 |
| W14 | Adapter/package/conformance/sim dispositions and scenarios | W2–W13 |
| W15 | Security/CSP, a11y, visual/browser, and performance evidence | all implementation work |
| W16 | Explicit API regression and unified 0.57 upgrade evidence | W2–W15 |
| W17 | Packaging, documentation truth, and release rehearsal | W16 |

W2/W3 are the minimum feature slice and W9 is the minimum styling slice. W4–W8 may develop in
parallel after W1; W12 is mandatory before a generated feature claims styling support. A facade
that cannot satisfy its security, native fallback, explanation, styling integration, and ejection
requirements moves through an explicit decision revision rather than weakening the common contract.

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
| `BRAND-058` | Deterministic coordinated light/dark brand output, locked contrast, and disclosed adjustment |
| `THEME-058` | Typed groups, `Theme` round trip, constructor normalization, build parity, and no second registry |
| `RECIPE-058` | Five families, ten feature roles, clone-before-render, exact precedence, and behavior neutrality |
| `SCOPE-058` | Explicit theme/mode/density boundaries and exact marker/output parity |
| `EXPLAIN-058` | Static redacted feature/design explain/graph/preview/diff/check plus safe unified ejection/source-map parity |
| `VISUAL-058` | Fixed gallery across three engines, modes, viewports, direction, zoom, content, and reviewed deltas |
| `A11Y-058` | Semantics, contrast, keyboard, announcements, no-JS, zoom, motion/color, and generated-design evidence |
| `SECURITY-058` | Feature trust boundaries plus styling input/CSP/asset/tooling/ejection/exposure adversarial evidence |
| `ADAPTER-058` | FastAPI Supported claims plus explicit Flask/Django/conformance/sim dispositions with no false parity |
| `REGRESS-058` | Existing feature and styling APIs plus 0.43–0.57 fixtures remain compatible |
| `DX-058` | Four runnable scaffolds; every inventoried starter uses the highest applicable feature and styling abstractions; labeled explicit equivalents and measured learning/ejection outcomes |
| `PKG-058` | Wheels, optional-dependency isolation, docs, exports, inventories, upgrade fixtures, metadata, and release rehearsal |

The D-102/D-105 packet provides the machine-readable symbol/surface/recipe inventories,
lowering/precedence/host dispositions, feature/design schemas, security requirements, scaffolds,
starter migrations, budgets, tracking, unified upgrade fixtures, and exact twenty-gate commands.

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
- CSS/selector/URL breakout through brand/recipe/scope names or values;
- implicit remote fonts/images, network during compile/tooling, inline-style requirements, private
  selectors/markup, source-map path disclosure, or runtime data capture;
- styling that changes routes, effects, authorization, destructive meaning, DOM/reading order,
  accessible names, authoritative values, interaction, or state; and
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
- every generated light/dark pair meets the locked contrast/focus targets or emits a recorded
  deterministic adjustment/failure; state is never communicated by color or motion alone;
- recipe/scope/design changes preserve DOM order, accessible names, focus, semantics, forced-color
  behavior, and static equivalents; and
- native HTTP paths, failed-upgrade behavior, 200% zoom, narrow viewports, reduced motion, forced
  colors, RTL, long content, and fragment replacement.

Generated code and explanations use plain language suitable for a beginner and identify advanced
terms only when they solve the current problem.

## Performance implications

Facades add registration-time compilation and read-only metadata, not an application request or
styling runtime. Equivalent explicit and facade-generated paths have the same rendering,
interaction, CSS-build, and asset authorities. Stage 0 sets representative budgets for:

- import and registration overhead with no optional features installed;
- descriptor/explanation size and static inspection time;
- route/surface/form-field/panel counts;
- dashboard load and bounded fan-out;
- polling amplification and terminal shutdown;
- ejection time/output size;
- brand compilation, design plan/diff/static-preview time and output size;
- design/recipe/scope count and inheritance limits, CSS/build ratios, and zero unused import/asset
  delta; and
- generated versus explicit render/response/markup/CSS parity.

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
- Existing `Theme`, built-in theme, `Theme.extend`, `compile_palette`, registration, appearance
  props, markers, `StyleSymbols`, component styles, style contracts, compiler/cascade/assets/CSP,
  theme checks, and zero-application-CSS behavior remain accepted and authoritative.
- No application is auto-opted into `DesignSystem`, a recipe, or `StyleScope`; a no-choice
  `DesignSystem.from_theme(...).to_theme()` round trip has no semantic or emitted-CSS drift.
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

## Resolved questions (D-105)

1. **Separate 0.59 styling phase?** No. D-103/D-104 and RFC-0086 are superseded; all styling scope,
   artifacts, workstreams, starter adoption, and gates are integrated into 0.58.
2. **Styling authority?** Existing `Theme`, props/markers, style contracts, CSS compiler/cascade,
   assets, and CSP; never a second registry, cascade, compiler, or runtime injector.
3. **Beginner custom look?** `DesignSystem.brand` with one 3/6-digit hex accent and finite typed
   groups; coordinated light/dark output uses `hedron.brand-palette/1` and records adjustments.
4. **App seam?** `Hedron(theme: str | Theme | DesignSystem | None)` normalizes to the existing
   registered theme name before lifespan composition.
5. **Recipe application?** Five finite families and ten built-in feature roles; clone before render,
   fill eligible `None` defaults only, explicit values and named-surface overrides win.
6. **Local defaults?** `StyleScope` only for explicit theme/color-mode/density boundaries. Scope
   recipe defaults and field/layout recipe families remain deferred.
7. **Inspection schemas?** `hedron.design-system-plan/1`, diff/preview/source-map `/1`, linked to
   feature explanations by stable logical IDs and common provenance.
8. **Unified ejection?** Feature ejection selects recipe-preserving or fully resolved output; style
   ejection targets a whole design/group/recipe/component with shared safety and parity rules.
9. **Starter policy?** Every starter example uses the highest applicable 0.58 feature and styling
   abstractions. Advanced primitives appear afterward and are clearly labeled.
10. **Release structure?** One RFC, implementation plan, acceptance checklist, tracking file,
    upgrade corpus, and twenty-gate release file; no 0.59 predecessor audit or second cut.

## Acceptance criteria

Phase 0.58 may cut only when:

- Published and Verified in-tree `v0.57.0` is the frozen upgrade source;
- D-102/D-105 resolve every open question and lock the unified finite inventories;
- every feature and styling facade lowers to existing public authorities with catalog/descriptor/
  plan/build/explanation parity;
- all generated surfaces are named, inspectable, replaceable, testable, and safely ejectable;
- authorization, persistence, transactions, tenancy, durable workers, storage, scanning,
  destructive meaning, and external exposure remain explicit;
- coordinated light/dark compilation, recipe/feature-role precedence, explicit scopes, and combined
  ejection preserve behavior, accessibility, security, and build authority;
- native HTTP, HTMX, failed-upgrade, visual, accessibility, strict-CSP, security,
  adapter-disposition, performance, and upgrade evidence pass;
- `minimal`, `crud`, `dashboard`, and `task` scaffolds are runnable from clean wheels and teach the
  intended authoring ladder;
- every inventoried starter/beginner/quick-start/golden-path/minimal/first-app/theming/scaffold
  example uses the highest applicable 0.58 feature and styling abstractions, with lower-level
  spellings confined to clearly labeled advanced/explicit/under-the-hood material;
- existing explicit APIs and 0.43–0.57 fixtures remain compatible;
- all twenty `*-058` release gates are Verified with zero Deferred; and
- package/version/release metadata truthfully identifies new APIs as Beta and does not schedule
  1.0.
