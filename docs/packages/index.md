# Optional packages

Hedron ships independently publishable **extension packages** beside the flagship
[`hedron`](https://pypi.org/project/hedron/) FastAPI distribution and the
framework-neutral [`hedron-core`](https://pypi.org/project/hedron-core/) renderer.

Most install as flagship extras (`hedron[data]`, `hedron[dev]`, …). A few
(`hedron-sample-kit`, `hedron-sim`) install directly. **Flask / Django hosts** are
[framework adapters](../getting-started/flask.md) — not extension packages.

!!! note "Maturity"

    Package maturity (Beta / Alpha) ≠ capability readiness (Supported / Experimental).
    See [How to read](../getting-started/how-to-read.md) and
    [What’s ready](../guides/whats-ready.md). Pin versions on `0.x`.

## Beta train (`0.20.x`)

| Package | Extra | Role |
|---|---|---|
| [hedron-data](hedron-data.md) | `hedron[data]` | DataTable, DataEditor, data sources |
| [hedron-jinja](hedron-jinja.md) | `hedron[jinja]` | `.hdj` templates over Jinja / HTML / HTMX |
| [hedron-explorer](hedron-explorer.md) | `hedron[dev]` | Development Component Explorer |
| [hedron-extras](hedron-extras.md) | `hedron[extras]` | Curated workbenches and specialty UI |
| [hedron-conformance](hedron-conformance.md) | `hedron[conformance]` | Language-neutral conformance kit |

```bash
pip install "hedron[data,dev]>=0.20.0,<0.21"
```

## Alpha lines (`0.1.x`)

Pin and expect churn. Interactive chart runtimes, notebook preview, MCP, and Gradio
interop are **Experimental** / Alpha — not production defaults.

| Package | Extra | Role |
|---|---|---|
| [hedron-charts](hedron-charts.md) | `hedron[charts]` | Chart components and visualization adapters |
| [hedron-native](hedron-native.md) | `hedron[native]` | Optional Rust HTML-escape acceleration |
| [hedron-notebook](hedron-notebook.md) | `hedron[notebook]` | Server-side notebook preview helper |
| [hedron-mcp](hedron-mcp.md) | `hedron[mcp]` | Deny-by-default MCP projection |
| [hedron-gradio](hedron-gradio.md) | `hedron[gradio]` | Gradio client interop |
| [hedron-sample-kit](hedron-sample-kit.md) | — | Reference third-party plugin shape |
| [hedron-sim](hedron-sim.md) | — | Offline HTMX sims for static docs |

```bash
pip install "hedron[charts]>=0.1.0,<0.2"
pip install "hedron-sim>=0.1.0,<0.2"
```

## Host adapters (not extensions)

| Package | Start here |
|---|---|
| `hedron-flask` | [Add Flask app](../getting-started/flask.md) · [Adapters API](../api/ADAPTERS.md) |
| `hedron-django` | [Add Django project](../getting-started/django.md) · [Adapters API](../api/ADAPTERS.md) |

## See also

- [Installation (extras)](../getting-started/installation.md)
- [Public API](../api/README.md)
- [Plugins](../api/PLUGINS.md) · [Plugin authoring](../guides/plugin-authoring.md)
