# FAQ

## Which version should I install?

```bash
pip install "hedron>=0.10.1"
# or
uv add "hedron>=0.10.1"
```

That installs the current published train from PyPI (**0.10.1**)—see
[What’s ready today](whats-ready.md). `Auto` is included. For DataTable/DataEditor, install
`hedron[data]`. For charts, install `hedron[charts]`. For Flask/Django adapters:

```bash
pip install hedron-flask
pip install hedron-django   # requires Django >=5.2,<6
```

## Do I need Node.js?

No. Hedron does not require npm or a JavaScript bundler for development or production.

## `hedron: command not found`

The `hedron` CLI is only on your shell PATH when the install environment’s scripts
directory is active. Common fixes:

1. Prefer **`uv tool install "hedron>=0.10.1"`**, then **re-open the shell** (or run
   `hash -r` / open a new terminal).
2. After `hedron new` and `pip install -e .` / `uv sync`, run the CLI from the project
   environment: `uv run hedron …` (or activate the venv and run `hedron` again).
3. On Windows, ensure the Python **Scripts** folder is on PATH (for example
   `%APPDATA%\Python\Python3x\Scripts` after a user install).
4. Confirm the library itself installed with the **same** interpreter you use for
   `uvicorn`:

   ```bash
   python -c "import hedron; print(hedron.__version__)"
   ```

There is no `python -m hedron` entry point today—use the `hedron` console script or
`uv run hedron`. Full steps: [Troubleshooting](troubleshooting.md#hedron-command-not-found).

## Why install Hedron twice (CLI then project)?

The recommended scaffold path installs Hedron once so the **`hedron` CLI** is available
(`pip install` / `uv tool install`), then again as a **project dependency**
(`pip install -e .` / `uv sync`) so `uvicorn app:app` imports the pinned version from
the app’s environment. That second install is what the scaffold’s `pyproject.toml`
declares—do not skip it.

## `uv add hedron` failed with “No pyproject.toml”

Create a project first: `uv init my-app && cd my-app`, then `uv add hedron`. Or use
`hedron new my-app` after `pip install "hedron>=0.10.1"`.

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

**Auto** and **DataTable/DataEditor** are Beta Supported (`hedron` / `hedron[data]`).
**Charts** (`hedron[charts]`) are **Alpha** — available on PyPI, pin versions, expect churn.
See [What’s ready](whats-ready.md).

```bash
pip install "hedron[data]"     # DataTable, DataEditor (Auto is already in hedron)
pip install "hedron[charts]"   # Alpha: LineChart and visualization adapters
```

See [Auto](../api/AUTO.md), [Data](../api/DATA.md), [Charts](../api/CHART.md), and the
[charts and HTMX guide](charts-and-htmx.md).

## Are Flask and Django supported?

Yes as **Beta** packages with a **Supported** adapter matrix (`hedron-flask`, `hedron-django`).
Install them separately; they do not pull in FastAPI. Django apps must use Django `>=5.2,<6`.
Some rows remain Deferred (Django QuerySet as a first-party DataSource; Hedron-owned Django forms).
Official HTMX SSE is Supported on the FastAPI flagship in 0.10; polling remains the Supported
fallback on all hosts. See [Compatibility](../COMPATIBILITY.md),
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

See [HDJ authoring](hdj-authoring.md) and [Installation](../getting-started/installation.md).

## How do I contribute code?

See [Contributing](../CONTRIBUTING.md) for environment setup, tests, and the
specification process. Support expectations: [Support](support.md).
