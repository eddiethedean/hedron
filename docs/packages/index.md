# Optional packages

Hedron ships independently publishable packages beside the flagship FastAPI distribution.
Start with the flagship and adapters if you are new; use this catalog for **extras**.

## Start here (flagship and hosts)

| Package | Role | Docs |
|---|---|---|
| [`hedron`](https://pypi.org/project/hedron/) | FastAPI flagship | [First app](../getting-started/quickstart.md) · [Hedron API](../api/HEDRON.md) |
| [`hedron-core`](https://pypi.org/project/hedron-core/) | Framework-neutral renderer | [Architecture](../ARCHITECTURE.md) |
| [`hedron-flask`](https://pypi.org/project/hedron-flask/) | Flask host adapter | [Flask](../getting-started/flask.md) · [Adapters](../api/ADAPTERS.md) |
| [`hedron-django`](https://pypi.org/project/hedron-django/) | Django host adapter | [Django](../getting-started/django.md) · [Adapters](../api/ADAPTERS.md) |

Most extras install as flagship extras (`hedron[data]`, `hedron[dev]`, …). `hedron-sim`
and the sample kit install directly. Charts require the compatible `0.1.6` satellite floor.

!!! note "Maturity"

    Package maturity (Beta / Alpha) ≠ capability readiness (Supported / Experimental).
    See [How to read](../getting-started/how-to-read.md) and
    [What’s ready](../guides/whats-ready.md). Pin versions on `0.x`.

## Beta extensions (`0.25.x`)

| Package | Extra | Role |
|---|---|---|
| [hedron-data](hedron-data.md) | `hedron[data]` | DataTable, DataEditor, data sources |
| [hedron-jinja](hedron-jinja.md) | `hedron[jinja]` | `.hdj` templates over Jinja / HTML / HTMX |
| [hedron-explorer](hedron-explorer.md) | `hedron[dev]` | Development Component Explorer |
| [hedron-extras](hedron-extras.md) | `hedron[extras]` | Curated toolkit (specialty widgets may be Experimental/stub) |
| [hedron-conformance](hedron-conformance.md) | `hedron[conformance]` | Language-neutral conformance kit |

```bash
pip install "hedron[data,dev]>=0.27.0,<0.28"
```

## Alpha lines

Pin and expect churn. Interactive chart runtimes, notebook preview, MCP, and Gradio
interop are **Experimental** / Alpha — not production defaults.

| Package | Extra | Role |
|---|---|---|
| [hedron-charts](hedron-charts.md) | `hedron[charts]` | Visualization adapters; `>=0.1.6,<0.2` on Hedron 0.26 |
| [hedron-native](hedron-native.md) | `hedron[native]` | Optional Rust HTML-escape acceleration |
| [hedron-notebook](hedron-notebook.md) | `hedron[notebook]` | Server-side notebook preview helper |
| [hedron-mcp](hedron-mcp.md) | `hedron[mcp]` | Deny-by-default MCP projection |
| [hedron-gradio](hedron-gradio.md) | `hedron[gradio]` | Gradio client interop |
| [hedron-sample-kit](hedron-sample-kit.md) | — | Reference third-party plugin shape; `>=0.1.6,<0.2` |
| [hedron-sim](hedron-sim.md) | — | Offline HTMX sims for static docs |

```bash
pip install "hedron[charts]>=0.27.0,<0.28"
pip install "hedron-sample-kit>=0.1.6,<0.2" "hedron-sim>=0.1.0,<0.2"
```

## Authoring an extension

Core stays framework-neutral; extensions depend toward `hedron-core` (and optionally
`hedron`). See [Plugin authoring](../guides/plugin-authoring.md) and
[Project layout](https://github.com/eddiethedean/hedron/blob/main/docs/PROJECT_LAYOUT.md).

## See also

- [Installation (extras)](../getting-started/installation.md)
- [What’s ready](../guides/whats-ready.md)
- [Adapters API](../api/ADAPTERS.md)
