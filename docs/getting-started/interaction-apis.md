# Which interaction API?

Hedron 1.0 has one ordinary interaction model. Use `@app.view` for safe replaceable reads and
`@app.action` for unsafe operations; describe local or combined browser behavior with
`Interaction`. `HedronRouter` remains the Advanced escape hatch for an explicit selector or raw
HTTP boundary.

| Use this | When |
|---|---|
| `@app.view` + `@app.action` | Canonical function roles. Views own replaceable handles; actions own unsafe requests and outcomes. |
| `HedronRouter.view` / `HedronRouter.action` | Advanced route integration when a lower-level HTTP/target contract is required. |

Both compile to the same fail-closed fragment/OOB stack. The 0.67 helper spellings remain only as
warning-backed migration paths.

## Canonical: view and action

```python
from hedron import Hedron, Stack, Text, html

app = Hedron(title="Demo", security="standard", session_secret="dev", explorer="off")


@app.view("/status")
def status():
    return html.div(Text("ok"), role="status")


@app.action("/ping")
def ping():
    from hedron import refresh

    return refresh(status).toast("Refreshed")


@app.page("/")
def home():
    return Stack(
        status(),
        html.button("Refresh", hx_get=status.path),
        html.button("Ping", hx_post="/ping"),
    )
```

Continue: [Build your first app](quickstart.md) →
[HTMX interactions](../guides/htmx-interactions.md) →
[Interaction](../api/INTERACTION.md).

## Explicit: region and fragment

```python
status = app.region("service-status")


def status_panel():
    return html.div(Text("ok"), id=status.id)


@app.view("/status", fragment_regions=(status,))
def refresh_status():
    return swap(status_panel())
```

Continue: [Interaction](../api/INTERACTION.md).

## Flask and Django

Adapter hosts use `hedron_route` / `hedron_view` rather than FastAPI's `@app.view`.
See [Flask](flask.md) and [Django](django.md).
