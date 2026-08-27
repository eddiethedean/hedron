# Hedron 1.0 interface audit informed by Edron

**Status:** Planning input  
**Target:** Hedron `v1.0.0` through the `v0.67.0` migration bridge  
**Governing RFC:** [RFC-0096](../rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md) / D-115 / D-116  
**Component engine dispositions:**
[COMPONENT_ENGINE_DISPOSITIONS_067_1_0](COMPONENT_ENGINE_DISPOSITIONS_067_1_0.md)  
**Compared Edron scope:** implemented `0.1`–`0.5` and planned `0.6`–`0.9`

## Outcome

Hedron 1.0 should adopt Edron's discipline, not its facade. Edron's strongest ideas are explicit
ownership, request-bounded execution, named binding, exact lowering, structured diagnostics, and a
small task-oriented vocabulary. Its weakest fit for native Hedron is the Streamlit-shaped page
class: an implicit current output buffer, many display methods returning `None`, automatic page
composition, and convenience wrappers over package capabilities. Those choices simplify a first
example but obscure the component tree, return types, HTTP boundaries, and package ownership that
define normal Hedron work.

Hedron therefore keeps **function handlers as the only canonical page/view/action authoring
style**. Classes remain appropriate for Pydantic models, reusable components, policies, services,
feature bundles, and other values—not as a second route-authoring DSL.

| Developer task | One canonical 1.0 path |
|---|---|
| Create an application | `Hedron(...)` |
| Register a navigable document | `@app.page(...)` function returning exactly one presentation tree; the decorator owns the document shell |
| Register a safe replaceable read | `@app.view(...)` function returning exactly one presentation tree and producing a view handle |
| Register an unsafe operation | `@app.action(...)` function returning one role-valid `Outcome` and producing an action handle |
| Describe browser behavior | one typed `Interaction` with a closed local/request/combined effect discriminant |
| Return an operation result | one role-indexed closed `Outcome` family |
| Compose presentation | explicit returned nodes from the typed `hedron.ui` module |
| Include a reusable capability | `app.include(...)` with an owning feature/provider |
| Inject request dependencies | standard typed FastAPI/Hedron dependency declarations |
| Use an optional domain capability | import it from its owning `hedron-*` package |
| Drop to raw HTTP | normal FastAPI routing, clearly labeled advanced |

These names are the recommended 0.67 freeze target. They may change before that freeze only if the
replacement still leaves exactly one path for each task.

## The one-clear-way rule

Hedron 1.0 has one documented, scaffolded, generated, and stable path for one task at one
abstraction level. A second spelling is admitted only when it performs different work, not merely
because it is older, shorter, more explicit, or lower level.

This has mechanical consequences:

1. API review starts from a task-to-interface graph, not an alphabetical export list.
2. Aliases never enter the 1.0 stable facade. Renames finish at the major boundary.
3. An escape hatch must name the capability the canonical path cannot express. Otherwise it is a
   duplicate and is removed.
4. Examples, scaffolds, type stubs, completion, Explorer, diagnostics, and migration output use the
   same spelling.
5. Convenience methods on handles are recipes, not alternate registration or response systems.
6. Optional-package features stay in their owning package rather than being copied into the root.

The rule does not collapse unlike tasks. A page, safe view, unsafe action, data workspace, and raw
JSON endpoint have different authority and remain different concepts.

## Recommended native authoring model

### Application and registration

Keep `Hedron` rather than copy Edron's `App`. It identifies the framework and remains the exact
FastAPI application. Do not retain both names as root aliases.

Consolidate Hedron route authoring to three function roles:

| Role | Contract | Merges or replaces |
|---|---|---|
| `@app.page` | Safe navigable document; owns title/layout/shell/head/browser metadata; function returns one presentation tree and produces a `PageHandle` | `screen` and the common `page` path; direct `Page` handler results move to Advanced rendering |
| `@app.view` | Safe `GET` renderer returning one presentation tree with one owned host/target and bound identity; produces a `ViewHandle` | `refreshable`, `fragment`, common GET `component`, and manual region setup |
| `@app.action` | Unsafe typed operation, `POST` by default, CSRF/fallback; returns one role-valid `Outcome` and produces an `ActionHandle` | `command`, `form_command`, common `action`, and unsafe `component` |

