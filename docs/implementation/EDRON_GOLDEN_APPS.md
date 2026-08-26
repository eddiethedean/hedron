# Edron golden applications

**Status:** Design draft; no Edron API in this document is implemented or available<br>
**Purpose:** Input to the proposed Edron RFC and public API contract<br>
**Baseline:** Hedron `0.66.x` repository train
**Public API contract:** [Edron 0.1 public API](../api/EDRON.md)
**State and interaction contract:** [Edron 0.1 state and interaction](../api/EDRON_STATE_INTERACTION.md)

This document tests the proposed Edron authoring model against six representative applications
before runtime code or public signatures are committed. The examples are executable-design
sketches, not tutorials and not availability claims.

Edron is a batteries-included, class-oriented authoring facade over Hedron. It must lower into
existing or explicitly planned Hedron renderers, screens, handles, forms, fragments, actions,
jobs, assets, security policies, and HTMX behavior. It must not introduce a second renderer,
browser runtime, route authority, job queue, state store, or dependency solver.

Edron is also a design customer for Hedron. A golden application may expose a missing lower-level
capability that should be added to Hedron before the Edron facade is implemented. Edron is not
limited to wrapping the exact current Hedron surface; it is limited to preserving one underlying
Hedron authority for framework behavior.

The examples deliberately retain useful Streamlit vocabulary such as `sidebar`, `selectbox`,
`slider`, `columns`, `metric`, `dataframe`, and chart names. They do not preserve Streamlit's
module-global rendering context, whole-script rerun model, mixed `session_state` dictionary, or
mutation-under-`if button` pattern.

## Candidate conventions shared by all examples

These are design candidates exercised by the examples. They become normative only if accepted by
the Edron RFC and public API contract.

1. Applications use `import edron as ed` and construct one explicit `ed.App`.
2. `@app.page(...)` registers an `ed.Page` subclass. The class is a request-scoped controller, not
   a rendered component and not persistent state.
3. Edron creates a fresh page instance for each page, fragment, and action request.
4. `render()` is the only required page method. Output methods append to the active request-local
   container and normally return `None`.
5. Decorated `@ed.fragment` methods lower to native Hedron refreshable fragment handles.
6. Decorated `@ed.action` methods lower to native Hedron action/form-command handles and execute
   only on an unsafe request boundary, normally `POST`.
7. Inputs return ordinary typed Python values and use `name=` for stable identity and request
   binding. A visible label is not identity.
8. `updates=` names the fragment or fragments affected by a safe input change. Edron derives the
   generated GET binding from matching input names and fragment parameter names.
9. `action=` accepts a bound Edron action. `.bind(...)` supplies explicit action arguments without
   callback `args`/`kwargs` bags.
10. The page decorator's `title=` supplies the document title, navigation label, and visible `h1`
    by default. `show_title=False` is the explicit escape hatch.
11. `pip install edron` includes native tables, data editing, first-party charts, maps, Markdown,
    and the application server. Third-party integrations activate when their compatible dependency
    is installed directly; `edron[extra]` is only an installer shortcut.
12. Native Hedron components remain embeddable through the canonical `self.include(...)` method.
13. Styling progresses from a built-in theme to `ed.theme(...)`, finite component variants, native
    `StyleRecipe`/`StyleScope`, and registered local CSS; every level uses Hedron's single styling
    authority.

## Upstream-enablement rule

When a proposed Edron feature cannot lower cleanly through a current Hedron primitive, Stage 0
must choose one of three explicit dispositions:

1. **Add to Hedron:** implement a reusable native Hedron capability first, then lower Edron into
   it.
2. **Keep in Edron:** implement authoring vocabulary, class ergonomics, packaging aggregation, or
   source mapping that does not become a second framework authority.
3. **Defer or reject:** do not emulate a missing foundation with hidden Edron-only runtime
   behavior.

The following concerns normally belong in Hedron when new foundation work is required:

- route, action, fragment, region, and handle semantics;
- HTMX requests, targets, swaps, effects, fallbacks, and progressive enhancement;
- request binding, validation, dependency lifetimes, and response conversion;
- CSRF, authorization composition, idempotency, security policy, and trust boundaries;
- component rendering, assets, CSP, accessibility, state ownership, jobs, and polling; and
- catalogs, manifests, diagnostics, tracing, and host portability.

The following concerns normally remain Edron-owned:

