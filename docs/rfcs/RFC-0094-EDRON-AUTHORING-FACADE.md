# RFC-0094: Edron batteries-included Pythonic authoring facade

**Status:** Draft<br>
**Proposed target:** Edron `0.1.0`; compatible Hedron train and release phase unassigned<br>
**Roadmap:** [Edron `0.x` release roadmap](../EDRON_ROADMAP.md)<br>
**Design fixtures:** [Edron golden applications](../implementation/EDRON_GOLDEN_APPS.md)<br>
**Public API contract:** [Edron 0.1 public API](../api/EDRON.md)<br>
**State and interaction contract:** [Edron 0.1 state and interaction](../api/EDRON_STATE_INTERACTION.md)<br>
**Packaging contract:** [Edron 0.1 packaging](../api/EDRON_PACKAGING.md)<br>
**Capability inventories:** [Edron 0.1 capability inventories](../implementation/EDRON_CAPABILITY_INVENTORIES.md)<br>
**Implementation specification:** [Edron 0.1 implementation](../implementation/EDRON_001.md)<br>
**Acceptance packet:** [Edron 0.1 acceptance](../acceptance/EDRON_001.md)<br>
**Extends:** RFC-0012, RFC-0014, RFC-0018, RFC-0023, RFC-0024, RFC-0026, RFC-0070,
RFC-0071, RFC-0072, RFC-0073, RFC-0084, RFC-0085, RFC-0087, RFC-0089, RFC-0090,
RFC-0091, and RFC-0092<br>
**Related:** RFC-0061 (Streamlit migration assistant)

## Summary

This RFC proposes **Edron**, a separate `edron` Python distribution that provides a
batteries-included, class-oriented authoring facade over Hedron. Edron is intended for Python and
data developers who want to build server-rendered applications without first learning route,
endpoint, HTMX target, form-binding, or response mechanics.

Edron borrows useful Streamlit vocabulary—such as `sidebar`, `columns`, `metric`, `selectbox`,
`dataframe`, and chart names—but does not reproduce Streamlit's module-global API, whole-script
rerun model, implicit widget execution, or undifferentiated `session_state`. The conventional import
is:

```python
import edron as ed
```

The primary authoring unit is a request-scoped `ed.Page` class:

```python
import edron as ed

app = ed.App(title="Sales")


@app.page("/", title="Sales dashboard")
class SalesPage(ed.Page):
    def render(self) -> None:
        region = self.sidebar.selectbox(
            "Region",
            ("All", "North", "South"),
            name="region",
            updates=self.results,
        )
        self.metric("Selected region", region)
        self.results(region=region)

    @ed.fragment
    def results(self, region: str) -> None:
        rows = load_sales(region)
        self.line_chart(
            rows,
            x="month",
            y="revenue",
            title="Monthly revenue",
            description="Revenue for the selected region.",
        )
        self.dataframe(rows, name="sales")
```

At application startup, Edron compiles this class metadata into ordinary Hedron pages, fragment
handles, action handles, typed bindings, registry entries, components, policies, and assets. During
a request, Edron collects output in a bounded request-local authoring buffer and lowers it to
Hedron `NodeLike` values. Hedron remains the only renderer, route authority, interaction registry,
security authority, and HTMX runtime. “Transpile” in Edron documentation means this inspectable
startup/request lowering; it does not mean source-to-source code generation or a second runtime.

Edron and Hedron are deliberately interoperable. Public Hedron renderables and handles may be used
directly in Edron applications. Every Edron-generated surface has exactly one underlying native
Hedron descriptor, which can be inspected and composed through public APIs. Native Hedron routes
and Edron pages may coexist on the same application and registry.

`pip install edron` includes the maintained first-party data, table, chart, map, Markdown, and
server capabilities expected by the beginner vocabulary. Third-party libraries remain optional.
Installing either the dependency directly or the matching Edron extra activates the same adapter:

```bash
pip install edron "plotly>=5.18,<7"
pip install "edron[plotly]"
```

The extra is only an installation shortcut. Optional methods remain importable and fail at the
call site with an exact direct-install command, shortcut command, and compatibility explanation.

Styling follows the same progressive approach. A reviewed built-in theme is one string, a branded
theme is one small typed value, repeated visual intent is a named recipe, local refinement uses
finite semantic component options, and full product-specific expression uses ordinary registered
CSS. Every lane compiles through Hedron's existing theme, token, recipe, scope, component hook,
asset, cascade, CSP, and diagnostics authority.

## Motivation and background

Hedron already has strong native primitives for semantic components, pages, forms, typed request
binding, refreshable views, commands, effects, jobs, HTMX, progressive enhancement, accessibility,
security, and inspection. Those primitives are intentionally explicit. A developer building a
small dashboard or internal tool can nevertheless encounter several full-stack concepts before
showing the first domain value.

Streamlit demonstrates the value of a compact Python vocabulary and immediate composition. Some of
its ease, however, comes from semantics that do not transfer cleanly to a server-authoritative,
multi-request application: module-global rendering context, top-to-bottom reruns, widgets that both
render and control execution, mutation under `if button`, and one state dictionary spanning several
lifetimes. Copying those semantics would hide rather than remove complexity and would weaken
Hedron's ordinary HTTP and HTMX model.

Edron therefore has a different objective: make the common path small and familiar while keeping
request boundaries, mutations, state ownership, and native Hedron capabilities coherent. It should
feel Pythonic to read and test, even where that means departing from Streamlit syntax.

The repository already contains much of the necessary foundation:

- RFC-0070 provides refreshable views, commands, native handles, generated routes, targets, and
  typed updates;
- RFC-0071 and RFC-0072 provide type-driven request, form, outcome, and ecosystem contracts;
- existing class-handler compilers create a fresh instance per endpoint and retain inspected
  signatures without `self`;
- RFC-0085 establishes inspectable lowering without a second framework authority;
- RFC-0090 and RFC-0091 define the server-first interaction and HTMX direction; and
- `hedron-data`, `hedron-charts`, and `hedron-maps` provide first-party feature depth that Edron can
  aggregate rather than recreate.

Edron is also a design customer for Hedron. When a golden application exposes a reusable missing
primitive, this RFC permits planned work in Hedron rather than forcing an Edron-only imitation.

## Goals

1. Provide one explicit `ed.App`, one conventional `ed` import, and one primary class-based page
   model for ordinary applications.
2. Retain useful Streamlit vocabulary where its meaning fits Hedron, while choosing explicit,
   typed Python interfaces for actions, state, dependencies, and reuse.
3. Hide routine route, target, CSRF-field, HTMX-attribute, response, and asset mechanics without
   hiding their inspectable consequences.
4. Preserve all public Hedron rendering and HTMX power through direct composition and native
   escape hatches.
5. Make request lifetimes, safe reads, unsafe mutations, durable state, and dependency boundaries
   understandable from the source.
6. Make first-party tables, charts, maps, Markdown, and the development server available after a
   normal `pip install edron`.