`HedronRouter` and normal FastAPI routes remain advanced integration surfaces for JSON APIs,
custom responses, unusual methods, and host composition. They are not a fourth Hedron interaction
style. During 0.67 the canonical signatures coexist with warning-emitting compatibility paths;
1.0 contains no dynamic alias that recreates the removed spellings.

### Composition and imports

Keep Hedron's explicit return-tree model. A canonical page or view handler returns exactly one
presentation tree; sibling composition uses the explicit fragment/container node. An action returns
exactly one role-valid `Outcome`. Direct full-`Page` construction, arbitrary response objects, and
raw HTTP remain Advanced surfaces. Hedron does not adopt a request-local output buffer, implicit
current container, display call returning `None`, or module-global render context.

Use a real, statically typed `hedron.ui` module for first-party layout, content, feedback, controls,
and document components. Keep `hedron.html` for semantic HTML. Root exports shrink to the
application spine and a deliberately small set of cross-cutting types. Data, charts, maps, files,
jobs, auth, and adapters remain in their owning packages/modules.

### Views, actions, and outcomes

A view handle owns its route, host, target authorization, binding, fallback, loading/error/empty
presentation, and refresh request. There is no separate beginner `Region`, `FragmentRegion`,
`ComponentRef`, or selector-allowlist workflow. Custom targeting is an option on the same view.

An action handle owns its method, CSRF policy, typed input, authorization dependencies, fallback,
idempotency/concurrency policy, and controls. Exactly one Pydantic model may define a generated
form; explicit controls resolve ambiguity. An action never returns a Boolean and is never invoked
during page rendering.

Action handlers return one role-indexed closed `Outcome` family. It covers success/no-content, refresh of exact
view handles, a bounded authoritative patch, safe local redirect, accepted job,
validation/conflict, and authorized download. It replaces competing beginner spellings based on
`InteractionResult`, `Refresh`, `RefreshIntent`, `PatchSet`, `swap`, `swap_oob`, `refresh`,
`patches`, and HTMX-specific redirects. Low-level response objects remain valid for advanced raw
HTTP routes.

### HTMX and Alpine

One `Interaction` describes the initiating event and exactly one closed effect variant: local,
request, or combined. Target/swap, pending/error/success presentation, concurrency, fallback,
accessibility behavior, state reconciliation, and trace identity are valid only where admitted by
that discriminant. Its compiler emits Alpine only, HTMX only, or coordinated Alpine plus HTMX;
construction and static checks reject illegal cross-lane combinations.

Controls receive this value through one property. Handles bind authoritative request facts into
it; local effects bind only browser-local state. Components and interactions contribute their exact
browser feature demands, so users do not repeat plugin lists on pages. Direct `hx-*`, `x-*`, raw
expressions, and module hooks remain reviewed Advanced markup, carry explicit requirements, and do
not appear in ordinary guides.

The browser engine underneath a component follows D-116 rather than becoming another public
authoring choice. Ordinary semantic widgets use native HTML plus Alpine; specialist browser
subsystems may retain or adopt the existing Web Component platform. In both cases the developer
uses the same task-oriented Python component name, and the engine boundary is inspectable lowering.

### State and dependencies

Adopt Edron's state-owner matrix as a native contract: URL for safe shareable filters, typed body
for one submission, typed session for bounded continuity, cache for recomputable values, job
backend for operation state, application storage for domain truth, and Alpine for disposable
presentation. Every transfer between owners is explicit.

Keep normal typed FastAPI/Hedron dependency injection instead of Edron's page-field dependency
descriptor. Resource registration may add lifecycle metadata, but it must lower to the existing
connection/lifespan authority rather than create another container.

## Edron feature and plan dispositions