- `Page` class vocabulary and beginner-facing method names;
- collection of imperative page output into a lowering plan;
- batteries-included dependency aggregation and optional-capability messages;
- Edron source locations and explanations mapped onto Hedron descriptors; and
- opinionated defaults that select among existing Hedron policies without weakening them.

An upstream Hedron addition must be independently useful through native Hedron authoring, have its
own public/implementation/acceptance ownership, and avoid importing or depending on Edron. Package
dependency direction remains one way:

```text
Edron authoring facade
        -> Hedron flagship and satellites
                -> hedron-core where framework-neutral
```

The golden applications currently suggest several upstream candidates for investigation rather
than assuming Edron-local implementations:

| Edron design need | Candidate Hedron enablement to evaluate |
|---|---|
| Page methods that become bound actions/fragments | Generalize the existing class-handler compiler and native handle descriptors. |
| Several named filters updating one fragment | Add a first-class coherent GET-filter binding plan over native forms and fragments. |
| Request-scoped dependency fields on a page class | Add or reuse a typed native dependency descriptor with static explanation and test overrides. |
| Owning-page native fallback for generated actions | Add a safe handle-owned fallback derivation rule if current explicit fallback remains too low-level. |
| Accessible confirmation with native fallback | Add a reusable Hedron confirmation flow rather than an Edron-only browser behavior. |
| Simplified job form/status/result composition | Extend `TaskFlow` only where the need is reusable outside Edron. |

These are candidates, not decisions. The RFC must determine whether each need is already satisfied,
requires upstream Hedron work, belongs only to Edron ergonomics, or is deferred.

## Golden application 1: hello page

### User outcome

A new user can install Edron, create one file, and run a semantic server-rendered page without
learning FastAPI, route decorators, Hedron `Page` construction, HTML, HTMX, or Uvicorn invocation.

### Proposed Edron source

```python title="app.py"
import edron as ed

app = ed.App(title="Hello")


@app.page("/", title="Hello, Edron")
class Home(ed.Page):
    def render(self) -> None:
        self.text("A Python application rendered by Hedron.")
        self.info("No frontend build is required.")
```

```bash
edron run app.py
```

The `app` object is also an ordinary ASGI application for advanced launch and deployment:

```bash
uvicorn app:app --reload
```

### Conceptual Hedron lowering

```text
ed.App(title="Hello")
    -> Hedron(title="Hello", secure Edron defaults, explicit development session policy)
    -> production gate requires an application-configured session secret

@app.page("/", title="Hello, Edron")
    -> one native Hedron screen/page route
    -> generated Page with one document title and one visible h1
    -> Home instantiated inside a request-local render context

self.text(...)
    -> Hedron Text

self.info(...)
    -> Hedron informational Alert
```

The generated document must retain Hedron's semantic page shell, escaping, accessibility,
security headers, asset policy, diagnostics, and no-JavaScript correctness.

### Design pressure and proposed disposition

| Question | Proposed disposition |
|---|---|
| Must a beginner construct `Page(...)`? | No. Edron owns the ordinary page shell. |
| Does `render()` return a component tree? | Not normally. Request-local methods collect nodes and `render()` returns `None`. |
| Is `title=` metadata or visible content? | Both by default, avoiding a duplicated `self.title(...)`. |
| Can the visible heading be customized? | Yes: `show_title=False`, followed by explicit heading composition. |
| Is a function-style page required for 0.1? | No. One primary class style is easier to teach and test. |
| Does Edron hide the ASGI app? | No. The explicit `app` remains deployable and inspectable. |

### Acceptance sketch

- a clean `pip install edron` environment imports and launches this file;
- GET `/` contains exactly one `h1` and the two content messages without user-authored JavaScript;
- the wheel requires no Node installation or network asset fetch at render time;
- two concurrent requests use distinct `Home` instances and render identical output; and
- `edron check app.py` explains the generated page and underlying Hedron screen.

## Golden application 2: filtered sales dashboard

### User outcome

A data-oriented user builds a familiar dashboard with sidebar filters, metrics, a chart, and a
table. Filter changes update only the result region through HTMX, preserve a usable GET fallback,
and produce a bookmarkable URL.

### Proposed Edron source

