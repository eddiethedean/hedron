---
description: Build, secure, test, and operate production-minded Edron applications.
search:
  boost: 1.7
---

# Edron user guide

Edron is a typed, server-rendered Python facade over one native Hedron application. It is designed
for dashboards, internal tools, data workspaces, and workflows that should remain useful with
ordinary HTTP and without a separate frontend build system.

This guide targets the stable Edron and Hedron `1.0.x` train (`>=1.0.0,<1.1`). Pin the minor
train, keep the supported surface explicit, and treat undocumented imports as internal.

## The operating model

Four rules explain most Edron design decisions:

1. **One application authority.** `edron.App` owns exactly one native `hedron.Hedron` application.
   Use `app.native` or `app.hedron` when a native contract is the right level of abstraction.
2. **Fresh request-local pages.** Edron creates a fresh `Page` instance for each page, fragment, or
   action request. Do not put user state, database sessions, or mutable process state on a page.
3. **Server-first behavior.** A page should render useful HTML through ordinary HTTP. HTMX-style
   enhancement is an optimization, not the only path to the result.
4. **Application-owned boundaries.** Authentication, authorization, transactions, persistence,
   audit records, secrets, queues, and durable backends remain application or platform owned.

Edron does not provide a Streamlit rerun runtime, `import edron as st`, a global session dictionary,
or a second renderer, router, state store, job queue, or security authority.

## 1. Install and create an application

Use a clean environment and pin the Edron minor train:

```console
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "edron>=1.0.0,<1.1"
```

On Windows, activate `.venv\\Scripts\\activate` instead. Verify the interpreter that will run the
server:

```console
python -c "import edron; print(edron.__version__)"
```

For a teaching scaffold:

```console
edron new sales-app --template minimal
cd sales-app
edron run app:app --reload
```

The scaffold is intentionally small. A normal application commonly contains:

```text
sales-app/
├── app.py                 # application construction and route registration
├── src/                   # domain, services, and adapters as the app grows
├── tests/                 # unit, HTTP, security, and browser-contract tests
├── .hedron/build/         # generated production assets; deploy with the app
├── pyproject.toml         # pinned package and runtime dependencies
└── uv.lock or requirements.txt
```

## 2. Build a first page

The conventional import is `import edron as ed`. A page class must define `render()` directly and
must not define `__init__`:

```python title="app.py"
import edron as ed

app = ed.App(title="Sales dashboard", security="standard")


@app.page("/", title="Sales dashboard")
class Home(ed.Page):
    def render(self) -> None:
        self.text("A server-rendered page with an accessible HTML fallback.")
        self.metric("Orders", 128, delta="+12")
```

Run it locally:

```console
edron run app:app --reload
```

For a function-shaped page, use the deliberately limited `function_page` form. It receives only
declared request parameters and may return a native node; use a class page when you need Edron page
helpers or related fragments and actions:

```python
from hedron import Text


@app.function_page("/health-summary", title="Health summary")
def health_summary() -> Text:
    return Text("All systems nominal")
```

Use class pages when the route will gain fragments, actions, dependencies, or related surfaces.

## 3. Compose layouts and inputs

Composition is request-local and explicit. Layout declarations are bounded and lower to native
Hedron layout nodes:

```python
@app.page("/filters", title="Filters")
class Filters(ed.Page):
    def render(self) -> None:
        region = self.selectbox(
            "Region",
            ("All", "North", "South"),
            name="region",
            default="All",
        )
        query = self.text_input(
            "Search",
            name="q",
            placeholder="Customer or order number",
        )

        with self.layout("grid", columns=2, gap="1rem") as body:
            body.metric("Region", region)
            body.metric("Query", query or "Any")
```

Useful page methods include `heading`, `text`, `markdown`, `code`, `metric`, `table`, `text_input`,
`number_input`, `selectbox`, `multiselect`, `slider`, `checkbox`, `date_input`, `card`, `container`,
`layout`, `columns`, `tabs`, `expander`, `image`, `audio`, `video`, and `download_button`.