### Core authoring and interaction (`0.1`)

| Edron idea | Hedron 1.0 disposition | Reason |
|---|---|---|
| Explicit ASGI application | **Adopt principle**; keep `Hedron` | Exact FastAPI identity and deployment remain visible. |
| Class-only `Page.render()` | **Reject** | Function handlers and returned trees are clearer and idiomatic. |
| Fresh page instance per request | **Adopt lifecycle invariant** | No persistent page object or cross-request instance state. |
| Implicit output/current container | **Reject** | Hides tree structure, return types, concurrency, and reuse. |
| Display/input methods on `self` | **Reject as native facade** | They duplicate components and make one class unbounded. |
| `include()` for native nodes | **Adapt** | Nodes compose directly; `app.include(...)` includes features. |
| One page decorator | **Adopt** | Merge native `screen` and common `page`. |
| Fragment/action descriptors | **Adopt semantics, rename** | Canonical native roles are `view` and `action` handles. |
| Named `.bind(...)`, no callback bags | **Adopt** | Typed, inspectable, deterministic, and safer. |
| Coherent safe GET filters | **Adopt** | URL remains canonical and groups submit complete typed state. |
| Pydantic form generation | **Adopt within `action`** | Do not retain separate form-registration paths. |
| Closed outcomes and exact refresh targets | **Adopt and consolidate** | One `Outcome` replaces response/update overlap. |
| Page-field dependency descriptor | **Do not copy** | Typed native/FastAPI DI already owns the lifecycle. |
| Cache convenience | **Package/module-native** | Keep one bounded cache API, not app/page/root duplicates. |
| `JobFlow` | **Adapt to native `TaskFlow`** | Preserve backend, scope, fallback, and durability truth. |
| Table/chart/map display methods | **Reject** | Use typed components from their owning packages. |
| Lazy optional capability diagnostics | **Adopt** | Missing, incompatible, and broken remain distinct. |
| Simple theme and finite variants | **Adopt progressive ladder** | One native theme registry, typed recipes, then registered CSS. |
| Native escape property | **Not applicable** | Hedron is already native; inspection exposes lowering. |

### Authoring and tooling (`0.2`)

| Edron idea | Hedron 1.0 disposition | Reason |
|---|---|---|
| AST-only `check` | **Adopt and extend** | `hedron check --target 1.0` never imports untrusted source. |
| Text/JSON/SARIF diagnostics | **Adopt** | One schema supports editors, CI, and migration. |
| Redacted source locations | **Adopt** | Trace declarations without exposing values. |
| Trusted `explain` and source map | **Adopt** | Show routes, handles, interactions, assets, and lowering. |
| `doctor` without installation | **Adopt** | Report missing/incompatible/broken capabilities and ops facts. |
| Teaching scaffolds | **Adopt** | Generate only canonical vocabulary and explicit ownership. |
| Class/function page aliases | **Reject** | Functions are the sole handler style; aliases violate the rule. |
| Explicit descriptor inheritance | **Defer** | Composition is clearer than inherited registered surfaces. |

### Data workspace (`0.3`)

| Edron idea | Hedron 1.0 disposition | Reason |
|---|---|---|
| Explicit source/workspace | **Adopt in `hedron-data`** | Clear query, edit, persistence, and transaction ownership. |
| Allowlisted paging/filter/projection | **Adopt** | Prevent unbounded reads and secret leakage. |
| Bounded current-page selection/export | **Adopt** | Honest authorization and resource bounds. |
| Deny-by-default edit policy | **Adopt** | Writes, validation, concurrency, and audit stay explicit. |
| Page data/editor convenience methods | **Reject** | Include the provider and render its owning typed component. |
| Dataframe/SQLAlchemy adapters | **Package-native** | Direct optional install and application-owned transactions. |
| Automatic ORM/repository discovery | **Reject** | It obscures persistence and authorization boundaries. |

### Visualization, maps, media, and linked data (`0.4`)

