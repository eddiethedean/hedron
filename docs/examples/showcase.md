---
description: A full-feature Hedron operations console, available as a real app and an offline simulation.
---

# Hedron Showcase

Meet Hedron through a complete synthetic operations console instead of a collection of isolated
snippets. The same product story is available in two forms:

- **Run the real app** with FastAPI, real Hedron routes, server-rendered components, and a
  CSRF-protected action.
- **Try the offline simulation** below with `hedron-sim`; it needs no server and exercises the
  documented fragment contracts in your browser.

## Run the real app

From a repository checkout:

```bash
uv sync
uv run uvicorn --app-dir examples/showcase app:app --reload
```

Open <http://127.0.0.1:8000/>. The data is synthetic and local, but the application boundaries
are real: AppShell chrome, typed components, fragment refresh, an unsafe action, and ordinary
FastAPI-compatible routing.

## Explore the offline simulation

The simulator pre-renders the same kind of component surfaces and intercepts the declared HTMX
requests locally. Try refreshing the pipeline, filtering recent runs, approving the release, and
inspecting the component surface map.

<!-- hedron-sim:showcase-dashboard -->

The simulation is intentionally not a replacement for the real app. It demonstrates the browser
experience and request contracts without authentication, persistence, or a running worker.

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