```python title="app.py"
from typing import Literal, TypedDict

import edron as ed

Region = Literal["All", "North", "South"]
REGIONS: tuple[Region, ...] = ("All", "North", "South")


class SaleRow(TypedDict):
    month: str
    region: Region
    revenue: int
    orders: int

app = ed.App(title="Sales")


@ed.cache_data(ttl=300, scope="public")
def load_sales() -> list[SaleRow]:
    return [
        {"month": "Jan", "region": "North", "revenue": 3200, "orders": 32},
        {"month": "Feb", "region": "North", "revenue": 4100, "orders": 38},
        {"month": "Jan", "region": "South", "revenue": 2800, "orders": 29},
        {"month": "Feb", "region": "South", "revenue": 3600, "orders": 34},
    ]


def filtered_sales(region: Region, minimum: int) -> list[SaleRow]:
    return [
        row
        for row in load_sales()
        if (region == "All" or row["region"] == region) and row["revenue"] >= minimum
    ]


@app.page("/", title="Sales dashboard")
class SalesDashboard(ed.Page):
    def render(self) -> None:
        region = self.sidebar.selectbox(
            "Region",
            REGIONS,
            name="region",
            default="All",
            updates=self.results,
        )
        minimum = self.sidebar.slider(
            "Minimum revenue",
            minimum=0,
            maximum=5_000,
            default=0,
            step=500,
            name="minimum",
            updates=self.results,
        )

        self.results(region=region, minimum=minimum)
        self.button("Reload data", action=self.reload_data)

    @ed.fragment
    def results(self, region: Region, minimum: int) -> None:
        rows = filtered_sales(region, minimum)
        revenue = sum(row["revenue"] for row in rows)
        orders = sum(row["orders"] for row in rows)

        revenue_column, orders_column = self.columns(2)

        with revenue_column:
            self.metric("Revenue", revenue, format="$,.0f")

        with orders_column:
            self.metric("Orders", orders)

        self.line_chart(
            rows,
            x="month",
            y="revenue",
            title="Monthly revenue",
            description="Revenue for the selected region and minimum.",
        )
        self.dataframe(rows, name="sales", page_size=25)

    @ed.action
    def reload_data(self) -> ed.Outcome:
        load_sales.invalidate()
        return ed.refresh(self.results).toast("Sales data reloaded")
```

### Conceptual Hedron lowering

```text
SalesDashboard page
    -> Hedron screen and Page/AppShell composition

sidebar inputs
    -> one validated GET form whose values are query parameters
    -> /?region=North&minimum=3000
    -> HTMX enhancement targets only the results region

@ed.fragment results(region, minimum)
    -> native FragmentHandle with a generated stable path and region
    -> FragmentHost containing the initial result
    -> GET fragment response with target allowlisting

self.line_chart(...)
    -> hedron-charts first-party LineChart
    -> semantic summary/table fallback and remount after HTMX swap

self.dataframe(...)
    -> hedron-data DataTable

@ed.action reload_data
    -> native Hedron action/command, POST, CSRF protected
    -> declared refresh of results plus toast outcome
    -> owning page as the native no-JavaScript fallback
```

Edron must not lower both filters to independent forms that lose the other filter's value. The
input collector owns one coherent filter state and submits every named filter required by the
target fragment.

### Design pressure and proposed disposition

| Question | Proposed disposition |
|---|---|
| Where do ordinary filter values live? | Query parameters by default, because they are safe and shareable. |
| How are fragment parameters bound? | By explicit matching `name=` and typed method parameters. Missing or ambiguous bindings fail during app registration/check. |
| Does `updates=` accept strings? | No. It accepts decorated fragment references or a finite sequence of them. |
| What happens without HTMX? | The GET form performs a full-page request with the same query values and outcome. |
| Are first-party charts optional? | No. Beginner charts ship with base Edron. |
| Does `reload_data` run during rendering? | No. Calling an action during render is a phase error; passing the action reference is allowed. |
| Can an action refresh an undeclared target? | No. Native Hedron effect/target validation remains authoritative. |

### Acceptance sketch

- the default result contains revenue `13,700` and orders `133`;
- `/?region=North&minimum=4000` contains one row, revenue `4,100`, and orders `38`;
- an invalid minimum and unknown region are rejected before `filtered_sales` runs;
- a filter HTMX request updates only the allowlisted results region;
- the same filter works through an ordinary GET with no HTMX headers;
- the chart retains an accessible title, description, and table fallback;
- reload requires a valid CSRF token and cannot execute on GET; and
- concurrent filter requests cannot share page/container/input state.

## Golden application 3: validated customer CRUD

### User outcome