| Edron idea | Hedron 1.0 disposition | Reason |
|---|---|---|
| One first-party chart/map path | **Adopt per owning package** | Avoid multiple constructors for one visualization. |
| Typed selection links | **Adopt through `Interaction`** | A browser selection invokes only registered boundaries. |
| Accessible table/text alternative | **Adopt as invariant** | Semantic fallback and keyboard behavior remain required. |
| Authorized export/media references | **Adopt** | Never accept arbitrary paths or client identity as authority. |
| No client runtime | **Supersede carefully** | Alpine enhances locally without changing server authority. |
| Library-specific page methods | **Reject** | Owning adapters expose one component interface. |

### Resources, state, jobs, and operations (`0.5`)

| Edron idea | Hedron 1.0 disposition | Reason |
|---|---|---|
| Explicit resource lifetime and secret refs | **Adopt** | Inspectable lifecycle without resolving secrets. |
| Typed state-owner matrix | **Adopt as contract** | Prevent accidental ownership changes. |
| Bounded scoped cache | **Adopt package-native** | Cache is derived performance state, never truth. |
| Job flow over explicit backend/scope | **Adopt native `TaskFlow`** | Keep polling fallback and production durability honest. |
| Polling canonical; SSE/WS observers | **Adopt** | Live transport never becomes job authority. |
| Operations diagnostics | **Adopt into inspect/doctor** | One report covers runtime and production facts. |
| App/page wrappers for all capabilities | **Reject** | They duplicate owners and make the app object unbounded. |

### Reusable composition (`0.6`)

| Edron idea | Hedron 1.0 disposition | Reason |
|---|---|---|
| Atomic feature packages | **Adopt as feature/provider inclusion** | One provenance, deduplication, and rollback boundary. |
| Typed navigation/shared layout | **Adopt in `hedron.ui`** | Compose exact page handles and explicit shell slots. |
| Promotion of satellite capabilities | **Adapt** | Curate docs, not root re-exports; ownership stays visible. |
| Mixed facade/native ejection | **Adopt as inspection/export tooling** | Expose exact native projection. |
| Plugin scanning/parallel registry | **Reject** | Application catalog and package metadata remain authoritative. |

### Migration and adoption (`0.7`)

| Edron idea | Hedron 1.0 disposition | Reason |
|---|---|---|
| Conservative AST analysis | **Adopt** | Never execute source during migration. |
| Source-mapped scaffolds with findings | **Adopt** | Generated code is reviewable; uncertainty is explicit. |
| State/interaction/style/dependency reports | **Adopt** | Organize migration by task and authority. |
| Accepted codemods | **Adopt** | Deterministic only, with explicit output/apply choice. |
| Runtime behavior emulation | **Reject** | Do not preserve contradictory 0.67 APIs through magic. |

### Deployment and host integration (`0.8`)

| Edron idea | Hedron 1.0 disposition | Reason |
|---|---|---|
| Reviewed ASGI profiles/diagnostics | **Adopt** | Proxy, assets, secrets, workers, and observability stay explicit. |
| SBOM/provenance/rollback/air gap | **Adopt** | Required for Alpine and production artifacts. |
| Host integrations require lifecycle/HTTP parity | **Adopt** | A facade cannot weaken security, state, fallback, or swaps. |
| Superficial Flask/Django parity | **Reject** | State exact supported host capabilities instead. |

### Long-lived consolidation (`0.9`)

| Edron idea | Hedron 1.0 disposition | Reason |
|---|---|---|
| Evidence-backed stability promotion | **Adopt** | The version does not make every feature stable. |
| Finish deprecations without aliases | **Adopt as 1.0 gate** | Directly enforces one clear way. |
| Frozen overhead budgets | **Adopt** | Measure imports, compile, request, assets, and diagnostics. |
| Usage-based vocabulary reduction | **Adopt before freeze** | Evidence resolves ambiguity; aliases still end at 1.0. |

## Ideas intentionally left in Edron

These may suit Edron's beginner audience but would oversimplify native Hedron:

