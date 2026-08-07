# FAQ

## Which version should I install?

Pin the **0.18 train** for production (Beta on PyPI):

```bash
pip install "hedron>=0.19.0,<0.20"
# or
uv add "hedron>=0.19.0,<0.20"
```

`>=0.18.0` alone allows a future `0.19` break. Use an upper bound when you need a stable
train. See [What’s ready today](whats-ready.md) and the [public roadmap](roadmap.md).

**How is this different from Streamlit or FastHTML?** See [Why Hedron](why-hedron.md).

For curated extras (`hedron-extras`), install `hedron[extras]>=0.19.0,<0.20`.
**Auto** (inspectable object rendering built into `hedron` — no extra) is included.
For DataTable/DataEditor, install `hedron[data]>=0.19.0,<0.20`. For charts, install
For charts, install `hedron[charts]>=0.1.0,<0.2` (Alpha). For Flask/Django adapters:

```bash
pip install "hedron-flask>=0.19.0,<0.20"
pip install "hedron-django>=0.19.0,<0.20"   # requires Django >=5.2,<6
```

## Do I need Node.js?

No. Hedron does not require npm or a JavaScript bundler for development or production.

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
`uv add "hedron>=0.19.0,<0.20"`. Or use
`hedron new my-app` after `pip install "hedron>=0.19.0,<0.20"`.

## Should I use `uv init` or `hedron new`?

Prefer **`hedron new`** for a ready scaffold on **0.18.x** (install Hedron first).
`uv init` + a hand-written `app.py` from the quickstart also works. Do not nest both into
the same directory by accident.

## What do Beta, Supported, and Deferred mean?

See [How to read Hedron docs](../getting-started/how-to-read.md). Short version:

- **Beta / Alpha** — **package** maturity on PyPI; pin versions (`>=0.19.0,<0.20`).
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
pip install "hedron[data]>=0.19.0,<0.20"     # DataTable, DataEditor (Auto is already in hedron)
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
pip install "hedron[jinja]>=0.19.0,<0.20"
# or
uv add "hedron[jinja]>=0.19.0,<0.20"
```

See [HDJ authoring](hdj-authoring.md) and [Installation](../getting-started/installation.md).

## Where is the SBOM / evidence bundle?

Prefer GitHub Release assets for the train tag (for example `v0.18.0`), or regenerate from
the tagged checkout with `scripts/build_evidence_bundle.py`. Step-by-step:
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
