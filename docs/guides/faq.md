# FAQ

## Which version should I install?

```bash
pip install "hedron>=0.23.0,<0.24"
# or
uv add "hedron>=0.23.0,<0.24"
```

That is the current published line (`v0.23.0`). Package maturity is **Beta** — see
[How to read](../getting-started/how-to-read.md). Pin with an upper bound:
`hedron>=0.23.0,<0.24`. Using `>=0.22.0` alone can resolve a future **0.23+**
breaking train. See [What’s ready today](whats-ready.md) and the
[public roadmap](roadmap.md).

**How is this different from Streamlit or FastHTML?** See [Why Hedron](why-hedron.md).

For curated extras (`hedron-extras`), install `hedron[extras]>=0.23.0,<0.24`.
**Auto** (inspectable object rendering built into `hedron` — no extra) is included.
For DataTable/DataEditor, install `hedron[data]>=0.23.0,<0.24`. For charts, install
`hedron[charts]>=0.1.0,<0.2` (Alpha). For Flask/Django adapters:

```bash
pip install "hedron-flask>=0.23.0,<0.24"
pip install "hedron-django>=0.23.0,<0.24"   # requires Django >=5.2,<6
```

## Do I need Node.js?

No. Hedron does not require npm or a JavaScript bundler for development or production.

## What is HTMX?

A small browser library that swaps server HTML into page regions using attributes like
`hx-get` / `hx-target`. Hedron uses it for fragment updates — see
[What is HTMX (for Hedron)](../getting-started/what-is-htmx.md).

## Why is FastAPI pinned so tightly?

Hedron’s Supported matrix tests FastAPI `>=0.141.1,<0.142` (and Pydantic Supported
`>=2.13.4,<2.14`; declared wider). Shared data-science envs with older FastAPI often
fail to resolve — use a **clean venv**. Details: [Compatibility](../COMPATIBILITY.md).

## Refresh status clicked but nothing changed

