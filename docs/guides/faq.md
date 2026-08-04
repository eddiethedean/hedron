# FAQ

## Which version should I install?

```bash
pip install "hedron>=0.10.0"
# or
uv add "hedron>=0.10.0"
```

That installs the current published train from PyPI (**0.10.0**)—see
[What’s ready today](whats-ready.md). `Auto` is included. For DataTable/DataEditor, install
`hedron[data]`. For charts, install `hedron[charts]`. For Flask/Django adapters:

```bash
pip install hedron-flask
pip install hedron-django   # requires Django >=5.2,<6
```

## Do I need Node.js?

No. Hedron does not require npm or a JavaScript bundler for development or production.

## `uv add hedron` failed with “No pyproject.toml”

Create a project first: `uv init my-app && cd my-app`, then `uv add hedron`. Or use
`hedron new my-app` after `pip install "hedron>=0.10.0"`.

## Should I use `uv init` or `hedron new`?

Prefer **`hedron new`** for a ready scaffold on the current train (install Hedron first).
`uv init` + a hand-written `app.py` from the quickstart also works. Do not nest both into
the same directory by accident.

## What do Beta, Supported, and Deferred mean?

See [How to read Hedron docs](../getting-started/how-to-read.md). Short version:

- **Beta** — package maturity; pin versions.
- **Supported** — claimed working capability on that host.
- **Deferred** — documented, not ready; do not treat as Supported.

Detailed API compatibility levels live in [STABILITY](../api/STABILITY.md).

## Are Auto, DataTable, and charts available?

Yes on the published PyPI train. `Auto` ships in core `hedron` (no extra). Tabular
widgets and charts need extras:

```bash
pip install "hedron[data]"     # DataTable, DataEditor (Auto is already in hedron)
pip install "hedron[charts]"   # LineChart and visualization adapters
```

See [Auto](../api/AUTO.md), [Data](../api/DATA.md), [Charts](../api/CHART.md), and the
[charts and HTMX guide](charts-and-htmx.md).

## Are Flask and Django supported?

Yes as **Beta** packages with a **Supported** adapter matrix (`hedron-flask`, `hedron-django`).
Install them separately; they do not pull in FastAPI. Django apps must use Django `>=5.2,<6`.
Some rows remain Deferred (Django QuerySet as a first-party DataSource; Hedron-owned Django forms).
Official HTMX SSE is Supported on the FastAPI flagship in 0.10; polling remains the Supported
fallback on all hosts. See [Compatibility](../COMPATIBILITY.md),
[Flask quickstart](../getting-started/flask.md), and
[Django quickstart](../getting-started/django.md).

## What replaced HDN?

Phase 0.9 removes HDN completely. Use typed Python components or install the optional
`hedron-jinja` package for trusted application templates. There is no `.hdn` discovery,
compatibility mode, or converter. See the [Jinja API contract](../api/JINJA.md) and
[0.9 upgrade guide](upgrade.md).

## Are the docs component gallery demos a running Hedron server?

No. They are in-browser simulations. Clone and run a real app from
[examples/](https://github.com/eddiethedean/hedron/tree/main/examples) (`uv sync` after
clone)—FastAPI, Flask, and Django reference slices. See also
[Support](support.md) and [SECURITY.md](../SECURITY.md).

## Multi-worker / production secrets?

Use a real secret store for `session_secret` / Flask `SECRET_KEY` / Django `SECRET_KEY`.
Do not share development secrets across environments. See [Deployment](deployment.md)
and [Configuration](../CONFIGURATION.md).

## Where do I put configuration?

Non-secret project settings go in `[tool.hedron]` (see
[Configuration](../CONFIGURATION.md)). Secrets and deployment mode use environment
variables / your secret store. Constructor args override both when explicit.

## How do I install HDJ / Jinja templates?

```bash
pip install "hedron[jinja]"
# or
uv add "hedron[jinja]"
```

See [HDJ authoring](../api/JINJA.md) and [Installation](../getting-started/installation.md).

## How do I contribute code?

See [Contributing](../CONTRIBUTING.md) for environment setup, tests, and the
specification process. Support expectations: [Support](support.md).