For media, provide meaningful alternative text or captions. For user-controlled text, use a safe
text method; do not treat database, tenant, upload, or prompt content as trusted HTML or executable
template source.

## 4. Add refreshable fragments and actions

Fragments are independently addressable server-rendered views. Actions are unsafe HTTP commands and
must be explicit. The following pattern keeps the page useful before enhancement and lets HTMX
replace only the summary panel:

```python
import edron as ed

app = ed.App(title="Sales", security="standard")


def load_sales(region: str) -> list[dict[str, object]]:
    # Replace with an application-owned query/service.
    return [{"region": region, "orders": 128}]


@app.page("/", title="Sales")
class Sales(ed.Page):
    def render(self) -> None:
        region = self.selectbox(
            "Region",
            ("All", "North", "South"),
            name="region",
            default="All",
        )
        self.summary(region=region)
        self.button("Refresh summary", action=self.refresh)

    @ed.fragment
    def summary(self, region: str = "All") -> None:
        self.heading("Summary", level=3)
        self.table(load_sales(region))

    @ed.action
    def refresh(self) -> ed.Outcome:
        return ed.refresh(self.summary)
```

Important interaction rules:

- Bind only declared action arguments: `self.refresh.bind(...)` rejects unknown values.
- Use `ed.success("Saved")` for a bounded action result and `ed.refresh(fragment)` for refresh
  intent. Do not call a bound action as an ordinary Python function.
- Keep write operations on `POST`, `PUT`, `PATCH`, or `DELETE`; Edron rejects safe action methods.
- Keep authorization and validation in the action or its dependencies. A button is not an
  authorization boundary.
- For a form, use `self.form(Model, action=self.save)` with a typed Pydantic model where appropriate.
- Test both the full-page response and the fragment response. The fragment is not a separate data
  authority; it is another projection of the same application code.

For browser-local enhancement, use the native Hedron 0.67 interaction algebra and planner through
Edron’s thin exports. Local effects are disposable; request effects remain server-owned:

```python
toggle = ed.Interaction.local("toggle-panel", state_keys=("open",))
save = ed.Interaction.request("sales-save", target="#sales", swap="outerHTML")
save_and_close = ed.Interaction.combined(
    "close-panel", "sales-save", state_keys=("open",), target="#sales"
)
app.interaction(toggle)
plan = ed.browser_plan(toggle.demands())
```

`ed.browser_plan()` is demand-driven. An empty plan emits no Alpine assets; a demanded plan owns
the local CSP-safe Alpine runtime, plugin assets, and HTMX bridge through Hedron. Do not add Alpine
fetch calls, remote scripts, page-level plugin tags, or a second state/request authority. Use
`ed.browser_closure()` when a page has statically reachable fragments.

## 5. Inject dependencies and own resources

Use typed dependencies for request or application services instead of constructing them inside page
methods:

```python
from collections.abc import Callable

import edron as ed


def current_user() -> dict[str, str]:
    # Replace with the host's authenticated principal lookup.
    return {"id": "demo", "role": "analyst"}


user = ed.dependency(current_user)
app = ed.App(title="Operations", security="standard")


@app.page("/operations", title="Operations")
class Operations(ed.Page):
    principal = user

    def render(self) -> None:
        self.text(f"Signed in as {self.principal['id']}")
```

Register lazy resources at the application boundary. The factory is not resolved during import or
page registration, and `secret_refs` contains opaque names rather than secret values:

```python
import os

import edron as ed

app = ed.App(title="Orders", security="standard")


def open_database() -> object:
    return make_database(os.environ["DATABASE_URL"])


database = app.resource(
    "database",
    open_database,
    kind="sqlalchemy",
    scope="application",
    secret_refs={"dsn": "DATABASE_URL"},
)
```

Application-scoped resources belong to the host lifespan. Request-scoped resources must be safe to
close after the request. The application owns transactions, pooling, retries, and health semantics.

