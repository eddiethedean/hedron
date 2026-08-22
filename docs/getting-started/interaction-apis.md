# Which interaction API?

Hedron has two ways to swap HTML into a page. **Start with refreshable views.** Use
`app.region` / `@app.fragment` only when you need an explicit selector allowlist.

| Use this | When |
|---|---|
| `@app.refreshable` + `@app.command` | Default. What `hedron new` generates. Named views and commands with handles (`status()`, `status.refresh_button(...)`, `refresh(status)`). |
| `app.region` + `@app.fragment` + `RefreshButton.for_region` | Explicit HTMX target allowlist, custom selectors, or you are maintaining pre-0.43 code. |

Both compile to the same fail-closed fragment/OOB stack. Neither is deprecated.

## Default: refreshable and command

```python
from hedron import Hedron, Stack, Text, html

app = Hedron(title="Demo", security="standard", session_secret="dev", explorer="off")


@app.refreshable("/status")
def status():
    return html.div(Text("ok"), role="status")


@app.command(fallback="/")
def ping():
    from hedron import refresh

    return refresh(status).toast("Refreshed")


@app.screen("/", title="Home")
def home():
    return Stack(status(), status.refresh_button("Refresh"), ping.button("Ping"))
```

!!! note "Advanced — explicit `@app.page`"

    Prefer `@app.screen` for new golden paths. Use `@app.page` + `Page(...)` when you need
    full document constructor control.

Continue: [Build your first app](quickstart.md) →
[HTMX interactions](../guides/htmx-interactions.md) →
[Refreshable views](../api/REFRESHABLE_VIEWS.md).

## Explicit: region and fragment

```python
status = app.region("service-status")


def status_panel():
    return html.div(Text("ok"), id=status.id)


@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())
```

Continue: [Interaction](../api/INTERACTION.md).

## Flask and Django

Adapter hosts use `hedron_route` / `hedron_view` rather than `@app.refreshable`.
See [Flask](flask.md) and [Django](django.md).
