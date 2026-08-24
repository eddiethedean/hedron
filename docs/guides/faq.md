# FAQ

## Which version should I install?

Install the latest public release from PyPI:
`pip install "hedron>=0.63.0,<0.64"`. Contributors working from a git checkout use
`uv sync` (workspace packages). The verified `v0.63.0` release is published on PyPI and has a
[GitHub Release](https://github.com/eddiethedean/hedron/releases/tag/v0.63.0); its [release CI](https://github.com/eddiethedean/hedron/actions/runs/32785419240)
passed all gates. See
[Installation](../getting-started/installation.md).

```bash
pip install "hedron>=0.63.0,<0.64"
# or
uv add "hedron>=0.63.0,<0.64"
```

Always use an upper bound so a future minor train cannot install by accident.
Packages are **Beta** (usable, no 1.0, no SLA). Capability detail:
[What’s ready](whats-ready.md).

**How is this different from Streamlit or FastHTML?** See [Why Hedron](why-hedron.md).

For DataTable/DataEditor, install `hedron[data]>=0.63.0,<0.64`. For charts, install
`hedron[charts]>=0.63.0,<0.64`
([Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor)).
Flask/Django adapters:

```bash
pip install "hedron-flask>=0.63.0,<0.64"
pip install "hedron-django>=0.63.0,<0.64"   # requires Django >=5.2,<6
```

## Do I need Node.js?

No. Hedron does not require npm or a JavaScript bundler for development or production.

## What is HTMX?

A small browser library that swaps server HTML into page regions using attributes like
`hx-get` / `hx-target`. Hedron uses it for fragment updates — see
[What is HTMX?](../getting-started/what-is-htmx.md).

## Why is FastAPI pinned so tightly?

Two bands: **declared** install metadata allows FastAPI `>=0.141.1,<0.150` and Pydantic
`>=2.13.4,<2.15`; the **CI-supported** matrix tests the tighter bands FastAPI
`>=0.141.1,<0.142` and Pydantic `>=2.13.4,<2.14`. Prefer Supported for first apps.
Shared data-science envs with older FastAPI often fail to resolve — use a **clean venv**.
Details: [Compatibility](../COMPATIBILITY.md).

## Refresh status clicked but nothing changed

1. Confirm you are on the **running app** (`uvicorn`, usually
   [http://127.0.0.1:8000](http://127.0.0.1:8000)), not a docs **Preview (no server)** /
   Demo simulation.
2. Hard-refresh the browser; with `--reload`, wait for the server to finish restarting.
3. Open the network tab: the Refresh click should request `/status` (or your fragment
   path) with `HX-Request: true` and an `HX-Target` that matches a declared region id.
4. A wrong or undeclared target returns **403** (fail closed) — not a silent no-op.

See [Troubleshooting](troubleshooting.md#htmx-403-on-fragment-request) and
[HTMX interactions](htmx-interactions.md).

## First POST returns 403

Built-in `security="standard"` validates CSRF on unsafe methods. Load a GET page first
so the cookie/context is seeded. FastAPI/Flask: include `CsrfField()` (`csrf_token`).
Django: use `csrfmiddlewaretoken` (portable `csrf_token` is not accepted). See
[Minimal form POST](minimal-form.md) and
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
with eyes open: packages are **Beta**, pin `>=0.63.0,<0.64`, prefer polling
for live status, and read [What’s ready](whats-ready.md). There is no vendor SLA or
scheduled 1.0. Use the [PoC checklist](evaluate.md#poc-checklist) on
[Evaluate](evaluate.md).

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
`uv add "hedron>=0.63.0,<0.64"`. Or use
`hedron new my-app` after `pip install "hedron>=0.63.0,<0.64"`.

## Should I use `uv init` or `hedron new`?

Prefer **`hedron new`** for a ready scaffold (install Hedron first).
`uv init` + a hand-written `app.py` from the quickstart also works. Do not nest both into
the same directory by accident.

## What do Beta, Supported, and Deferred mean?

Short version for builders: **pin from PyPI** (`hedron>=0.63.0,<0.64`). The repository
train is for contributors and is not an application install source.
Packages are Beta; that does not mean “do not use” — it means expect
occasional `0.x` churn and pin upper bounds.

Evaluators (three axes — skip if you are just building):

- **Beta / Alpha** — **package** maturity on PyPI; pin versions.
- **Supported** — **capability** readiness on a host; ship with pins. **Not** the same as API level `stable`.
- **Deferred** — documented, not ready; do not treat as Supported.
- API levels (`stable` / `beta` / …) in [STABILITY](../api/STABILITY.md) are a third axis.

Full cheat-sheet: [Maturity labels (evaluators)](../getting-started/how-to-read.md).
Snapshot: [What’s ready today](whats-ready.md).

## What is a “train”? Why these version pins?

A **train** is a minor release line (for example `0.60.x`). Patch releases inside the
train are meant to be compatible; the next minor (`0.60`) may add breaking changes.

Install with an upper bound — `hedron>=0.63.0,<0.64` — so you get patches automatically
but do not jump to the next train by accident. That is ordinary Python packaging, not a
second registry. Contributors working from a git checkout use `uv sync`; application
installs use PyPI.

See [Current release](current-release.md) and [Compatibility](../COMPATIBILITY.md).

## Why pin with an upper bound?

A lower bound without an upper bound allows a future minor train to install
automatically. Use `hedron>=0.63.0,<0.64` so compatible patches are accepted while the
next minor train requires an intentional review. See [Compatibility](../COMPATIBILITY.md).

## Are Auto, DataTable, and charts available?

**Auto** (built-in — no extra) and **DataTable/DataEditor** (`hedron[data]`) are
**Supported**. Those packages are **Beta** on PyPI — pin versions.

Charts install through `hedron[charts]>=0.63.0,<0.64`; the sample kit installs as
`hedron-sample-kit>=0.2.1,<0.3`. Earlier satellite versions target older cores. See
[What’s ready](whats-ready.md) and
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

```bash
pip install "hedron[data]>=0.63.0,<0.64"     # DataTable, DataEditor (Auto is already in hedron)
pip install "hedron[charts]>=0.63.0,<0.64"   # compatible chart satellite
```

See [Auto](../api/AUTO.md), [Data](../api/DATA.md), and the
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

## Are the docs simulated UI demos a running Hedron server?

No. They are in-browser simulations. Clone and run a real app from
[examples/](https://github.com/eddiethedean/hedron/tree/main/examples) (`uv sync` after
clone)—FastAPI, Flask, and Django reference slices.

## Multi-worker / production secrets?

See [Secrets, sessions, and workers](secrets-and-workers.md). Short version: pass
`session_secret=` into `Hedron` (the env var `HEDRON_SESSION_SECRET` is a convention —
Hedron does not load it for you). Multiple workers need sticky sessions **or** a shared
session store, plus a shared job backend for status.

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

## How do I add login?

Start with [session auth](../examples/session-auth.md) to gate a page. Optional OIDC
helpers: `hedron[auth]` — [Authentication](authentication.md). You own the identity
provider.

## Where do I put configuration?

Non-secret project settings go in `[tool.hedron]` (see
[Configuration](../CONFIGURATION.md)). Secrets and deployment mode use environment
variables / your secret store. Constructor args override both when explicit.

## How do I install Jinja templates?

```bash
pip install "hedron[jinja]>=0.63.0,<0.64"
# or
uv add "hedron[jinja]>=0.63.0,<0.64"
```

See [HDJ authoring](hdj-authoring.md) and [Installation](../getting-started/installation.md).

## Procurement / evidence pack?

Evaluator diligence (SBOM, support window, GitHub release lag) lives on
[Evaluate](evaluate.md) and [Enterprise diligence](enterprise-diligence.md), not this builder FAQ.

Prefer **polling** for job status. SSE / WebSocket helpers remain experimental. See
[What’s ready](whats-ready.md) and [Live updates](live-interaction.md).

## How do I contribute code?

See [Contributor day-one](contributor-day-one.md) for environment setup, tests, and the
specification process. Support expectations: [Support](support.md).