Confirm you are on the **running app** (`uvicorn`, usually
[http://127.0.0.1:8000](http://127.0.0.1:8000)), not only a docs Demo tab (those are
simulations). Check the browser network tab: fragment requests need `HX-Request` and a
matching `HX-Target`. A wrong target returns **403**. See
[Troubleshooting](troubleshooting.md#htmx-403-on-fragment-request) and
[HTMX interactions](htmx-interactions.md).

## First POST returns 403

Built-in `security="standard"` validates CSRF on unsafe methods. Load a GET page first
so the cookie/context is seeded, and include `CsrfField()` (or a matching
`csrf_token`) in the form. See [Minimal form POST](minimal-form.md) and
[Troubleshooting](troubleshooting.md#csrf-403-on-post-fastapi-flask).

## `api.mount` or `HedronRouter`?

For an **existing** FastAPI app, prefer `HedronRouter` + `api.include_router(ui)` and
`mount_hedron_static` — [Plain FastAPI](plain-fastapi.md). Mounting a full `Hedron()`
sub-app with `api.mount(...)` is an alternate when you want the facade’s middleware
([Mount](../api/MOUNT.md)). New apps should start with `hedron new` / `Hedron()`.

## Do I need Redis?

Not for Hello, HTMX refresh, or a single-process notes demo. Use a shared
`JobBackend` (Redis / Celery / RQ) when **multiple workers** must see the same job
status — [Jobs](../api/JOBS.md) · [Celery / RQ](jobs-celery-rq.md).

## Is Hedron production-ready for internal admin?

For pinned **Supported** CRUD/admin/forms on FastAPI (and Flask/Django adapters), yes
with eyes open: packages are **Beta**, pin `>=0.23.0,<0.24`, prefer polling for live
status, and read [What’s ready](whats-ready.md). There is no vendor SLA or scheduled
1.0. Use the [PoC checklist](evaluate.md#poc-checklist) on [Evaluate](evaluate.md).

## How did CSRF forms change in 0.22?

Prefer `CsrfField()` / `Form(hx=Hx(...))` on FastAPI pages. Manual
`csrf_token_for_request` + hidden inputs still work for existing apps. See
[CSRF composition](../api/CSRF_COMPOSITION.md) and [Minimal form](minimal-form.md).

## `hedron: command not found`

Prefer **`python -m hedron …`** with the same interpreter you used for `pip` / `uv`.
Full PATH fixes, Windows Scripts notes, and verification steps:
[Troubleshooting](troubleshooting.md#hedron-command-not-found).

## Why install Hedron twice (CLI then project)?

The **uv** path is one shot: `uvx … hedron new` scaffolds the app, then `uv sync`
installs the project-local pin. The **pip** path installs Hedron once so the **`hedron`
CLI** is available, then again as a **project dependency** (`pip install -e .`) so
`uvicorn app:app` imports the pinned version from the app’s environment. That second
install is what the scaffold’s `pyproject.toml` declares—do not skip it on pip.

## `uv add hedron` failed with “No pyproject.toml”

Create a project first: `uv init my-app && cd my-app`, then
`uv add "hedron>=0.23.0,<0.24"`. Or use
`hedron new my-app` after `pip install "hedron>=0.23.0,<0.24"`.

## Should I use `uv init` or `hedron new`?

Prefer **`hedron new`** for a ready scaffold on **0.23.x** (install Hedron first).
`uv init` + a hand-written `app.py` from the quickstart also works. Do not nest both into
the same directory by accident.

## What do Beta, Supported, and Deferred mean?

See [How to read Hedron docs](../getting-started/how-to-read.md). Short version:

- **Beta / Alpha** — **package** maturity on PyPI; pin versions (`>=0.23.0,<0.24`).
- **Supported** — **capability** readiness on a host; ship with pins. **Not** the same as API level `stable`.
- **Deferred** — documented, not ready; do not treat as Supported.
- API levels (`stable` / `beta` / …) in [STABILITY](../api/STABILITY.md) are a third axis.

A Beta package can expose Supported capabilities whose API level is still `beta`.

## Are Auto, DataTable, and charts available?

**Auto** (built-in inspectable object rendering — no extra) and **DataTable/DataEditor**
are **Supported** capabilities (`hedron` / `hedron[data]`). Those packages are **Beta**
on PyPI — pin versions.
**Charts** (`hedron[charts]`) are **Alpha** — available on PyPI, pin versions, expect churn.
See [What’s ready](whats-ready.md).

```bash
pip install "hedron[data]>=0.23.0,<0.24"     # DataTable, DataEditor (Auto is already in hedron)
pip install "hedron[charts]>=0.1.0,<0.2"   # Alpha: LineChart and visualization adapters
```

See [Auto](../api/AUTO.md), [Data](../api/DATA.md), [Charts](../api/CHART.md), and the
[charts and HTMX guide](charts-and-htmx.md).

## Are Flask and Django supported?

Yes. `hedron-flask` and `hedron-django` are **Beta** packages with a **Supported**
adapter matrix. Install them separately; they do not pull in FastAPI. Django apps must
use Django `>=5.2,<6`.
Django QuerySet DataSource and forms bridge are Supported. FastAPI ships SSE/WebSocket
helpers as **experimental**; on every host — including FastAPI — **polling** is the
Supported production fallback for live status. See [What’s ready](whats-ready.md),
[Compatibility](../COMPATIBILITY.md),
[Flask — add to existing app](../getting-started/flask.md), and
[Django — add to existing project](../getting-started/django.md).

## What replaced HDN?

An experimental template prototype (HDN) was removed in 0.9. New apps use typed Python
components or optional `hedron[jinja]` (HDJ). Migration details:
[upgrade guide](upgrade.md).

## Are the docs simulated UI demos a running Hedron server?

No. They are in-browser simulations. Clone and run a real app from
[examples/](https://github.com/eddiethedean/hedron/tree/main/examples) (`uv sync` after
clone)—FastAPI, Flask, and Django reference slices. See also
[Support](support.md) and [SECURITY.md](../SECURITY.md).

## Multi-worker / production secrets?

Use a real secret store for `session_secret` / Flask `SECRET_KEY` / Django `SECRET_KEY`.
Do not share development secrets across environments. Adopter convention:
`HEDRON_SESSION_SECRET` in the process environment, read in `app.py` and passed to
`Hedron(session_secret=...)`. See [Deployment](deployment.md) and
[Configuration](../CONFIGURATION.md).

## How do I test a Hedron app?

See [Test your UI](testing.md) and [API: Testing](../api/TESTING.md)
(`AppScenario`, HTMX asserts, portable adapter fixtures).

## How do I run background jobs?

In-process polling demo: [Jobs poll recipe](../examples/jobs-poll.md). Multi-worker:
shared Redis + [Celery / RQ](jobs-celery-rq.md) · [Jobs API](../api/JOBS.md). Prefer
polling over experimental SSE.

## How do I talk to Postgres / SQLAlchemy?

Start from the [Notes + SQLAlchemy recipe](../examples/notes-sqlalchemy.md) (SQLite locally;
swap the SQLAlchemy URL for Postgres). Hedron is not an ORM — use SQLAlchemy/SQLModel as
usual.

## How do I add OAuth / OIDC?

You own the IdP. Optional helpers: `hedron[auth]` / `hedron.oidc` — see
[Authentication](authentication.md). Session cookie demo:
[Session auth recipe](../examples/session-auth.md).

## Where do I put configuration?

Non-secret project settings go in `[tool.hedron]` (see
[Configuration](../CONFIGURATION.md)). Secrets and deployment mode use environment
variables / your secret store. Constructor args override both when explicit.

## How do I install HDJ / Jinja templates?

```bash
pip install "hedron[jinja]>=0.23.0,<0.24"
# or
uv add "hedron[jinja]>=0.23.0,<0.24"
```

See [HDJ authoring](hdj-authoring.md) and [Installation](../getting-started/installation.md).

## Where is the SBOM / evidence bundle?

Prefer GitHub Release assets for the train tag (`v0.22.0`), or regenerate from the
tagged checkout with
`scripts/build_evidence_bundle.py`. Step-by-step:
[Evidence pack](evidence-pack.md). PyPI remains authoritative for package versions.

## Why might GitHub “Latest release” lag PyPI?

Tags can land before Release objects/assets are attached. Trust **PyPI + the git tag** for
version truth; regenerate evidence from the tag if assets are missing.

## Supported vs Deferred (PERF / live browser)

**Supported** means the capability is claimed on that host for the current train.
**Deferred** rows (for example some load/proxy backpressure or live-browser evidence) mean
you should not treat them as proven — prefer **polling** for jobs when those rows matter
for your risk profile. See [What’s ready](whats-ready.md) and [Performance](performance.md).

## How do I contribute code?

See [Contributing](../CONTRIBUTING.md) for environment setup, tests, and the
specification process. Support expectations: [Support](support.md).