7. Make third-party capability activation depend on the actual compatible dependency, not on how
   it was installed.
8. Produce deterministic explanations, diagnostics, source maps, type information, and tests for
   every generated surface.
9. Add reusable missing foundations to Hedron first, with one-way dependency direction from Edron
   to Hedron.
10. Make polished, responsive, accessible styling simple for beginners without limiting advanced
    authors or creating CSS-in-Python.

## Non-goals

- Drop-in source or behavioral compatibility with Streamlit.
- Supporting `import edron as st` as a documented convention.
- A whole-script rerun engine, global mutable rendering context, signal system, virtual DOM,
  hydration layer, SPA router, or mandatory client runtime.
- A second renderer, route registry, interaction registry, component hierarchy, state store, job
  queue, security policy, or dependency solver.
- Inferring authorization, tenancy, transactions, persistence, idempotency, or destructive meaning
  from labels, method names, or Python control flow.
- Re-exporting every Hedron symbol from the `edron` root namespace.
- Physically vendoring first-party packages into one source tree or obscuring their independent
  versions and licenses.
- A second theme registry, styling runtime, CSS-in-Python property dictionary, utility-class DSL,
  runtime stylesheet injection, or private-selector compatibility promise.
- Automatically installing dependencies at runtime or providing an unbounded `edron[all]` extra.
- Making Flask, Django, notebooks, Explorer, authentication providers, databases, or worker
  backends required dependencies of Edron `0.1`.
- Replacing the separate reviewable Streamlit migration work in RFC-0061.

## Proposed design

### 1. Distribution and authority boundaries

`edron` is a new top-level distribution and import package. Its required dependency set includes
compatible releases of:

- `hedron` and its `hedron-core` dependency;
- `hedron-data`, `hedron-charts`, and `hedron-maps`;
- the maintained Markdown/sanitization dependencies used by the native Markdown component; and
- Uvicorn for `edron run`.

Exact version ranges are frozen in the Edron Stage 0 packaging packet. Edron publishes `py.typed`,
wheel, and source distributions and follows the repository's Python support policy. The underlying
distributions remain independently importable and testable. Edron does not copy their modules into
its namespace or change their registries.

The authority graph is one way:

```text
edron authoring facade
    -> hedron flagship and first-party satellites
        -> hedron-core where framework-neutral
```

Hedron and its satellites never import Edron. Edron may own vocabulary, opinionated defaults,
request-local output collection, packaging aggregation, and source mapping. Hedron continues to own
rendering, routes, handles, HTMX, binding, responses, assets, security, accessibility primitives,
state contracts, jobs, catalogs, and host integration.

### 2. Primary application and page interface

The primary interface is class based:

```python
import edron as ed

app = ed.App(title="Customers")


@app.page("/customers", title="Customers")
class Customers(ed.Page):
    def render(self) -> None:
        self.text("Search and maintain customers.")
        self.list_customers()

    @ed.fragment
    def list_customers(self, query: str = "") -> None:
        self.dataframe(find_customers(query), name="customers")

    @ed.action(updates=(list_customers,))
    def archive(self, customer_id: int) -> ed.Outcome:
        archive_customer(customer_id)
        return ed.success("Customer archived")
```

The page decorator is the single source for route and page metadata. `title=` supplies the document
title, navigation label, and visible `h1` by default; `show_title=False` disables only the generated
heading. Conflicting duplicate metadata on the class fails registration.

`render()` is the only required lifecycle method. `@ed.fragment` marks safe independently rendered
regions. `@ed.action` marks unsafe operations. Ordinary helper methods remain ordinary Python.
Edron `0.1` does not add `setup`, `mounted`, `rerun`, `before_render`, or `after_render` hooks.

Page classes are controllers, not components, dependency containers, or persistent session objects.
The decorated class symbol remains the class so normal typing, inheritance, documentation, and
unit construction remain understandable. Registration metadata is held by the application, not by
mutating a shared class instance.

The simple constructor also exposes the construction-time production inputs that cannot be changed
safely after middleware and lifespan composition: `session_secret`, `production`, and `build_dir`.
Applications needing additional native FastAPI/Hedron construction options create the native app
explicitly and pass it to `App.from_hedron(...)`; post-construction access through `app.hedron`
does not pretend that immutable middleware or lifespan configuration can be retrofitted.

### 3. Instance and execution lifecycle

Edron creates a fresh page instance for each independently addressable request:

| Request | Instance behavior | Callable phase |
|---|---|---|
| Full page `GET` | One fresh instance | `render()` |
| Fragment `GET` | One fresh instance | The addressed `@ed.fragment` method |
| Action `POST` | One fresh instance | The addressed `@ed.action` method |

`self` is request-local convenience, not durable state. Two concurrent requests never share a page
instance or output buffer. A fragment or action request does not run `render()` first. Page classes
use the inherited Edron constructor in `0.1`; request dependencies use the typed dependency
mechanism described below. Registration rejects a page instance, any custom `__init__`, or a
decorated method that cannot be compiled without ambient values.

The active request/output context is propagated safely across supported async calls using a
`ContextVar`-equivalent mechanism. It is entered and cleared by Edron-owned request boundaries.
Using output methods outside such a boundary produces a deterministic diagnostic rather than
writing to a process-global buffer.

`render`, fragment, and action methods may be synchronous or asynchronous where the underlying
Hedron boundary supports it. Rendering a native component remains deterministic; Edron does not
introduce hidden I/O while Hedron renders a component tree.

### 4. Request-local output and lowering

Output methods append native Hedron `NodeLike` values to the current container and normally return
`None`:

```python
self.text("Ready")
self.metric("Rows", len(rows))
```

Context managers return explicit request-local container objects:

```python
left, right = self.columns(2)
with left:
    self.metric("Revenue", revenue)
with right:
    self.metric("Orders", orders)
```

Input methods return typed Python values:

```python
query = self.text_input("Search", name="query")
```

`name=` supplies stable request and control identity. A label is presentation and is never used as
identity. Edron does not adopt Streamlit's overloaded `key=` vocabulary. Duplicate names within one
binding scope fail with both source locations.

The buffer records native nodes, container relationships, binding declarations, source locations,
and references to registered native handles. It is not a public component tree and has no renderer.
After the author method completes, it validates finite limits and lowers once to an ordinary Hedron
page or fragment value. Partial output is discarded when the author method fails.

Returning a non-`None` value from a normal output-producing `render` or fragment method is a
diagnostic in `0.1`, preventing a confusing mixture of imperative output and return-tree styles.
Pure domain helpers may of course return values. Native full-document replacement, redirects, and
response escape hatches use explicit APIs rather than an overloaded return value.

### 5. Native Hedron interoperability

Edron and Hedron objects must compose through public contracts, without conversion to look-alike
Edron objects.