## 6. Add bounded data workspaces

Use explicit columns and allowlists. Edron does not own rows, authorization, transactions, or audit
storage:

```python
import edron as ed

source = ed.DataSource.in_memory(
    [
        {"id": "1", "name": "Northwind", "status": "open"},
        {"id": "2", "name": "Contoso", "status": "closed"},
    ],
    key_field="id",
    columns=(
        ed.Column("id", read_only=True, sortable=True),
        ed.Column("name", sortable=True, filterable=True),
        ed.Column("status", sortable=True, filterable=True),
    ),
    sort_fields=("id", "name", "status"),
    filter_fields=("name", "status"),
)

workspace = ed.DataWorkspace(
    "customers",
    source=source,
    columns=(
        ed.Column("id", read_only=True, sortable=True),
        ed.Column("name", sortable=True, filterable=True),
        ed.Column("status", sortable=True, filterable=True),
    ),
    page_size=25,
    max_page_size=100,
)


@app.page("/customers", title="Customers")
class Customers(ed.Page):
    def render(self) -> None:
        self.data_workspace(workspace, caption="Customer list")
```

For editing, provide an `EditPolicy` with explicit writable fields and an authorization hook, then
register the save route with `app.data_workspace(workspace)`. Enable inserts and deletes separately.
Use optimistic row versions where the source supports them, and send audit metadata to an
application-owned audit sink. Never mark secret, hidden, or authorization fields as writable.

For database-backed workspaces, use `DataSource.sqlalchemy(...)` and keep session creation and
commit/rollback behavior in the application-owned session factory and change applier.

## 7. Use charts, maps, and downloads safely

Visualization and media methods lower to native capability packages. Install optional packages only
when the application uses them, and provide an accessible alternative:

```python
@app.page("/revenue", title="Revenue")
class Revenue(ed.Page):
    def render(self) -> None:
        rows = load_revenue()
        self.line_chart(
            rows,
            x="month",
            y="revenue",
            title="Monthly revenue",
            description="Revenue in USD by month.",
        )
        self.text("The table below is the accessible data alternative.")
        self.table(rows)
```

Charts, maps, and optional adapters remain capability-labeled. A missing or incompatible optional
package should produce a clear capability error during setup or a documented fallback, not a runtime
package installation. Downloads must have an application-owned authorization decision and a bounded
filename/media type; never expose an arbitrary filesystem path as a download reference.

## 8. Cache recomputable work and run durable jobs

`cache_data` is for bounded, recomputable values. It is not a session, lock, authorization cache, or
durable source of truth:

```python
@ed.cache_data(
    ttl=60,
    scope="tenant",
    max_entries=256,
    version="sales-v2",
    vary_on=("tenant_id",),
)
def sales_summary(tenant_id: str) -> dict[str, int]:
    return query_sales_summary(tenant_id)
```

Invalidate deliberately after writes:

```python
sales_summary.invalidate(tenant_id)
# or, after a schema/data change:
sales_summary.invalidate_all()
```

For work that must outlive a request, compose a native-backed `JobFlow` with an explicit backend:

```python
from pydantic import BaseModel


class ExportRequest(BaseModel):
    tenant_id: str


export_job = ed.JobFlow(
    name="customer-export",
    input_model=ExportRequest,
    job_type="customer-export",
    payload=lambda request: request.model_dump(),
    scope=ed.JobScope.application,
    result=run_customer_export,
    backend=job_backend,
)
```

The backend, retry policy, idempotency behavior, authorization, result retention, and polling route
must be reviewed for the application. Process-local jobs are not durable across restarts or workers.
Prefer bounded polling for production status UX; live transports require separate host and proxy
evidence.

## 9. Secure the application

Start with the standard security profile and move to strict when the application has explicit asset
and CSP coverage:

