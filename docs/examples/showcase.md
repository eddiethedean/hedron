---
description: A full-feature Hedron operations console built from the real runnable application.
---

# Hedron Showcase

Meet Hedron through the complete synthetic operations console instead of a collection of isolated
snippets. This page documents the real runnable application, so the UI you run locally is the UI
represented here; there is no separate documentation-only showcase implementation.

## Run the real app

From a repository checkout:

```bash
uv sync
uv run uvicorn --app-dir examples/showcase app:app --reload
```

Open <http://127.0.0.1:8000/>. The data is synthetic and local, but the application boundaries
are real: AppShell chrome, typed components, fragment refresh, an unsafe action, and ordinary
FastAPI-compatible routing.

The complete source is [`examples/showcase/app.py`](https://github.com/eddiethedean/hedron/blob/v1.0/examples/showcase/app.py).

The built-in theme emits coordinated light/dark tokens and follows the browser color preference;
the app shell and content grids collapse for narrow screens.

## What this showcases

| Surface | Hedron building block |
|---|---|
| Product chrome | `AppShell`, `Brand`, environment banner, account summary, grouped navigation |
| Operational overview | `PageHeader`, `Alert`, `Metric`, `Card`, `Status` |
| Workflow visibility | `ProcessFlow`, `Progress`, `Timeline`, `ResourceList` |
| Structured data | `Table`, column metadata, status badges, bounded result views |
| Server interaction | `@app.view` fragment refresh and `@app.action` approval with fallback |
| Extensibility | Explicit fragment regions, typed component values, inspectable route contracts |

For production architecture, continue to the [reference app](reference-app.md). For the smallest
first success, use [Build your first Hedron app](../getting-started/quickstart.md).
