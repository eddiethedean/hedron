# Edron

[![CI](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/edron.svg)](https://pypi.org/project/edron/)
[![Python versions](https://img.shields.io/pypi/pyversions/edron.svg)](https://pypi.org/project/edron/)
[![License](https://img.shields.io/github/license/eddiethedean/hedron.svg)](https://github.com/eddiethedean/hedron/blob/main/packages/edron/LICENSE)
[![Status: Beta](https://img.shields.io/badge/status-beta-orange.svg)](https://github.com/eddiethedean/hedron)

Build polished, server-rendered Python apps with a small, explicit API. The current Edron train is
`0.9.x`, built on Hedron `0.67.0`.

Edron keeps the first page simple and gives the same codebase room to grow into dashboards,
internal tools, data workspaces, long-running jobs, and reusable feature packages. You write
ordinary Python, run one command, and get accessible HTML with progressive enhancement—without
maintaining a separate frontend application or learning a callback-heavy UI model.

For existing Streamlit projects, `edron migrate streamlit app.py --out migrated-app` produces a
fresh Edron project, deterministic review report, and source map. The migration is static and
review-first: source files are never executed or overwritten, and uncertain behavior is called out
as a finding or TODO.

## A first page in minutes

Install Edron, create `app.py`, and start the development server:

```console
python -m pip install "edron>=0.9,<0.10" "hedron>=0.67.0,<0.68" "hedron-data>=0.67.0,<0.68"
edron run app:app --reload
```

```python
import edron as ed

app = ed.App(title="Hello Edron")


@app.page("/", title="Hello")
class Home(ed.Page):
    def render(self) -> None:
        self.heading("Hello, Edron")
        self.text("A small Python API for useful web applications.")
```

That is the whole application. Add a route, compose a layout, or wire an action when you need
it—there is no generated frontend project to keep in sync.

For a guided starting point, use a teaching scaffold:

```console
edron new my-app --template minimal
cd my-app
edron run app:app --reload
```

## Why developers reach for Edron

- **Python all the way down.** Pages, components, actions, forms, data, and jobs use familiar
  functions, classes, and type hints.
- **A fast path and an escape hatch.** Start with a handful of readable Edron primitives. Keep
  full control of the underlying application when an advanced integration needs it.
- **Server-first by default.** HTML is useful on its own; HTMX-style enhancement adds smooth
  interactions without making JavaScript a requirement.
- **Batteries included for real work.** Compose navigation and layouts, render charts and media,
  build bounded data tables and editors, manage resources and caching, and expose durable jobs.
- **Inspectable instead of magical.** `edron check`, `edron explain`, and `edron doctor` make
  registration, dependencies, capabilities, and deployment facts visible before production.
- **Easy to test and review.** Explicit routes, typed inputs, bounded payloads, and deterministic
  manifests keep behavior straightforward to assert in unit tests and code review.

## A small API that scales

The same page vocabulary works for a simple screen or a complete workflow:

```python
import edron as ed

app = ed.App(title="Sales")


@app.page("/sales", title="Sales")
class Sales(ed.Page):
    def render(self) -> None:
        self.heading("Sales overview")
        with self.layout(ed.layout("grid", columns=2)) as body:
            body.text("A layout is just Python composition.")
```

Common building blocks include:

| Need | Edron API |
| --- | --- |
| Pages and reusable UI | `Page`, `@app.page`, `fragment`, `inherit`, `expose` |
| Navigation and layout | `navigation_target`, `layout`, `NavLink`-compatible targets |
| Forms and interactions | typed `action`, `fragment`, `Outcome`, `refresh`, `success` |
| Tables and editing | `DataSource`, `DataWorkspace`, `Column`, `EditPolicy` |
| Charts and media | `chart`, `map`, `image`, `audio`, `video` |
| Resources and performance | `resource`, `dependency`, `cache_data` |
| Long-running work | `JobFlow`, `JobBackend`, status polling/events |
| Reusable app features | `feature_package`, `include_package`, capability promotion |

## Data, resources, and jobs stay explicit

Edron makes application boundaries visible instead of hiding them in global state. For example,
resources are lazy and app-owned, cache policy is declared beside the function it protects, and
data editing is deny-by-default:

```python
db = app.resource("database", create_database, secret_refs={"dsn": "DATABASE_URL"})


@ed.cache_data(ttl=60, scope="tenant", vary_on=("tenant_id",))
def load_summary(tenant_id: str) -> dict[str, int]:
    return query_summary(db, tenant_id)
```

Use `DataWorkspace` for bounded paging, filtering, sorting, selection, CSV export, and typed edit
intents. Use `JobFlow` when work must outlive a request. Your application still owns the database
session, transaction, authorization, persistence, and audit decisions.

## Tooling that helps before deployment

```console
# Check source without importing application code
edron check app.py

# Inspect registered pages and surfaces
edron explain app:app

# Check installed required and optional capabilities
edron doctor

# Validate a deployment profile without importing application code
edron deploy-check --profile reverse-proxy --format json
```

For CI, `edron check --format sarif` produces review-friendly diagnostics. Applications can also
expose deterministic `app.manifest()` and `app.conformance()` reports for release checks.

## Installation and optional integrations

Edron supports Python 3.11–3.14. Install only what your application needs:

```console
python -m pip install edron
```

Optional extras are available for pandas, Polars, PyArrow, Plotly, Altair, Matplotlib, and
SQLAlchemy (for example, `pip install "edron[polars,sqlalchemy]"`).

Read the [getting started guide](https://hedron.readthedocs.io/en/latest/getting-started/), browse
the [API guides](https://hedron.readthedocs.io/en/latest/api/), or see the
[Edron user guide](https://hedron.readthedocs.io/en/latest/guides/edron-user-guide/), the
[Edron roadmap](https://github.com/eddiethedean/hedron/blob/main/docs/EDRON_ROADMAP.md) and
[deployment guide](https://github.com/eddiethedean/hedron/blob/main/docs/guides/edron-deployment.md).

## How Edron fits in

Edron is the authoring layer: it gives application developers a friendly, typed vocabulary and
keeps the important boundaries explicit. A mature native web engine handles the lower-level
rendering, routing, interaction, styling, and security work underneath. Most applications never
need to think about that implementation detail; when they do, the exact native application remains
available through `app.native` / `app.hedron` and `Page.include()`.

Edron is currently a **Beta** API line. Feedback, issues, and contributions are welcome in the
[Hedron repository](https://github.com/eddiethedean/hedron).