A user creates and deletes customers without defining endpoints, parsing form bodies, wiring CSRF,
or hand-authoring validation markup. Business persistence and authorization remain application
responsibilities and are ordinary Python dependencies.

### Proposed Edron source

```python title="app.py"
from typing import Annotated, Protocol

import edron as ed
from pydantic import BaseModel, Field

app = ed.App(title="Customers")


class CustomerInput(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    email: Annotated[str, Field(min_length=3, max_length=254)]


class Customer(BaseModel):
    id: int
    name: str
    email: str


class CustomerRepository(Protocol):
    def list(self) -> list[Customer]: ...
    def create(self, data: CustomerInput) -> Customer: ...
    def delete(self, customer_id: int) -> None: ...


def get_customers() -> CustomerRepository:
    # Supplied by application lifespan/dependency configuration.
    raise NotImplementedError


@app.page("/customers", title="Customers")
class CustomersPage(ed.Page):
    customers: CustomerRepository = ed.dependency(get_customers)

    def render(self) -> None:
        self.form(
            CustomerInput,
            action=self.create,
            submit_label="Create customer",
        )
        self.customer_list()

    @ed.fragment
    def customer_list(self) -> None:
        customers = self.customers.list()

        if not customers:
            self.empty("No customers yet")
            return

        for customer in customers:
            with self.card():
                self.subheader(customer.name)
                self.text(customer.email)
                self.button(
                    "Delete",
                    action=self.delete.bind(customer_id=customer.id),
                    variant="danger",
                    confirm=f"Delete {customer.name}?",
                )

    @ed.action
    def create(self, customer: CustomerInput) -> ed.Outcome:
        created = self.customers.create(customer)
        return ed.refresh(self.customer_list).toast(f"Created {created.name}")

    @ed.action(idempotency="required")
    def delete(self, customer_id: int) -> ed.Outcome:
        self.customers.delete(customer_id)
        return ed.refresh(self.customer_list).toast("Customer deleted")
```

### Conceptual Hedron lowering

```text
CustomerInput + self.form(...)
    -> Pydantic-owned validation schema
    -> Hedron type-driven FormBody/control compilation
    -> semantic labels, help, retained safe values, and error summary
    -> generated POST action with owning-page fallback

ed.dependency(get_customers)
    -> request-scoped FastAPI dependency descriptor
    -> resolved once per request and never during class registration/static explanation

@ed.action create(customer: CustomerInput)
    -> Hedron form command/action handle
    -> validated model passed to application code
    -> refresh customer_list and produce toast after success

self.delete.bind(customer_id=...)
    -> native bound ActionHandle input
    -> hidden input generated by a controlled binding plan

confirm=...
    -> progressive confirmation UI
    -> no authorization claim and no substitute for server checks
```

The example omits authentication policy only to keep the fixture focused. A production action must
be able to declare or inherit an ordinary FastAPI/Hedron authorization dependency. Edron must not
infer authorization from page visibility, a confirmation dialog, or Pydantic validation.

### Design pressure and proposed disposition

| Question | Proposed disposition |
|---|---|
| How are form controls chosen? | Conservatively from one Pydantic model, with explicit overrides for ambiguous fields. |
| Must an action repeat a URL? | No. Its stable internal path is generated from app/page/method identity. |
| What is the fallback after a native POST? | The owning page path, unless the action declares another safe local outcome. |
| How are action arguments supplied? | Typed `.bind(...)`; no arbitrary callback `args` or `kwargs`. |
| Is dependency state stored on the class? | No. `ed.dependency` is a descriptor resolved onto each fresh request instance. |
| Does confirmation make delete safe? | No. CSRF, authorization, idempotency, validation, and repository policy remain required independently. |
| Can page subclasses inherit registered actions implicitly? | No by default. Only methods declared on the registered class are exposed unless inheritance is explicitly designed and accepted later. |

### Acceptance sketch

- invalid form data never calls `CustomerRepository.create`;
- native and HTMX submissions share validation and CSRF behavior;
- validation errors focus the error summary and retain only safe submitted fields;
- `get_customers` resolves once within each request and is not shared across requests;
- create/delete refresh only the customer-list region;
- a forged or cross-app bound action is rejected;
- duplicate delete submission follows the declared idempotency policy;
- confirmation is keyboard accessible and has a functional no-JavaScript disposition; and
- route catalogs and `edron check` identify generated actions without exposing bound customer data.

