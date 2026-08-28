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
| [`fastapi-workbench`](https://pypi.org/project/fastapi-workbench/) | Independent 1.x Posit Workbench adapter for plain FastAPI/ASGI apps | [FastAPI Workbench](../guides/fastapi-workbench.md) |

Most extras install as flagship extras (`hedron[data]`, `hedron[dev]`, …). `hedron-sim`
and the sample kit install directly. This catalog describes the verified 1.0 repository
inventory; PyPI still serves the 0.66.2 coordinated train until publication.

!!! note "Maturity"

    Package maturity (Beta / Alpha) ≠ capability readiness (Supported / Experimental).
    See [How to read](../getting-started/how-to-read.md) and
    [What’s ready](../guides/whats-ready.md). Use the documented upper bound for every
    coordinated or independent distribution.

## Extensions and adapters

| Package | Extra | Role |
|---|---|---|
| [hedron-data](hedron-data.md) | `hedron[data]` | DataTable, DataEditor, data sources |
| [hedron-jinja](hedron-jinja.md) | `hedron[jinja]` | `.hdj` templates over Jinja / HTML / HTMX |
| [hedron-explorer](hedron-explorer.md) | `hedron[dev]` | Development Component Explorer |
| [hedron-extras](hedron-extras.md) | `hedron[extras]` | Curated toolkit (specialty widgets may be Experimental/stub) |
| [hedron-conformance](hedron-conformance.md) | `hedron[conformance]` | Language-neutral conformance kit |
| [hedron-charts](hedron-charts.md) | `hedron[charts]` | First-party charts and visualization adapters; `>=0.2.3,<0.3` on the 1.0 train |
| [hedron-native](hedron-native.md) | `hedron[native]` | Optional Rust HTML-escape acceleration |
| [hedron-posit](hedron-posit.md) | `hedron[posit]` | Preferred Posit Workbench / Connect facade (`HedronPosit`) |
| [hedron-maps](hedron-maps.md) | `hedron[maps]` | First-class custom-server, MapLibre, and offline maps (`hedron-maps` `0.1.3`) |
| [hedron-elements](hedron-elements.md) | `hedron[elements]` | Beta Web Component ABI; production-grade for the locked Supported inventory only |

```bash
pip install "hedron[data,dev,posit]>=0.66.2,<0.67"
```

The checkout tip is `v1.0.0`; the latest public PyPI release remains `v0.66.2`.

## Tooling-grade and independent Beta lines

These packages version independently from the flagship train. Their declared Supported
scope is intentionally narrow; for example, notebook preview is localhost-only, MCP is
deny-by-default, and Gradio allows only declared remote destinations.

| Package | Extra | Role |
|---|---|---|
| [hedron-notebook](hedron-notebook.md) | `hedron[notebook]` | Server-side notebook preview helper |
| [hedron-mcp](hedron-mcp.md) | `hedron[mcp]` | Deny-by-default MCP projection |
| [hedron-gradio](hedron-gradio.md) | `hedron[gradio]` | Gradio client interop |
| [hedron-sample-kit](hedron-sample-kit.md) | — | Reference third-party plugin shape; `>=0.2.2,<0.3` |
| [hedron-sim](hedron-sim.md) | — | Offline HTMX sims for static docs; `>=0.2.2,<0.3` |
| [hedron-runtime-node](hedron-runtime-node.md) | npm | Portable Node conformance evaluator |
| [hedron-runtime-java](hedron-runtime-java.md) | Maven | Portable Java conformance evaluator |

```bash
pip install "hedron[charts]>=0.66.2,<0.67"
```

After the coordinated 1.0 publication (or from a local wheel set built from this checkout):

```bash
pip install "hedron-sample-kit>=0.2.2,<0.3" "hedron-sim>=0.2.2,<0.3"
```

Independent package versions are listed above; check each page for its Hedron compatibility
range and publication status.

## Authoring an extension

Core stays framework-neutral; extensions depend toward `hedron-core` (and optionally
`hedron`). See [Plugin authoring](../guides/plugin-authoring.md) and
[Project layout](https://github.com/eddiethedean/hedron/blob/main/docs/PROJECT_LAYOUT.md).

## See also

- [Installation (extras)](../getting-started/installation.md)
- [What’s ready](../guides/whats-ready.md)
- [Adapters API](../api/ADAPTERS.md)