- a page class as the universal authoring context;
- implicit output collection and current-container context managers;
- `self.text`, `self.table`, `self.line_chart`, `self.map`, and similar display methods;
- input controls that look local while actually binding request/query state;
- automatic visible headings and layout decisions from page metadata;
- inferred owning-page fallbacks when route ownership is ambiguous;
- broad base-install or root-facade promotion of optional packages;
- convenience aliases such as `subheader`, `page_function`, or multiple chart spellings;
- generic object writers, arbitrary HTML shortcuts, style dictionaries, or callback bags;
- reruns, global session dictionaries, Boolean mutation buttons, or persistent pages; and
- hiding workers, transactions, authorization, durability, or host differences.

## 0.67 migration bridge and warning contract

Every canonical 1.0 spelling ships in 0.67. “Public 0.67” includes every documented, exported,
generated, configured, CLI, HDJ, and browser-markup contract, including beta/experimental
contracts; private underscore/internal details are excluded. Every executable public path accepted for removal
emits `HedronFutureWarning` once per source callsite in development, tests, and trusted CLI
inspection. The warning is visible by default, machine-readable, and contains:

- stable diagnostic code;
- old symbol or calling form;
- one canonical replacement, or a removal-without-replacement reason;
- first-warning version (`0.67`), removal version (`1.0`), and owning package;
- documentation/migration anchor; and
- automatic, review-required, or manual migration status.

Static-only configuration, HDJ, template attributes, CLI flags, manifests, imports not executed by
tests, and browser markup receive the same warning record from `hedron check --target 1.0`. A
changelog entry is insufficient, and a Python `DeprecationWarning` hidden by the default filter
does not satisfy the requirement. Findings carry `complete`, `partial`, or `unknown` confidence;
dynamic imports, reflection, generated keyword bags, or opaque templates may require manual review
and cannot be reported as a clean migration.

| 0.67 paths | Proposed 1.0 path |
|---|---|
| `screen`, common `page` | `page` |
| `refreshable`, `fragment`, GET `component`, manual region recipe | `view` |
| `form_command`, `command`, common `action`, unsafe `component` | `action` |
| interaction result, refresh/patch/swap helpers and builders | `Outcome` |
| HTMX attrs/helpers plus Alpine directives/helpers | `Interaction` |
| `include_feature`, flow-specific inclusion | `include` |
| root satellite re-exports | owning package/module import |

The generated inventory must decide every symbol and artifact. This table is not permission to
remove unlisted paths silently.

## Evidence and freeze gates

1. Complete fixtures cover pages, safe filters, CRUD, jobs, data editing, visualization, media,
   auth, feature bundles, optional adapters, and local-only Alpine.
2. Each fixture uses one route, interaction, outcome, composition, and inclusion spelling;
   duplicate concepts fail a docs/API lint.
3. The same 1.0 fixture corpus imports, type-checks, and executes on 0.67 and 1.0 under the exact
   compatibility BOM.
4. Every removed executable path emits the structured 0.67 warning; every non-executed use is
   found by the target-1.0 checker.
5. HTMX, no-JavaScript, Alpine-local, combined, history, OOB, morph, late-response, validation,
   conflict, and fallback scenarios preserve the authority model.
6. Root exports, constructors, decorators, outcomes, CLI/config, markup, and artifacts match the
   frozen manifests exactly.
7. User testing can identify the correct interface from the task alone without a “which API?”
   decision page.

## Required deliverables

- machine-readable task-to-interface and removal inventories;
- the accepted `FREEZE-067` lock and exact Python/dependency/adapter/satellite/browser/tooling BOM;
- warning registry and executable warning coverage report;
- canonical 0.67/1.0 type stubs and cross-version fixture suite;
- target-1.0 check and conservative migration tooling;
- one canonical quickstart and task-oriented migration guide;
- interaction compiler/lifecycle architecture and Alpine/HTMX browser matrix;
- root-export and owning-package import policy;
- source-map/inspect/doctor schemas; and
- accepted freeze review before the 1.0 release candidate.