```python
import edron as ed
import hedron as h

app = ed.App(title="Mixed application")


@app.page("/", title="Home")
class Home(ed.Page):
    def render(self) -> None:
        self.include(h.Alert("Rendered by Hedron", tone="info"))
        self.include(native_status())       # native FragmentHandle mount
        self.include(native_command.button("Run"))


@app.hedron.page("/native")
def native_page():
    return h.Page(h.Text("A native Hedron route on the same app"))
```

The interoperability rules are:

1. `self.include(value)` accepts every public Hedron `NodeLike` value and every public object whose
   Hedron protocol produces `NodeLike`, including mounted fragment handles and action controls.
2. Edron inserts the original native node or handle result. It does not clone, serialize and
   reconstruct, rename, wrap in an incompatible component, or strip theme, asset, CSP,
   accessibility, source, or registry metadata.
3. A full Hedron document page or framework response is not valid inside a body container. Edron
   reports the boundary and directs the author to register a native route through `app.hedron` or,
   for an action, return a supported native outcome/response as defined by the public contract.
4. `action=` accepts a bound Edron action or a compatible native Hedron `ActionHandle`.
   `updates=` accepts Edron fragments and compatible native `FragmentHandle`/`ComponentRef`
   targets. Native target policy and effect validation remain authoritative.
5. Every registered Edron page, fragment, and action maps to exactly one native Hedron screen,
   `FragmentHandle`, or `ActionHandle`. `app.native(surface)` returns that exact public object;
   it does not return a parallel Edron handle with divergent identity.
6. The same native object identity is used for rendering, reverse routing, effects, target
   allowlists, testing, the interaction catalog, Explorer, and explanations.
7. `app.hedron` exposes the underlying Hedron application for native pages, middleware,
   dependencies, integrations, and supported FastAPI/ASGI composition. It is available from app
   construction onward and is not a one-way “eject” operation.
8. Edron-generated and native registrations share the Hedron collision rules. Duplicate routes,
   keys, logical IDs, targets, assets, or incompatible policy fail registration regardless of which
   API registered first.
9. Native Hedron types remain named and documented as Hedron types. Edron may provide convenience
   overloads but must not claim that arbitrary Hedron objects are Edron subclasses.
10. Interoperability uses public protocols and descriptors only. Edron may not depend on private
    renderer internals or mutate frozen native objects after registration.

An implementation matrix is required at Stage 0:

| Native object | Edron consumption | Edron-to-Hedron projection |
|---|---|---|
| `NodeLike` / component | `self.include(...)` and compatible container slots | Edron output lowers to `NodeLike` |
| `FragmentHandle` | mount, refresh control, `updates=` target | `@ed.fragment` has one native `FragmentHandle` |
| `ActionHandle` | control `action=`, native button/form composition | `@ed.action` has one native `ActionHandle` |
| `ComponentRef` / update effect | compatible explicit targeting | Edron target references resolve to the same ref |
| Hedron page/screen handle | native navigation and inspection | Edron page has one native screen/page descriptor |
| Theme, asset, policy, dependency | configured on `app.hedron` or approved Edron shortcut | Edron defaults compile to the native authority |
| Framework response | explicit response escape hatch only | Edron outcomes lower through native response rules |

This matrix must have identity, typing, registry, mixed-composition, and version-compatibility tests.
A feature is not “interoperable” merely because its final HTML looks similar.

### 6. Fragments, safe inputs, and HTMX

`@ed.fragment` declares a safe independently renderable method. At startup, Edron inspects its
signature and registers one native Hedron refreshable handle. Calling the bound method during page
render mounts that handle; the call does not execute a network request or invoke the fragment
renderer twice.

Input controls with `updates=` form a coherent safe GET binding plan. Input `name=` values must
match compatible fragment parameters or an explicit mapping. Edron derives ordinary query
parameters, a native fallback URL, a registered target, and HTMX enhancement. The URL remains
bookmarkable where all values are safe and serializable.

An HTMX request invokes only the addressed fragment method on a fresh page instance and returns a
normal native Hedron fragment response. A non-HTMX request follows the declared ordinary HTTP
fallback. Generated paths and DOM IDs are inspectable but are not authorization boundaries.

Edron exposes native handle configuration for advanced swaps, out-of-band updates, extension use,
preload policy, and explicitly public paths. It does not implement a reduced parallel subset of
HTMX. When Edron lacks vocabulary for a native option, the author composes or configures the native
handle rather than waiting for an Edron-specific copy.

### 7. Actions, forms, and outcomes

`@ed.action` declares an unsafe operation. It lowers to a native Hedron command/action handle and
uses `POST`, CSRF protection, target allowlists, and an ordinary HTTP fallback by default.

```python
@ed.action(updates=(results,))
def refresh_data(self, account_id: int) -> ed.Outcome:
    update_account(account_id)
    return ed.success("Updated")


def render(self) -> None:
    self.button(
        "Refresh",
        action=self.refresh_data.bind(account_id=42),
    )
```

The action is passed as a value. Button calls never return a Boolean that gates mutation, and an
action is never executed merely because a page rendered. `.bind(...)` validates named application
arguments against the action signature. Request dependencies are supplied only by the server and
cannot be shadowed through `.bind(...)` or client data.

Action results use the native typed outcome/effect system for success, validation failure,
authorization failure, conflict, redirect, toast, refresh, and direct updates. Edron may provide
short constructors such as `ed.success(...)`; those constructors return or lower immediately to
the native authority. Domain transactions, idempotency, and authorization remain explicit.

Pydantic models are the default multi-field form boundary. `self.form(Model, action=...)` lowers
through Hedron's schema-derived controls and `form_command` path. Edron does not implement a second
validator or infer a database mutation from a model.

### 8. Dependencies and state ownership

Edron exposes distinct typed interfaces for distinct lifetimes:

| Need | Default owner |
|---|---|
| Shareable safe filters | URL query parameters |
| One submission | Request/form model |
| Bounded user continuity | Typed server session field |
| Durable domain data | Application service/database |
| Recomputable shared result | Declared cache |
| Non-secret presentation preference | Explicit browser preference |

There is no general `session_state` dictionary and page instance attributes do not persist across
requests. Assigning `self.value` may support ordinary computation during one invocation, but it is
never a persistence mechanism.

The proposed dependency interface is a typed class descriptor or equally inspectable declaration:

```python
class Customers(ed.Page):
    repository: CustomerRepository = ed.dependency(get_customer_repository)
```

