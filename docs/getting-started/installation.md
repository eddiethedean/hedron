# Installation

The `hedron` package is the recommended starting point for applications. It includes the
framework-neutral rendering core plus FastAPI routing, HTMX responses, security policy,
state, CLI tooling, plugins, and testing helpers.

## Create a project

=== "uv"

    ```bash
    uv init my-hedron-app
    cd my-hedron-app
    uv add hedron "uvicorn[standard]"
    ```

=== "pip"

    ```bash
    mkdir my-hedron-app && cd my-hedron-app
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install hedron "uvicorn[standard]"
    ```

=== "CLI scaffold"

    ```bash
    pip install hedron
    hedron new my-hedron-app
    cd my-hedron-app
    ```

`hedron new` creates `app.py`, `pyproject.toml`, and a component directory. It refuses to
overwrite a non-empty destination unless you pass `--force`. Do not run `uv init` and
`hedron new` into the same directory unless you intend to replace the scaffold.

Then follow the [quickstart](quickstart.md), or use the generated `app.py` from
`hedron new`.

## Choose a package

| Package | Use it when | Install |
|---|---|---|
| `hedron` | You are building a FastAPI web application | `uv add hedron` |
| `hedron-flask` | You need Flask (Supported Beta adapter) | `uv add hedron-flask` |
| `hedron-django` | You need Django `>=5.2,<6` (Supported Beta adapter) | `uv add hedron-django` |
| `hedron-core` | You need framework-neutral component rendering | `uv add hedron-core` |
| `hedron[data]` | You need DataTable / DataEditor / data sources | `uv add "hedron[data]"` |
| `hedron[charts]` | You need LineChart and visualization adapters | `uv add "hedron[charts]"` |
| `hedron[markdown]` | You need Markdown rendering | `uv add "hedron[markdown]"` |
| `hedron[code]` | You need Pygments code highlighting | `uv add "hedron[code]"` |
| `hedron[images]` | You need Pillow image helpers | `uv add "hedron[images]"` |
| `hedron[email]` | You need email address validation helpers | `uv add "hedron[email]"` |
| `hedron[sanitize]` | You need nh3 HTML sanitization (`TrustedHtml.nh3`) | `uv add "hedron[sanitize]"` |
| `hedron[auth]` | You need Authlib helpers | `uv add "hedron[auth]"` |
| `hedron[dev]` | You also want Component Explorer | `uv add "hedron[dev]"` |
| `hedron[browser]` | You need browser and accessibility test helpers | `uv add "hedron[browser]"` |

Chart backends are optional on top of `hedron-charts`:

| Extra | Backend |
|---|---|
| `hedron-charts[matplotlib]` | Matplotlib static charts |
| `hedron-charts[plotly]` | Plotly interactive charts |
| `hedron-charts[altair]` | Altair / Vega-Lite charts |

Or install a backend through the flagship package once `hedron[charts]` is present
(for example `pip install "hedron-charts[plotly]"`).

## Verify the installation

```bash
uv run python -c "import hedron; print(hedron.__version__)"
```

The installed version should print without an import error. Expect **`0.10.0`** from PyPI for the
current live-interaction train—see [STATUS](../STATUS.md). Data APIs require `hedron-data`
(`pip install "hedron[data]"`). Charts require `hedron-charts`
(`pip install "hedron[charts]"`). Hedron follows semantic versioning; see the
[roadmap](../ROADMAP.md) and [compatibility policy](../COMPATIBILITY.md).

## Contributor checkout

To work on Hedron itself:

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
```

See [Contributing](../CONTRIBUTING.md).

## Supported environments

Hedron supports CPython 3.11–3.14. The flagship integration pins a compatible FastAPI
range; let your package manager resolve it instead of installing FastAPI separately at
an incompatible version. See the [compatibility policy](../COMPATIBILITY.md) for the
full support matrix and deprecation rules.

[Build your first app :material-arrow-right:](quickstart.md){ .md-button .md-button--primary }
