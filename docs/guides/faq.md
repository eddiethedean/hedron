# FAQ

## Which version should I install?

```bash
pip install "hedron>=0.18.0"
# or
uv add "hedron>=0.18.0"
```

That pins **Hedron 0.18.0** (Beta on PyPI). See
[What’s ready today](whats-ready.md) and the [public roadmap](roadmap.md).

**How is this different from Streamlit or FastHTML?** See [Why Hedron](why-hedron.md).

For curated extras (`hedron-extras`), install `hedron[extras]>=0.18.0`.
**Auto** (inspectable object rendering built into `hedron` — no extra) is included.
For DataTable/DataEditor, install `hedron[data]>=0.18.0`. For charts, install
`hedron[charts]>=0.1.0` (Alpha). For Flask/Django adapters:

```bash
pip install "hedron-flask>=0.18.0"
pip install "hedron-django>=0.18.0"   # requires Django >=5.2,<6
```

## Do I need Node.js?

No. Hedron does not require npm or a JavaScript bundler for development or production.

## `hedron: command not found`

The `hedron` CLI is only on your shell PATH when the install environment’s scripts
directory is active. **Always-works:** `python -m hedron new …` / `python -m hedron check`
with the same interpreter you used for `pip`.

Other common fixes:

1. Prefer **`uv tool install "hedron>=0.18.0"`** (or `pipx install`), then **re-open the shell**.
2. After `hedron new` and `pip install -e .` / `uv sync`, run the CLI from the project
   environment: `uv run hedron …` (or activate the venv and run `hedron` / `python -m hedron`).
3. On Windows, ensure the Python **Scripts** folder is on PATH (for example
   `%APPDATA%\Python\Python3x\Scripts` after a user install).
4. Confirm the library itself installed with the **same** interpreter you use for
   `uvicorn`:

   ```bash
   python -c "import hedron; print(hedron.__version__)"
   ```

Full steps: [Troubleshooting](troubleshooting.md#hedron-command-not-found).

## Why install Hedron twice (CLI then project)?

The **uv** path is one shot: `uvx … hedron new` scaffolds the app, then `uv sync`
installs the project-local pin. The **pip** path installs Hedron once so the **`hedron`
CLI** is available, then again as a **project dependency** (`pip install -e .`) so
`uvicorn app:app` imports the pinned version from the app’s environment. That second
install is what the scaffold’s `pyproject.toml` declares—do not skip it on pip.

## `uv add hedron` failed with “No pyproject.toml”

Create a project first: `uv init my-app && cd my-app`, then `uv add hedron`. Or use
`hedron new my-app` after `pip install "hedron>=0.18.0"`.

## Should I use `uv init` or `hedron new`?

Prefer **`hedron new`** for a ready scaffold on **0.18.x** (install Hedron first).
`uv init` + a hand-written `app.py` from the quickstart also works. Do not nest both into
the same directory by accident.

## What do Beta, Supported, and Deferred mean?

See [How to read Hedron docs](../getting-started/how-to-read.md). Short version:

- **Beta** — package maturity; pin versions.
- **Supported** — claimed working capability on that host.
- **Deferred** — documented, not ready; do not treat as Supported.

Detailed API compatibility levels live in [STABILITY](../api/STABILITY.md).

## Are Auto, DataTable, and charts available?

**Auto** (built-in inspectable object rendering — no extra) and **DataTable/DataEditor**
are Supported on Beta packages (`hedron` / `hedron[data]`).
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