```python
import os

import edron as ed

is_production = os.environ.get("HEDRON_ENV", "").lower() in {"prod", "production"}
session_secret = os.environ.get("HEDRON_SESSION_SECRET")
if is_production and not session_secret:
    raise RuntimeError("HEDRON_SESSION_SECRET is required in production")

app = ed.App(
    title="Operations",
    security="strict",
    production=is_production,
    session_secret=session_secret,
)
```

Production requirements:

- Inject a strong session secret from the platform secret store. Never commit it, bake it into an
  image, or print it in diagnostics.
- Serve through HTTPS so session and CSRF cookies can be `Secure`.
- Keep CSRF enabled for unsafe methods. A safe GET seeds the token; the client sends the matching
  `X-CSRF-Token` header or form field.
- Trust only explicitly configured proxy addresses or bounded CIDRs. Never trust arbitrary forwarded
  headers or the inbound `Host` header.
- Use application authentication and authorization for every protected page, action, download,
  workspace mutation, and job status lookup.
- Keep `explorer="off"` in production unless the host supplies real authentication and the exposure
  has been reviewed.
- Treat templates, JavaScript, CSS, and HTML passed to trusted rendering APIs as application source.
  Escape or validate tenant and user content before it reaches a page.

See [Security](security.md), [Threat model](threat-model.md), and [Accessibility](accessibility.md)
for the native policies that Edron delegates to.

## 10. Test the application in layers

Use the smallest test that proves the contract:

1. **Pure unit tests** for domain services, authorization, validation, and data transformations.
2. **Render tests** for page structure, accessible names, safe URLs, alternative text, and bounded
   payloads.
3. **HTTP tests** for full pages, fragments, CSRF, redirects, downloads, error status, and ordinary
   non-JavaScript behavior.
4. **Browser tests** for keyboard/focus behavior, mounted paths, progressive enhancement, and the
   real reverse proxy or host.
5. **Release tests** for package isolation, build manifests, artifact hashes, diagnostics, and
   upgrade/rollback behavior.

Keep the app importable in a test environment and make external dependencies replaceable with
explicit dependencies or test doubles. Do not test by mutating process-global state that another
test might reuse.

For Edron-specific checks:

```console
edron check app.py
edron explain app:app --format json
edron doctor app:app --format json
```

`edron check` parses source without importing it. `explain`, `doctor`, and registered application
checks inspect bounded metadata; they do not execute page callbacks as a substitute for tests.

## 11. Build and deploy

Build assets before enabling production mode:

```console
hedron build
edron deploy-check --profile single-process \
  --build-dir .hedron/build \
  --secret-source platform://production/edron-session-secret
```

For a reverse-proxy mount:

```console
edron deploy-check --profile reverse-proxy \
  --root-path /sales \
  --build-dir .hedron/build \
  --external-url https://apps.example.test/sales \
  --trust-proxy 10.0.0.10 \
  --secret-source platform://production/edron-session-secret \
  --format json
```

Start the ASGI application with the host’s normal process mechanism:

```console
uvicorn app:app --host 127.0.0.1 --port 8000
```

For containers or orchestrators, bind externally only at the platform boundary, keep the generated
`.hedron/build/manifest.json` in the image, and run the check in CI or as a release preflight. More
than one worker requires verified shared state and job backends:

```console
edron deploy-check --profile orchestrated --workers 2 \
  --state-backend shared \
  --job-backend shared \
  --build-dir .hedron/build \
  --secret-source platform://production/edron-session-secret
```

`deploy-check` validates declared assumptions; it does not provision infrastructure, test a remote
database, discover a public URL, install packages, or import arbitrary application callbacks.

Read the [Edron deployment guide](edron-deployment.md) for profile semantics and the [Hedron ship
checklist](ship.md) for proxy, host, and multi-worker details.

## 12. Inspect and diagnose a release

Use deterministic reports as release artifacts:

```console
edron check app.py --format sarif > edron-check.sarif
edron explain app:app --format json > edron-explain.json
edron doctor app:app --profile reverse-proxy --format json > edron-doctor.json
```

In Python, the corresponding app-level reports are:

