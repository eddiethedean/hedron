# Hedron Showcase

The polished, full-feature Hedron tour: a synthetic operations console composed from
server-rendered Python components.

It demonstrates AppShell chrome, metrics, alerts, process flows, progress, tables, resources,
timeline activity, an HTMX fragment refresh, a CSRF-protected action, multiple pages, and typed
status/feedback surfaces.

```bash
uv run uvicorn --app-dir examples/showcase app:app --reload
```

Open <http://127.0.0.1:8000/>. The data is synthetic and local; the application structure and
request boundaries are real.

For a no-server tour, open the [interactive `hedron-sim` showcase](https://hedron.readthedocs.io/en/latest/examples/showcase/).