## Golden application 4: durable report job

### User outcome

A user submits a report request, sees queued/running/succeeded/failed states, can request
cancellation, and downloads the result. Edron hides polling routes and status components but does
not pretend to provide a worker, queue, scheduler, result database, or deployment topology.

### Proposed Edron source

```python title="app.py"
from typing import Annotated

import edron as ed
from pydantic import BaseModel, Field

app = ed.App(title="Reports")


class ReportRequest(BaseModel):
    year: Annotated[int, Field(ge=2000, le=2100)]
    include_details: bool = False


def get_job_backend() -> ed.JobBackend:
    # Supplied by application lifespan/dependency configuration.
    raise NotImplementedError


def current_job_scope() -> ed.JobScope:
    # Derived from the authenticated request by application policy.
    raise NotImplementedError


def report_result(page: ed.Page, result: dict[str, str]) -> None:
    page.download_button(
        ed.download(result["download_id"]),
        label="Download report",
    )


reports = ed.JobFlow(
    name="annual-report",
    input_model=ReportRequest,
    job_type="build-annual-report",
    payload=lambda request: request.model_dump(mode="json"),
    backend=ed.dependency(get_job_backend),
    scope=current_job_scope,
    result=report_result,
)

app.include(reports)


@app.page("/reports", title="Annual report")
class ReportsPage(ed.Page):
    def render(self) -> None:
        self.job(
            reports,
            submit_label="Build report",
            show_cancel=True,
        )
```

An application-operated worker consumes `job_type="build-annual-report"`, validates the payload
again at its trust boundary, performs the work, and records bounded status/result data through the
configured Hedron `JobBackend`. That worker is intentionally outside this page file and outside
Edron's runtime responsibility.

### Conceptual Hedron lowering

```text
ed.JobFlow(...)
    -> Hedron TaskFlow over application-operated JobBackend
    -> generated typed submit form and POST command
    -> generated status, cancel, and result surfaces
    -> JobScope propagated to every submit/get/cancel observation

self.job(reports)
    -> initial task form/status composition
    -> Poll-based status observation through generated refreshable handle
    -> HTTP 202 + Retry-After while non-terminal
    -> terminal result, failure, expiry, or cancellation state

ed.download(download_id)
    -> authorized application download identifier
    -> never an arbitrary local filesystem path
```

Polling is the supported default. SSE or WebSocket observation may be an explicit experimental
integration but cannot change job authorization, transition, fallback, or terminal-state
correctness.

### Design pressure and proposed disposition

| Question | Proposed disposition |
|---|---|
| Does `@ed.job` run arbitrary work inside the web process? | No. The initial API uses a declarative `JobFlow` over an application-operated backend. |
| Does Edron ship a production worker? | No. It may ship an in-memory development backend with explicit single-process diagnostics. |
| What is the default live transport? | Bounded polling through existing Hedron job/status helpers. |
| Who owns job authorization? | The application supplies a scope/dependency; the same scope is required for submit, status, cancel, and result. |
| Can a result contain a filesystem path? | No. It contains an opaque authorized download identifier or bounded display value. |
| Can job configuration be hidden completely? | No. Backend and scope are security/operations decisions and remain explicit at app configuration. |

### Acceptance sketch

- submission validates before the backend is called;
- unsafe submission and cancellation require CSRF;
- status observation fails closed for missing or mismatched subject/tenant scope;
- polling stops on success, failure, cancellation, expiry, and unrecoverable error;
- a stale status response cannot replace a newer terminal state;
- the no-JavaScript path can submit and refresh status manually;
- multi-worker acceptance uses a durable backend rather than process memory;
- the development backend is labeled and refused by the production gate where required; and
- Edron documentation never claims to run or deploy the worker.

## Golden application 5: optional Plotly integration

### User outcome

A base Edron installation always provides first-party charts. A user who deliberately chooses
Plotly may install Plotly directly or use `edron[plotly]` as a shortcut. Application behavior is
based only on whether a compatible dependency is actually installed.

### Proposed Edron source

```python title="app.py"
import edron as ed

app = ed.App(title="Interactive chart")

ROWS = [
    {"month": "Jan", "revenue": 10},
    {"month": "Feb", "revenue": 14},
    {"month": "Mar", "revenue": 18},
]


@app.page("/", title="Interactive revenue")
class InteractiveRevenue(ed.Page):
    def render(self) -> None:
        self.plotly_chart(
            ROWS,
            x="month",
            y="revenue",
            mark="line",
            title="Monthly revenue",
        )
```