It must lower to the native host dependency system, retain test overrides, expose scope and source
metadata, and prevent client binding. The public signature is frozen by the
[Edron API contract](../api/EDRON.md#dependency). If Hedron does not yet have a reusable descriptor
with those properties, it is upstream Hedron work.

`ed.cache_data` retains familiar vocabulary for pure/recomputable data and lowers to the native
cache policy. Resource lifetimes, connections, transactions, and cleanup remain explicitly owned
by dependencies or application services; a cache decorator is not a resource manager.

### 9. Jobs and long-running work

`ed.JobFlow` is a thin beginner projection over Hedron `TaskFlow`, not a worker or queue. It may
compose a typed submission form, durable operation identity, status fragment, polling, cancellation
policy, and result presentation. A production application still configures its backend, worker,
retention, authorization, and tenant scope.

Polling is a progressive enhancement over an ordinary status URL. Status, error, cancellation, and
result states remain usable without JavaScript. If the current `TaskFlow` cannot express a golden
application without Edron-owned lifecycle semantics, the missing reusable behavior is added to
Hedron or the Edron feature is deferred.

### 10. First-party batteries and optional capabilities

The following beginner-facing capabilities are Required after `pip install edron` without another
Hedron package installation command:

- semantic text, feedback, layout, inputs, forms, navigation, and file controls supplied by Hedron;
- Edron `table`/`dataframe` paths plus the installed native `hedron-data` editor for explicit direct
  composition; Edron `0.1.0` does not claim a `data_editor` facade method;
- first-party charts supplied by `hedron-charts`;
- first-party maps supplied by `hedron-maps`;
- safe Markdown; and
- the development application server.

“Batteries included” is a dependency aggregation promise, not a reimplementation promise. Public
objects continue to identify their owning Hedron package in introspection and diagnostics.

Third-party adapters are always present as lazy Edron methods when the adapter itself can be loaded
without importing the third-party library. Capability detection checks the installed distribution
and supported version at use time. It does not inspect the requested Edron extra name because
Python packaging does not preserve extras as runtime feature flags.

```python
self.plotly_chart(figure)
```

If Plotly is absent, the call raises a structured `ed.MissingCapabilityError` containing:

- capability and adapter name;
- missing distribution and compatible version range;
- `pip install "plotly>=5.18,<7"` as the direct command;
- `pip install "edron[plotly]"` as the equivalent shortcut;
- the Edron call site; and
- an offline documentation reference.

An incompatible version raises `IncompatibleCapabilityError`; a present dependency that fails to
import raises `BrokenCapabilityError` and preserves a safe exception chain. These states are not
collapsed into “missing.” Edron never invokes `pip`, mutates the environment, or contacts a package
index at runtime.

Extras are curated installation aliases only. For example, `edron[plotly]` declares the same
supported Plotly range used by capability detection. A clean environment test proves that direct
installation and shortcut installation expose identical methods and output. There is no `all`
extra; documentation recommends explicit dependencies for reproducible applications.

### 11. Styling ladder

Edron exposes a small front door to Hedron's existing presentation and styling platform. It does
not define another theme type, token graph, recipe resolver, stylesheet compiler, cascade, or
component-hook manifest.

The teaching order is:

1. use Edron's polished default or select a reviewed built-in theme;
2. create a coordinated brand theme from a small set of semantic choices;
3. use a finite `variant=` or native semantic appearance options on one component;
4. name repeated presentation intent with a native style recipe;
5. apply theme, mode, density, or recipe defaults to an explicit subtree;
6. register ordinary local CSS against public component hooks for product-specific design; and
7. inspect, preview, validate, diff, or eject the native Hedron styling plan.

Each rung is optional. An application can remain on the first or second rung indefinitely, and
moving down the ladder does not switch renderers or invalidate the simpler source.

#### Built-in and branded themes

The zero-configuration path uses an Edron-reviewed native theme that covers the complete required
component, data, chart, map, form, workflow, light/dark, print, and accessibility-mode profile.
Selecting another reviewed built-in remains one string:

```python
app = ed.App(title="Sales", theme="aurora")
```

The smallest custom brand is:

```python
brand = ed.theme(
    "acme",
    base="aurora",
    accent="#635bff",
    density="comfortable",
    geometry="soft",
    typography="system-sans",
    motion="calm",
)

app = ed.App(title="Sales", theme=brand)
```

`ed.theme(...)` is a pure convenience constructor that returns a native Hedron `DesignSystem`; it
is not an Edron wrapper retained at runtime. It accepts only the native bounded brand and
design-group vocabulary, including
typed native `Color` values when advanced color spaces are required. It compiles coordinated light
and dark modes, contrast/focus relationships, reduced-motion behavior, and provenance through the
native validator. Unsafe or unsatisfied combinations fail with the native explanation instead of
silently choosing an unrelated color.

`ed.App(theme=...)` also accepts public native Hedron `Theme`, `ThemeSpec`, and `DesignSystem`
values directly. Edron preserves their identity or canonical native normalization; it does not
flatten them into a smaller Edron schema. Theme packages and server-authoritative preference
selection remain available through `app.hedron`.

Theme configuration is data rather than a page class. Edron does not add a metaclass in which
magic class attributes become tokens: immutable native values, builders, validation reports, and
normal Python composition are more explicit and easier to test.

#### Per-component styling

Common Edron component methods expose a small, consistent set of keyword-only presentation
arguments. Where the native family supports them, these include `size`, `density`, `appearance`,
`emphasis`, `tone`, `width`, `shape`, and `elevation`. Their names and values are the native Hedron
vocabulary and lower directly to native component props.

For the most common compound choices, `variant=` is a finite beginner shorthand:

```python
self.button("Save", action=self.save, variant="primary")
self.button("Delete", action=self.delete, variant="danger")

with self.card(variant="raised"):
    self.metric("Revenue", revenue)
```

Variants are family-specific aliases for named native recipes, not free-form CSS and not a new
cascade. The initial mappings are deliberately small:

| Edron family | Variant | Native intent |
|---|---|---|
| Action control | `primary` | `primary_action` recipe |
| Action control | `secondary` | `secondary_action` recipe |
| Action control | `danger` | `destructive_action` recipe |
| Action control | `quiet` | finite ghost/neutral control appearance |
| Surface/card | `plain` | baseline surface |
| Surface/card | `outlined` | finite outlined surface appearance |
| Surface/card | `raised` | `dashboard_panel` recipe |
| Data view | `compact` | `dense_data` recipe |

Stage 0 freezes the exact family mapping from the native registry; Edron does not hard-code a list
that can drift from Hedron. An unknown family/variant pair fails at registration or render with the
valid choices. `danger` changes presentation only: destructive meaning, confirmation,
authorization, method, and idempotency remain action policy.

Authors may use `recipe="primary_action"` for an explicit named recipe or the native semantic
props for more control:

```python
self.button(
    "Publish",
    action=self.publish,
    recipe="primary_action",
    size="lg",
    width="full",
)
```

`variant=` and `recipe=` are mutually exclusive. Explicit native props are stronger than recipe
defaults under Hedron's established precedence and the explanation records both sources. Edron
does not accept a `style={...}` dictionary, an inline CSS string, arbitrary utility classes, or a
request-derived CSS value on beginner methods.

#### Reusable recipes and explicit scopes

Edron re-exports a deliberately small set of native styling value types by identity. In
particular, `ed.StyleRecipe` is the public Hedron `StyleRecipe`, not a subclass or adapter. A
reusable application design may therefore remain compact:

```python
brand = ed.theme("acme", accent="#635bff").with_recipes(
    ed.StyleRecipe.surface(
        "kpi",
        appearance="raised",
        density="compact",
        padding="md",
    ),
)

app = ed.App(title="Sales", theme=brand)
```

```python
with self.card(recipe="kpi"):
    self.metric("Revenue", revenue)
```

Recipes remain immutable, named, family-scoped, bounded, serializable presentation values. They
cannot add selectors, arbitrary declarations, behavior, state, routes, visibility, authorization,
or DOM reordering.

An explicit request-local scope provides local theme, mode, density, and native style-context
defaults:

```python
with self.style_scope(density="compact"):
    self.dataframe(rows, name="sales")
```

`self.style_scope(...)` lowers to native `StyleScope`/`StyleContext` and emits the same stable
markers. It is a visible subtree boundary, not ambient process state. Fragment swaps inherit their
mounted scope. An out-of-band or overlay host outside that subtree requires an explicit native
context reference; Edron does not guess from the Python call stack.

#### Ordinary CSS as the powerful path

When semantic props and recipes are insufficient, the advanced language is CSS itself:

```python
app.styles(
    "sales-dashboard",
    "styles/sales.css",
    scope="app",
)
```

`app.styles(...)` delegates to the native Hedron stylesheet registration contract. The local file
participates in scoping, the documented application cascade layer, public parts/states, theme
tokens, development reload, production fingerprinting, source maps, asset manifests, CSP, HTMX
asset planning, packaging checks, and upgrade diagnostics. Advanced authors may use standard
selectors, media queries, container queries, and supported modern CSS against documented public
hooks. Private generated classes and observed descendant structure are not compatibility APIs.

Edron never generates a new stylesheet from request data, accepts remote styles/fonts by default,
or inserts an inline `style` attribute to implement the Supported path. Dynamic domain values do
not become CSS. A bounded native custom-property contract may carry an approved presentation value
only when Hedron already validates its type, fallback, scope, and CSP behavior.

#### Styling native and third-party content

Native Hedron components included with `self.include(...)` consume the same resolved theme,
recipes, scopes, application CSS, assets, and cascade as Edron-generated components. Edron must not
wrap them in a reset boundary or translate their public appearance props.

First-party data, chart, and map packages consume the shared semantic theme and mode tokens. A
third-party adapter must declare one of these honest dispositions:

- consumes the resolved theme and required accessibility modes;
- accepts an explicit adapter-specific native theme configuration;
- provides a documented bounded visual fallback; or
- is Experimental and excluded from whole-application theme-conformance claims.

Edron never claims a third-party visualization is fully themed merely because its outer container
matches. HTMX replacement must preserve required style and asset registration without duplicating
CSS or flashing an unthemed intermediate state.

#### Precedence, inspection, and tooling

Edron inherits Hedron's canonical styling precedence and cascade; it does not redefine which token,
scope, recipe, component prop, or application declaration wins. The beginner explanation presents
the normal Python-side order—explicit component prop, explicit recipe/variant, nearest scope,
application design, resolved theme, first-party baseline—while linking application CSS results to
the native cascade/layer explanation.

Styling tools are Edron source-mapped projections over native reports:

```text
edron style check app.py
edron style preview app.py --output .edron/preview
edron style explain app.py
edron style diff BASE CANDIDATE
```

They report resolved themes, modes, tokens, recipes, scopes, component parts/states, winning
sources, suppressed defaults, contrast adjustments, local assets, browser fallbacks, private-hook
coupling, CSP policy, and compatibility fingerprints. Preview uses fixed synthetic fixtures and
does not invoke page loaders, fragments, actions, dependencies, or application data. Exact command
spelling is frozen by the [Edron API contract](../api/EDRON.md#cli-contract), and Edron must not
create a second report schema.

### 12. App tooling and diagnostics

Edron proposes these commands:

```text
edron run app.py
edron check app.py
edron explain app.py
edron doctor
```

`run` imports a trusted application and starts its ordinary ASGI app. `check` performs static checks
that do not execute application callbacks, then may offer a clearly separated trusted-registration
check. `explain` projects the native Hedron registry, descriptors, policies, dependencies, assets,
and source map in Edron vocabulary. `doctor` reports Edron/Hedron package compatibility and the
available, missing, incompatible, or broken status of curated third-party capabilities.

Diagnostics use stable families for application registration, page lifecycle, execution phase,
binding, forms, dependencies, capabilities, lowering, and native interoperability. Every error
contains a concise title, explanation, Edron source location where known, native descriptor identity
where registered, and concrete remediation. Sensitive dependency values, form data, credentials,
and session values are redacted.

### 13. Upstream Hedron enablement

Before Edron implementation, Stage 0 inventories every golden-application need and assigns one of
three dispositions:

1. **Use existing Hedron:** identify the public primitive and required conformance evidence.
2. **Add to Hedron:** create an independently useful native capability first, with its own RFC or
   accepted contract, implementation plan, compatibility story, and acceptance owner.
3. **Keep in Edron or defer:** keep only authoring ergonomics in Edron; otherwise defer rather than
   create a hidden Edron runtime.

Initial upstream candidates are the same `UP-001`–`UP-011` rows locked by the capability inventory
and acceptance packet:

| Hedron workstream | Requirements | Cohesive native deliverable |
|---|---|---|
| `HEDRON-WS-CLASS` | `UP-001`, `UP-003` | fresh-instance class compilation with typed dependency lifecycle |
| `HEDRON-WS-INTERACTIONS` | `UP-002`, `UP-004`–`UP-006` | transport-equivalent filters, action fallback, confirmation, and success outcomes |
| `HEDRON-WS-PROVENANCE` | `UP-007`, `UP-011` | exact registry identity and bounded external-facade provenance in native reports |
| `HEDRON-WS-JOBS` | `UP-008` | application-oriented native `TaskFlow` composition |
| `HEDRON-WS-STYLING` | `UP-009`, `UP-010` | registry-derived variants and cross-package theme/token parity |

These five workstreams are independently useful Hedron changes with native vocabulary, ownership,
tests, changelogs, and release decisions. Grouping coordinates related contracts; it does not merge
their acceptance identities or let one completed row satisfy another.

| ID | Edron need | Hedron question |
|---|---|---|
| `UP-001` | Page methods compiled as bound actions/fragments | Can the existing fresh-instance class compiler and handle descriptors be generalized without Edron knowledge? |
| `UP-002` | Several named filters updating one fragment | Does Hedron need a first-class coherent GET filter-binding plan? |
| `UP-003` | Typed request-scoped fields on page classes | Does the native dependency system need a public descriptor with static explanation and overrides? |
| `UP-004` | Owning-page fallback for generated actions | Can a safe fallback derive from a registered screen without making path identity authoritative? |
| `UP-005` | Accessible destructive confirmation | Does Hedron need a reusable native confirmation flow with no-JavaScript behavior? |
| `UP-006` | Equivalent simple success presentation | Can one native success outcome retain authoritative status and accessible meaning under HTMX and ordinary HTTP? |
| `UP-007` | Exact native object projection from class members | Can the shared registry expose a stable lookup from source surface to native handle? |
| `UP-008` | Simple job form/status/result composition | Which reusable `TaskFlow` improvements are required? |
| `UP-009` | Compact component variants without a parallel vocabulary | Can variant aliases be projected from native recipe-family registry metadata? |
| `UP-010` | One brand call covering first-party data/chart/map packages | Do all required packages consume the complete shared theme/token contract? |
| `UP-011` | Source-mapped style explanations in Edron vocabulary | Can native style plans retain an external facade source without duplicating report schemas? |

Each row must resolve as `Existing` or `Shipped` in the upstream lock before Decision B. If review
instead keeps behavior wholly Edron-specific or defers the facade surface, the RFC, public
contracts, inventory, goldens, and lock must first remove or reclassify that Required dependency;
an `Edron-only` label cannot falsely satisfy an upstream row.

No Edron release may implement a candidate locally and describe it as native parity while the
underlying route, binding, security, lifecycle, or registry semantics differ.

## Alternatives considered

| Alternative | Disposition |
|---|---|
| Copy Streamlit's module-global `ed.*` interface | Rejected: implicit ambient state and rerun semantics conflict with request concurrency and make `ui` behave like disguised `self`. |
| Document `import edron as st` | Rejected: it implies compatibility Edron does not provide and obscures Edron-specific semantics. |
| Make Edron a one-for-one Streamlit compatibility layer | Rejected: preserves non-transferable execution and state practices and competes with RFC-0061's reviewable migration approach. |
| Use only function pages | Deferred as a possible secondary convenience; classes give related render, fragment, action, and dependency behavior a clear request-local owner. |
| Require component-tree returns everywhere | Rejected for the primary style: it loses the approachable sequential vocabulary. Native Hedron return composition remains available on native routes. |
| Declare widgets as class attributes/descriptors | Rejected as the primary style: it separates controls from layout and encourages shared-state confusion. Dependencies may use descriptors because they represent injected capability, not rendered output. |
| Add many page lifecycle hooks | Rejected: three roles—render, fragment, action—are sufficient and easier to reason about. |
| Wrap every Hedron object in an Edron counterpart | Rejected: breaks identity, typing, metadata, and ecosystem interoperability. |
| Expose native Hedron only through irreversible ejection | Rejected: mixed native/Edron composition is a normal authoring mode. |
| Build Edron-only endpoints and HTMX helpers | Rejected: creates competing route, policy, and interaction authorities. |
| Provide only a few fixed Edron themes | Rejected: easy defaults are necessary but cannot replace native theme, recipe, scope, token, CSS, and package composition. |
| Model CSS properties as Python dictionaries | Rejected: creates an incomplete CSS-in-Python language, weakens tooling, and duplicates the native compiler boundary. |
| Put theme values on a magic `Page` or `Theme` subclass | Rejected as the primary interface: immutable native theme values and normal composition have clearer construction, validation, and provenance. |
| Accept arbitrary inline CSS on every output call | Rejected: bypasses tokens, public hooks, asset manifests, CSP, source maps, preference fallbacks, and upgrade checks. |
| Expose only native Hedron styling APIs | Rejected for the beginner path: one small brand constructor and finite variants materially reduce first-use complexity while returning native objects. |
| Create an Edron-specific theme and recipe registry | Rejected: it would diverge from native components and break mixed Edron/Hedron styling. |
| Limit Edron to Hedron's current APIs | Rejected: Edron may identify missing reusable foundations, but those foundations must be added upstream. |
| Merge all `hedron-*` source into Edron | Rejected: aggregation through dependencies preserves ownership, release clarity, and direct native use. |
| Require `edron[charts]` or `edron[data]` for first-party basics | Rejected: violates the batteries-included beginner promise. |
| Use extras as runtime flags | Rejected: installed extras are not a reliable runtime capability record. |
| Auto-install an optional dependency on first use | Rejected: mutates environments, may require network/privilege, and harms reproducibility. |
| Publish `edron[all]` | Rejected: unbounded dependency weight and incompatible third-party ecosystems make it misleading. |

## Security implications

- Safe rendering and fragments use `GET`; mutations use unsafe methods, normally `POST`. Edron may
  not infer safety from a friendly method name.
- Native Hedron CSRF, authorization, tenancy, target allowlists, redirect validation, cache scope,
  upload policy, CSP, asset integrity, and replay/idempotency controls remain authoritative.
- `.bind(...)`, query values, form fields, browser preferences, generated paths, DOM IDs, and HTMX
  headers are untrusted input or routing facts, never authorization evidence.
- Dependency parameters and server-owned context cannot be shadowed by client values or action
  binding. Registration rejects ambiguous names.
- The fresh-instance rule prevents accidental cross-request page-object state, but does not replace
  application review of process globals, caches, repositories, or external clients.
- Generated action fallbacks must preserve the unsafe method and CSRF behavior. A no-JavaScript
  fallback may not turn a mutation into a link or safe request.
- Native object inclusion preserves trust boundaries. Including `RawHTML`, custom assets, third-
  party scripts, native responses, or relaxed policy remains subject to the same explicit Hedron
  review; Edron does not sanitize an object merely by including it.
- Theme, recipe, scope, and component presentation inputs are application-authored bounded values.
  Request/user/domain data cannot become a selector, CSS declaration, token name, asset URL,
  stylesheet source, remote font, or unrestricted custom property.
- Local stylesheets retain native root, traversal, symlink, URL, CSP, integrity, manifest, and
  production-build checks. `scope="app"` is not a security sandbox for hostile CSS.
- Styling cannot hide an authoritative value as the only access path, grant authorization, change
  method/route/effect semantics, reorder focus/DOM meaning, or make an action destructive.
- Optional capability loading imports only declared adapters/dependencies. It never imports a name
  supplied by a request, executes installation commands, or treats package metadata as trusted
  application authorization.
- Explanations and source maps redact secrets, cookies, tokens, dependency values, private payloads,
  and unsafe callable representations. Developer paths follow existing Hedron disclosure policy.
- Jobs require authoritative operation, user, and tenant scope. Polling IDs and generated URLs are
  not access control.
- Registration and request plans have finite limits for pages, surfaces, controls, bindings,
  targets, nested containers, output nodes, payloads, and diagnostic data. Limit exhaustion fails
  closed before partial mutation or response emission where possible.

Threat modeling and security review are release gates. The Edron acceptance packet must include
cross-tenant, CSRF, target-forgery, dependency-shadowing, fallback, stale/replay, open-redirect,
unsafe-content, and diagnostic-redaction tests.

## Accessibility implications

Edron defaults inherit Hedron's semantic components and accessibility contracts. The facade adds
these obligations:

- a page has one meaningful document title and one `h1` by default;
- every control requires an accessible label even when visual presentation is customized;
- validation summaries and field errors are programmatically associated and keyboard reachable;
- fragments preserve or deliberately move focus, busy state, and announcements according to the
  native interaction contract rather than replacing arbitrary DOM;
- action pending, success, error, conflict, and retry states avoid duplicate or high-frequency live
  announcements;
- tables retain headers, captions where needed, keyboard behavior, and bounded responsive fallback;
- charts and maps require a meaningful text summary or accessible tabular alternative for Supported
  claims; visual-only third-party adapters cannot silently inherit a Supported claim;
- confirmation and destructive actions work with keyboard, assistive technology, and no JavaScript;
- layout helpers preserve logical DOM order, zoom, reflow, and reduced-motion preferences; and
- variants, recipes, branded themes, local CSS, data views, charts, and maps retain visible focus,
  contrast, forced-colors/high-contrast, reduced-motion/transparency, print, RTL, zoom/reflow,
  narrow-width, and non-color state fallbacks required by their native maturity claim; and
- all golden applications remain operable through ordinary HTML/fallback paths when HTMX or
  JavaScript is unavailable.

Automated semantic, keyboard, contrast, and browser checks are required. Human assistive-technology
claims remain separate until sessions are recorded under the repository accessibility process.

## Performance implications

Edron adds a fresh lightweight page object, request-local buffer, source mapping, and one lowering
pass. It must not add a second render pass, duplicate native component trees, eagerly import every
optional integration, or duplicate assets already registered by Hedron.

Stage 0 records baselines and numeric budgets for:

- clean import and application registration time;
- incremental Edron registration cost per page/fragment/action;
- full-page and fragment latency overhead relative to an equivalent native Hedron fixture;
- request-local allocation and peak memory per emitted node;
- output, binding, target, and nesting limits;
- generated HTML and metadata size;
- optional-capability detection and negative-result caching; and
- first-party chart/table/map asset deduplication;
- theme/recipe resolution and validation at registration/build time; and
- stylesheet count, raw/gzip bytes, duplicate assets, and unthemed-content behavior across full and
  fragment responses.

Static registration work is preferred over repeated request introspection. Optional third-party
imports occur on first adapter use and may be cached by capability/version, but a previously broken
import must remain diagnosable. Data methods keep native row, byte, geometry, and chart complexity
limits. Fragments are encouraged for bounded recomputation; they are not permission for unbounded
fan-out or hidden N+1 I/O.

Performance claims require comparison against behaviorally equivalent native Hedron applications,
including mixed Edron/native composition. Any convenience that materially duplicates native work
must be redesigned or disclosed before acceptance.

## Testing strategy

The implementation requires layered evidence:

1. **Contract/unit tests:** decorator metadata, class validation, fresh instances, context cleanup,
   output ordering, containers, duplicate names, binding, `.bind(...)`, return-value errors,
   diagnostics, and source maps.
2. **Concurrency tests:** simultaneous page, fragment, and action requests prove that instances,
   buffers, inputs, dependencies, and outcomes never leak across requests.
3. **Native interoperability tests:** exact native object identity, `NodeLike` inclusion, native
   fragments/actions in Edron controls, Edron surfaces in native effects/navigation, mixed
   registration order, collision behavior, theme/assets/policy preservation, Explorer/catalog
   projection, and native response boundaries.
4. **HTTP/HTMX integration tests:** full pages, safe GET filters, bookmarkable URLs, fragment swaps,
   action POSTs, CSRF, validation, multi-target effects, fallback navigation, errors, and no-JavaScript
   operation.
5. **Security tests:** the adversarial cases listed in the Security section and preservation of
   native fail-closed behavior through every convenience path.
6. **Accessibility tests:** semantic snapshots, keyboard flows, focus, announcements, reflow,
   reduced motion, accessible tables/chart alternatives, and no-JavaScript scenarios.
7. **Packaging tests:** clean wheel and sdist environments, offline imports, `py.typed`, license and
   asset data, required first-party capabilities, and compatible package ranges.
8. **Optional capability matrix:** absent, directly installed, extra-installed, incompatible, and
   broken-import environments. Direct and extra installation must expose identical behavior.
9. **Typing tests:** page methods, bound actions/fragments, dependency fields, input return types,
   native handles, and mixed Edron/Hedron composition under the supported type checkers.
10. **Styling tests:** built-in and branded themes, finite variant mappings, recipe precedence,
    explicit scopes, native component inclusion, local CSS registration, public hooks, source
    maps, CSP, asset deduplication, HTMX swaps, light/dark/accessibility modes, responsive/RTL/print,
    visual regressions, native report identity, and third-party adapter dispositions.
11. **Golden application tests:** every application in the design fixture runs as written after its
    contract is accepted and has HTML, interaction, security, accessibility, and explanation
    evidence.
12. **Differential tests:** selected Edron applications and their explicit native Hedron lowerings
    produce equivalent descriptors, policies, registered assets, HTTP semantics, and rendered
    meaning. Byte-for-byte HTML is required only where the native contract promises it.

All accepted upstream Hedron additions have their own native tests before Edron consumes them.
An Edron-only test cannot be the sole evidence for a new Hedron capability.

## Compatibility and migration

Edron is additive. Existing Hedron applications, native components, handles, pages, routes, and
deployment commands remain valid. Installing Edron adds dependencies but does not change behavior
of an existing `hedron` import or application.

Edron `0.x` declares a bounded compatible Hedron release train and checks incompatible mixed
versions with a clear startup diagnostic. Public Edron APIs follow semantic-versioning rules within
the stated pre-1.0 policy. Native Hedron descriptor schema and object compatibility follow their
own established policies; Edron does not freeze private implementation details.

An application may adopt Edron incrementally:

1. construct `ed.App` and continue registering native routes through `app.hedron`;
2. convert one page to an `ed.Page` while retaining native components and handles;
3. adopt Edron fragments/actions only where their vocabulary helps; and
4. move back to a native surface locally without changing application runtime or registry.

No global “Edron mode” or irreversible ejection exists. The native object lookup and explanation
APIs provide a review path before replacing a generated surface.

Edron does not promise that Streamlit source runs unchanged. Migration material maps familiar words
while explicitly redesigning reruns, callbacks, session state, cache/resource ownership, and side
effects. RFC-0061 may eventually generate Edron-style source as an additional reviewed target, but
that is outside this RFC and may not weaken its migration findings.

Extras remain backward-compatible installation conveniences only. Removing an extra alias in a
future major release cannot make direct compatible dependency installation stop working unless the
underlying adapter itself is deprecated with a documented replacement.

Edron styling is also additive. Existing native `Theme`, `ThemeSpec`, `DesignSystem`,
`StyleRecipe`, `StyleScope`, component presentation props, and registered stylesheets remain valid
when passed through Edron. Variant aliases have a versioned native-recipe mapping and migration
diagnostic; they do not freeze generated CSS classes or private component markup. Removing Edron
from a mixed application leaves its native styling assets and source usable through the documented
Hedron APIs.

## Remaining Stage 0 questions

The [public API contract](../api/EDRON.md) and
[state and interaction contract](../api/EDRON_STATE_INTERACTION.md), together with the
[packaging contract](../api/EDRON_PACKAGING.md), resolve the beginner names, return behavior, page
class rules, descriptor behavior, native app/property/lookup spelling, initial direct identity
exports, state ownership and lifecycle, interaction defaults, job facade presence, base battery
boundaries, optional shortcut semantics, artifact/release behavior, styling constructor/variants/
scope, and deliberately absent 0.1 features. Stage 0 still must resolve:

1. What numeric performance, registration, output, binding, styling, and diagnostic budgets satisfy
   the acceptance gates?
2. Which upstream candidates are already fully supported by public Hedron contracts, and which
   require separate Hedron RFCs before Edron implementation?
3. What first compatible Hedron release train contains all accepted upstream enablement, and
   therefore supplies Edron's exact required dependency pins?
4. Which native confirmation, owning-page fallback, dependency-descriptor, filter-plan, job-flow,
   and source-to-handle lookup signatures must be added or refined before the Edron contract can be
   implemented without a parallel authority?
5. Do the curated third-party ranges still match their owning package adapters at the release cut,
   or must the draft contract and extras metadata be revised together before acceptance?

## Acceptance criteria

This RFC may move from Draft to Accepted only after the following contract evidence exists and
Decision A in the [Edron 0.1 acceptance packet](../acceptance/EDRON_001.md) is Verified. Edron
runtime implementation begins only after that packet separately records Decision B as Verified.

- **EDR-STAGE0-001:** A public API contract freezes `App`, `Page`, page registration, output/input
  behavior, containers, fragments, actions, forms, outcomes, native lookup, and diagnostics used by
  all golden applications.
- **EDR-GOLDEN-001:** Every golden application has an approved Edron source fixture, conceptual
  native lowering, state/security/accessibility analysis, and executable acceptance scenario.
- **EDR-INVENTORY-001:** The capability inventories account for every public surface, base and
  optional installation, native escape hatch, upstream dependency, deferral, cross-cutting
  disposition, and acceptance fixture; every `EDR-INV-*` criterion has corresponding evidence.
- **EDR-IMPLEMENTATION-001:** The implementation specification maps every accepted capability to
  package/module boundaries, definition/request lowering, native authority, staged work, tests,
  artifacts, and release evidence; every `EDR-IMPL-*` requirement has a release-gate owner.
- **EDR-AUTHORITY-001:** Architecture review proves Edron introduces no renderer, route registry,
  interaction registry, HTMX runtime, security authority, durable state store, or job queue.
- **EDR-LIFECYCLE-001:** Page, fragment, and action requests create distinct fresh instances;
  concurrency and context-cleanup tests prove no cross-request leakage.
- **EDR-LOWER-001:** Each Edron surface explains its source, native descriptor, routes, methods,
  bindings, targets, effects, policies, dependencies, assets, and limitations without executing
  application callbacks.
- **EDR-INTEROP-001:** The native interoperability matrix is frozen and its identity, typing,
  metadata, registry, collision, mixed-composition, and compatibility tests pass.
- **EDR-HTMX-001:** Safe filter changes use native Hedron GET/HTMX handling, target policy, history,
  and ordinary HTTP fallback; no Edron-only client runtime or author-authored JavaScript is required.
- **EDR-ACTION-001:** Mutations lower to native unsafe action/form boundaries with CSRF,
  authorization composition, binding protection, explicit effects/outcomes, and accessible fallback.
- **EDR-STATE-001:** The companion state and interaction contract is approved and every
  `EDR-SI-*` owner, lifecycle, binding, concurrency, parity, security, accessibility, explanation,
  and performance criterion has corresponding evidence; page fields are never presented as
  persistent state.
- **EDR-PACKAGE-001:** The companion packaging contract is approved and every `EDR-PKG-*`
  artifact, base, train, authority, capability, extras, diagnostic, import, asset, drift, security,
  compatibility, and performance criterion has corresponding evidence; a clean `pip install edron`
  runs the first-party golden paths without another Hedron package installation.
- **EDR-CAPABILITY-001:** Direct third-party installation and matching extra installation activate
  identical adapters; missing, incompatible, and broken imports yield structured exact remediation;
  no runtime installer or `all` extra exists.
- **EDR-STYLE-001:** The default theme, built-in selection, `ed.theme(...)`, finite variants,
  native semantic props/recipes/scopes, local CSS, precedence, style tooling, and third-party
  disposition contracts all lower to the single native Hedron styling authority and pass the
  styling, accessibility, CSP, browser, HTMX, performance, and interoperability matrices.
- **EDR-UPSTREAM-001:** Every identified missing foundation has an approved `existing`, `upstream`,
  `Edron-only ergonomics`, or `deferred` disposition. Upstream items have independent native
  ownership and preserve the one-way dependency graph.
- **EDR-SECURITY-001:** Security review and the adversarial matrix pass without weakening native
  Hedron policy on any Edron or mixed native path.
- **EDR-A11Y-001:** Automated semantic/keyboard/browser evidence and recorded manual-review scope
  cover all golden applications, including no-JavaScript operation and chart/table alternatives.
- **EDR-PERF-001:** Numeric budgets are frozen and equivalent native-versus-Edron benchmarks meet
  them for registration, full-page, fragment, action, memory, and asset behavior.
- **EDR-TYPING-001:** Supported type checkers validate the public class, input, dependency,
  action/fragment binding, and native interoperability fixtures without required casts in the
  ordinary path.
- **EDR-TOOLING-001:** `run`, `check`, `explain`, and `doctor` contracts, exit statuses, trust
  boundaries, stable diagnostics, offline behavior, and source-mapped native style projections are
  documented and tested.
- **EDR-COMPAT-001:** Clean install, upgrade, incompatible-version, mixed-registration, wheel,
  source-distribution, package-data, and rollback tests pass on the supported Python/platform matrix.
- **EDR-DOCS-001:** The quickstart, Pythonic interface guide, Streamlit vocabulary/migration guide,
  Hedron interoperability guide, styling ladder, theme and local-CSS guides, state guide, optional
  dependency guide, deployment guide, API reference, and troubleshooting catalog match the
  accepted contracts.
- **EDR-ACCEPTANCE-001:** The human acceptance packet and machine gate enumerate separate design,
  implementation-entry, and publication decisions; every Required gate is fail-closed, and all
  upstream locks, package locks, budgets, commands, retained artifacts, and sign-offs required for
  the applicable decision are Verified.

Acceptance of this RFC approves the architecture and contract-development work. It does not by
itself claim that Edron exists on PyPI, that the sketched APIs are implemented, or that unresolved
upstream Hedron capabilities have shipped.
