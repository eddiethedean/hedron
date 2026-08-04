# FAQ

## Which version should I install?

```bash
pip install hedron
# or
uv add hedron
```

That installs the latest published release from PyPI. Repository `main` is implementing the
intentional **0.9.0** HDN-to-HDJ authoring break; published artifacts may lag—see
[STATUS](../STATUS.md). For DataTable/DataEditor, install
`hedron[data]`. For charts, install `hedron[charts]`. For Flask/Django adapters:

```bash
pip install hedron-flask
pip install hedron-django   # requires Django >=5.2,<6
```

## Do I need Node.js?

No. Hedron does not require npm or a JavaScript bundler for development or production.

## `uv add hedron` failed with “No pyproject.toml”

Create a project first: `uv init my-app && cd my-app`, then `uv add hedron`. Or use
`hedron new my-app` after `pip install hedron`.

## Should I use `uv init` or `hedron new`?

Either works. Prefer one path: `uv init` + hand-written `app.py` from the quickstart, or
`hedron new` alone. Do not nest both into the same directory by accident.

## Are Auto, DataTable, and charts available?

Yes on the published PyPI train:

```bash
pip install "hedron[data]"     # Auto, DataTable, DataEditor
pip install "hedron[charts]"   # LineChart and visualization adapters
```

See [Auto](../api/AUTO.md), [Data](../api/DATA.md), [Charts](../api/CHART.md), and the
[charts and HTMX guide](charts-and-htmx.md).

## Are Flask and Django supported?

Yes as **Beta Supported** adapters (`hedron-flask`, `hedron-django`). Install them
separately; they do not pull in FastAPI. Django apps must use Django `>=5.2,<6`. Some
rows remain Deferred (official HTMX SSE; Django QuerySet as a first-party DataSource;
Hedron-owned Django forms). See [Compatibility](../COMPATIBILITY.md),
[Flask quickstart](../getting-started/flask.md), and
[Django quickstart](../getting-started/django.md).

## What does “Supported” vs “Deferred” vs package Beta mean?

- **Package maturity** (Beta/Alpha): how ready the *distribution* is for production judgment.
- **API stability** (`stable` / `beta` / `experimental` / `internal` / `deferred`): compatibility catalog in
  [STABILITY](../api/STABILITY.md).
- **Adapter capability Supported/Deferred**: what we claim in acceptance evidence
  ([ADAPTERS](../acceptance/ADAPTERS.md)). Deferred features are documented and must not
  be marketed as Supported.

## What replaced HDN?

Phase 0.9 removes HDN completely. Use typed Python components or install the optional
`hedron-jinja` package for trusted application templates. There is no `.hdn` discovery,
compatibility mode, or converter. See the [Jinja API contract](../api/JINJA.md) and
[0.9 upgrade guide](upgrade.md).

## Are the docs “interactive demos” a running Hedron server?

No. They are in-browser simulations. Runnable backends live under
[examples/](https://github.com/eddiethedean/hedron/tree/main/examples) in the repo
(`uv sync` after clone)—FastAPI, Flask, and Django reference slices.

## Multi-worker / production secrets?

Use a real secret store for `session_secret` / Flask `SECRET_KEY` / Django `SECRET_KEY`.
Do not share development secrets across environments. See [Deployment](deployment.md)
and [Configuration](../CONFIGURATION.md).

## Where do I put configuration?

Non-secret project settings go in `[tool.hedron]` (see
[Configuration](../CONFIGURATION.md)). Secrets and deployment mode use environment
variables / your secret store. Constructor args override both when explicit.

## How do I contribute code?

See [Contributing](../CONTRIBUTING.md) for environment setup, tests, and the
specification process.