Either installation activates the same capability:

```bash
pip install edron "plotly>=5.18,<7"
```

```bash
pip install "edron[plotly]"
```

The equivalent `uv add` forms must also be documented by the runtime diagnostic.

### Missing dependency outcome

The module and page class remain importable without Plotly. The call fails at the feature boundary,
not during `import edron`:

```text
EdronOptionalDependencyError

plotly_chart() requires plotly>=5.18,<7, but Plotly is not installed.

Install the dependency directly:
    pip install "plotly>=5.18,<7"

Or use the Edron installation shortcut:
    pip install "edron[plotly]"
```

An incompatible installed version reports its discovered version and compatible range. An
installed package that fails internally during import retains its original cause and is not
misreported as absent.

### Conceptual Hedron lowering

```text
self.plotly_chart(...)
    -> lazy Edron capability check for distribution/import/version
    -> hedron-charts Plotly adapter
    -> explicit experimental/Supported maturity disposition from Edron inventory
    -> Hedron asset/CSP/HTMX lifecycle

edron[plotly]
    -> packaging metadata shortcut that installs the same direct dependency range
    -> no runtime flag, feature gate, or alternate code path
```

The base alternative remains available without an optional dependency:

```python
self.line_chart(ROWS, x="month", y="revenue", title="Monthly revenue")
```

### Design pressure and proposed disposition

| Question | Proposed disposition |
|---|---|
| Are optional feature methods conditionally defined? | No. They remain discoverable and type-checkable. Dependency checks are lazy. |
| Does runtime inspect which extra was selected? | No. Extras have installation-time meaning only. |
| May Edron install Plotly automatically? | No. Runtime environment mutation is forbidden. |
| Is a missing dependency an `ImportError`? | No. It is a structured Edron diagnostic with direct and shortcut installation commands. |
| Are all plotting backends installed by `edron`? | No. First-party charts are built in; third-party ecosystems remain direct optional dependencies. |
| May Edron silently fall back from `plotly_chart`? | No. An explicit backend request either works or explains the missing/incompatible capability. |

### Acceptance sketch

- `import edron` and application discovery succeed without Plotly;
- the feature call produces the structured missing-dependency diagnostic;
- direct compatible Plotly installation activates the feature;
- the `edron[plotly]` shortcut resolves the same supported range;
- incompatible-version and broken-import cases have distinct diagnostics;
- no dependency check imports or executes the page during static `edron check` analysis;
- chart assets remount after an HTMX swap and obey strict CSP; and
- the first-party `line_chart` equivalent passes in the clean base environment.

## Golden application 6: branded styling from simple to native

### User outcome

A user gives an application a coherent brand, applies familiar variants to ordinary controls,
defines one reusable presentation recipe, and retains normal CSS for a product-specific detail.
Edron-generated, first-party chart/data, and directly included Hedron components all consume the
same theme and cascade.

### Proposed Edron source

```python title="app.py"
import edron as ed
import hedron as h

brand = ed.theme(
    "acme",
    base="aurora",
    accent="#635bff",
    density="comfortable",
    geometry="soft",
    typography="system-sans",
    motion="calm",
).with_recipes(
    ed.StyleRecipe.surface(
        "kpi",
        appearance="raised",
        density="compact",
        padding="md",
    ),
)

app = ed.App(title="Acme operations", theme=brand)
app.styles("acme-dashboard", "styles/dashboard.css", scope="app")


@app.page("/", title="Operations overview")
class Operations(ed.Page):
    def render(self) -> None:
        with self.card(recipe="kpi"):
            self.metric("Successful runs", 128, delta="+12%")

        with self.style_scope(density="compact"):
            self.dataframe(
                [
                    {"pipeline": "Customers", "state": "Healthy"},
                    {"pipeline": "Invoices", "state": "Delayed"},
                ]
            )

        self.button("Run pipeline", action=self.run, variant="primary")
        self.button(
            "Delete history",
            action=self.delete,
            variant="danger",
            confirm="Delete all run history?",
        )

        self.include(
            h.Alert(
                "Native Hedron components use the same resolved theme.",
                tone="info",
            )
        )

    @ed.action
    def run(self) -> ed.Outcome:
        return ed.success("Pipeline submitted")

    @ed.action
    def delete(self) -> ed.Outcome:
        delete_history()
        return ed.success("History deleted")
```