```python
manifest = app.manifest()
conformance = app.conformance()
operations = app.operations()
deployment = app.deployment("single-process")
```

Retain the package lockfile, build manifest, artifact hashes, supported Python/Hedron versions,
report schemas, and exact commands used to produce the evidence. Reports are bounded and redact
secret-shaped values; they are not a certification of the application’s business logic or cloud
configuration.

## 13. Upgrade and rollback

Treat an Edron upgrade as an application release:

1. Review the [compatibility policy](../COMPATIBILITY.md) and pin one compatible Edron/Hedron train.
2. Create a clean environment and install the lockfile exactly.
3. Run source checks, unit/HTTP/browser tests, `hedron build`, and `edron deploy-check`.
4. Rehearse one full-page request, one fragment, one CSRF-protected action, one download, and one
   data/job path through the real proxy mount.
5. Promote the immutable application artifact and retain the previous artifact and lockfile.
6. Roll back application code, generated assets, and package pins together if startup or smoke checks
   fail.

Edron does not reverse database migrations, rotate secrets, cancel external side effects, reclaim
user files, or undo already-enqueued work. Those actions require an application-owned runbook.

For the current release boundary, see [Edron 1.0 acceptance](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_100.md) and the
[Edron roadmap](../EDRON_ROADMAP.md).

## 14. Migrate from Streamlit

Migration is static and review-first:

```console
edron migrate streamlit app.py --out migrated-app
```

The migration output is a fresh project, report, and source map. It does not execute the source or
overwrite it. Review every finding, especially global state, callbacks, caching, file downloads,
authentication, and data mutation. Replace implicit Streamlit behavior with explicit Edron owners:

| Streamlit concern | Edron direction |
|---|---|
| `st.write` | `Page.text`, `markdown`, `table`, or a native component |
| `st.session_state` | Explicit dependency, signed/session authority, or application persistence |
| `st.cache_data` | `ed.cache_data` with scope, TTL, version, and invalidation |
| Button callback | `@ed.action` with authorization, validation, and an explicit outcome |
| Long work | Native-backed `JobFlow` with a reviewed backend and bounded polling |
| Page rerun | A full page request or an explicit `@ed.fragment` refresh |

Do not seek one-for-one behavioral emulation. Preserve the user outcome while making state,
authorization, persistence, and request boundaries reviewable.

## Troubleshooting

| Symptom | First checks |
|---|---|
| `ModuleNotFoundError: edron` | Confirm `python` and `uvicorn` are from the same environment; print `edron.__version__`. |
| `edron: command not found` | Run `python -m edron ...` or activate the environment containing the console script. |
| Production check rejects startup | Run `hedron build`; verify `.hedron/build/manifest.json`, the profile, and the runtime secret source. |
| Blank page or missing CSS | Forward `/hedron-static/` and `/hedron-assets/` unchanged; verify the root path and build directory. |
| CSRF `403` | GET the page first, preserve the CSRF cookie, and send the matching `X-CSRF-Token` on unsafe requests. |
| Fragment `403` | Use the registered fragment handle and declared target; do not invent an arbitrary `HX-Target`. |
| Multi-worker warning | Use one worker or prove shared state and job backends; process-local resources are not durable. |
| Missing optional capability | Install the direct optional dependency in the lockfile; Edron never installs packages at runtime. |
| Changes do not appear | Rebuild assets, invalidate the relevant cache, and verify the deployed artifact contains the new manifest. |

## Next references

- [Edron deployment guide](edron-deployment.md)
- [Edron 1.0 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_100.md)
- [Edron 0.8 → 0.9 upgrade fixtures](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/upgrade-fixtures-09.md)
- [Edron packaging and compatibility](../api/EDRON_PACKAGING.md) · [Compatibility policy](../COMPATIBILITY.md)
- [Security](security.md) · [Accessibility](accessibility.md) · [Test your UI](testing.md)
- [Edron API contract](../api/EDRON.md) · [Edron roadmap](../EDRON_ROADMAP.md)