The registered local stylesheet uses standard CSS and documented native hooks rather than a
Python property dictionary:

```css title="styles/dashboard.css"
h1 {
  max-inline-size: 20ch;
  text-wrap: balance;
}

[data-hedron-component="Card"] [data-hedron-part="header"] {
  border-block-end: 1px solid var(--hedron-color-border);
}

@media print {
  [data-hedron-component="Button"] {
    display: none;
  }
}
```

The exact public hook and token names are validated by Hedron's stylesheet contract. A private
class, unknown token, selector escaping the declared scope, or unsupported remote URL produces a
source-linked style diagnostic.

### Conceptual Hedron lowering

```text
ed.theme(...)
    -> native DesignSystem/ThemeSpec brand compilation
    -> coordinated light/dark semantic tokens and accessibility modes
    -> native validation report, provenance, fingerprint, and assets

ed.StyleRecipe.surface(...)
    -> the public Hedron StyleRecipe object by identity

variant="primary" / variant="danger"
    -> registry-derived native primary_action/destructive_action recipe
    -> presentation only; no mutation or confirmation semantics inferred

self.style_scope(...)
    -> native StyleScope/StyleContext subtree

app.styles(...)
    -> native application stylesheet registration
    -> scoped compiler, public-hook checks, cascade layer, manifest, CSP, source map

self.include(h.Alert(...))
    -> original native component in the same theme/cascade
```

### Design pressure and proposed disposition

| Question | Proposed disposition |
|---|---|
| Must a user learn a token graph to set one brand color? | No. `ed.theme(...)` compiles a safe coordinated native design from bounded choices. |
| Is `ed.theme(...)` a new theme object? | No. It returns the canonical native Hedron styling value selected at Stage 0. |
| Should every component accept arbitrary CSS dictionaries? | No. Common intent uses finite variants/native props; advanced intent uses CSS. |
| What does `variant="danger"` mean? | Presentation only. The action still needs explicit unsafe-method, authorization, confirmation, and idempotency policy. |
| Can recipes change application behavior or state? | No. They are presentation-only native values. |
| Can an app use plain CSS? | Yes. Registered local CSS is the powerful path and participates in native scope, hooks, assets, CSP, source maps, and upgrade checks. |
| Do native Hedron components look foreign inside Edron? | No. They consume the exact same resolved theme, scope, tokens, and cascade. |
| Do third-party charts automatically inherit full theme support? | Only when their adapter declares and proves it; otherwise the limitation is explicit. |

### Acceptance sketch

- the default, built-in-string, and `ed.theme(...)` paths all resolve through one native registry;
- `ed.StyleRecipe is hedron.StyleRecipe`, or an equally strict public identity contract selected at
  Stage 0, and no parallel Edron recipe registry exists;
- variant mappings are derived from frozen native recipe metadata and invalid family/variant pairs
  fail with valid choices;
- explicit native component props override recipe defaults and the style explanation identifies
  both sources;
- the scoped data table inherits compact density across initial render and HTMX replacement;
- the included native Alert receives the same light/dark, brand, accessibility-mode, and print
  behavior as Edron-generated content;
- local CSS is fingerprinted once, survives page and fragment asset planning, and passes strict CSP;
- private-hook, path escape, remote URL, unknown token, and request-derived CSS probes fail;
- keyboard focus, contrast, forced colors, reduced motion, zoom/reflow, RTL, print, and narrow-width
  fixtures pass; and
- `edron style explain` reports native tokens, recipes, hooks, winning sources, assets, adjustments,
  compatibility, and Edron source locations without invoking page or action code.

## Cross-application lowering invariants

Every accepted golden application must preserve these Hedron authorities.

| Concern | Required authority |
|---|---|
| Component rendering and escaping | Hedron renderer and component model |
| Pages and navigation | Hedron screen/page routes and handles |
| Partial updates | Hedron fragment handles, regions, target allowlists, and HTMX responses |
| Mutations | Hedron actions/form commands, CSRF, effects, outcomes, and idempotency policy |
| Typed boundaries | Pydantic plus Hedron type-driven binding/form schemas |
| Tables and editing | `hedron-data` |
| Charts | `hedron-charts` and its asset lifecycle |
| Maps | `hedron-maps` |
| Jobs | Hedron `JobBackend`, `TaskFlow`, status helpers, and polling |
| Dependencies | FastAPI/Hedron dependency lifecycle |
| Assets and CSP | Hedron registry, build manifest, and security policy |
| Themes, tokens, recipes, scopes, CSS, and cascade | Hedron presentation/styling registry, compiler, assets, and public hook manifest |
| Diagnostics and explanation | Hedron catalogs/diagnostics plus Edron source mapping |

Edron may infer a simpler declaration and provide friendlier names, but it may not create a
parallel authority for any row in this table. If the required authority is incomplete, the plan
may add it to Hedron before implementing the corresponding Edron surface.

## Proposed 0.1 surface exercised by the fixtures

| Surface | Golden application |
|---|---|
| `App`, `Page`, `@app.page`, `render` | All |
| Text, alerts, empty state, headings | Hello, CRUD |
| Sidebar, columns, cards | Dashboard, CRUD |
| Selectbox and slider | Dashboard |
| Metric, dataframe, first-party chart | Dashboard |
| `@ed.fragment`, `updates`, `ed.refresh` | Dashboard, CRUD |
| `@ed.action`, action binding, outcomes | Dashboard, CRUD |
| Pydantic-generated form | CRUD, jobs |
| Request-scoped dependency descriptor | CRUD, jobs |
| Idempotency and confirmation | CRUD |
| JobFlow and polling | Jobs |
| Optional capability diagnostics | Plotly |
| Native Hedron lowering and escape hatch | Cross-application invariant |
| Theme, variants, recipes, scopes, local CSS, and style tooling | Styling |

## Public contract decisions exposed by the fixtures

The [Edron public API contract](../api/EDRON.md) resolves these design pressures for 0.1. They remain
draft decisions until RFC-0094 and its Stage 0 packet are accepted.

1. **Visible page title:** `title=` emits the document title and default `h1`; `show_title=False`
   suppresses only the generated heading.
2. **Output collection:** display methods and fragment mounts append native output and return
   `None`; layouts return request-local containers; native objects use `include`.
3. **Fragment call behavior:** the descriptor binds/mounts and materializes once during the initial
   page request; a fragment request creates a fresh instance and invokes only the fragment.
4. **Input-to-fragment binding:** explicit `name=` values and typed parameters form coherent
   connected GET filter groups; ambiguity requires an explicit `filters(...)` scope.
5. **Action descriptors:** actions are values, render-phase calls fail, `.bind(...)` accepts only
   named application parameters, inherited decorated methods are not exposed, and sync/async are
   supported at native boundaries.
6. **Forms:** one Pydantic model is authoritative; compatible native control overrides are explicit;
   nested forms and guessed model/result conversions are rejected.
7. **Dependency descriptors:** `ed.dependency(...)` is request-scoped native DI with per-request
   caching, native test overrides, static explanation, cleanup, and no client shadowing.
8. **Native fallback:** action defaults to its owning page; safe filters use that page with the same
   query; unsafe method and CSRF meaning are preserved.
9. **Job facade:** `JobFlow` is in 0.1 but remains blocked on native `TaskFlow` enablement and never
   provides a production worker.
10. **Capability registry:** actual installed distributions activate lazy adapters; direct and
    extra commands are equivalent; missing, incompatible, and broken imports are distinct.
11. **Public vocabulary:** explicit display/input methods, `include`, `app.hedron`, and
    `app.native(...)` are canonical; `display`, `write`, `self.hedron`, and magic dispatch are absent.
12. **Configuration defaults:** `App` uses the native standard security profile, exposes ASGI,
    includes Uvicorn for `edron run`, and delegates advanced host configuration to `app.hedron`.
13. **Upstream work:** every missing native foundation requires independent Hedron ownership before
    Edron consumes it.
14. **Styling facade:** `ed.theme(...)` returns native `DesignSystem`; selected styling types are
    identity re-exports; finite variants, native scopes/recipes, and registered CSS share one
    authority.

## Stage 0 exit gate

The golden application packet is ready to feed an accepted RFC only when:

- every proposed symbol has a disposition in the Edron surface inventory;
- each lowering arrow points to one existing Hedron authority or an explicitly planned upstream
  Hedron capability with separate ownership;
- security, accessibility, native fallback, and concurrent-request behavior are stated for every
  interaction;
- the clean base and optional-dependency installation matrices are fixed;
- the six examples type-check under the proposed public signatures; and
- unresolved decisions are either selected in the RFC or explicitly deferred outside Edron 0.1.
