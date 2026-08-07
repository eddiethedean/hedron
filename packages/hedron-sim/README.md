# hedron-sim

Alpha helper for **offline HTMX simulations**: author demos with ordinary Hedron
components (`Page`, `RefreshButton`, `swap`, regions), then embed them in static
docs. A small JavaScript runtime intercepts `hx-*` attributes and serves
pre-rendered fragment HTML — no FastAPI process required.

```python
from hedron import Page, RefreshButton, Stack, Text, html, swap
from hedron_sim import SimApp, embed_demo, sim_utc

app = SimApp(demo_id="hello-status")
status = app.region("service-status")


def status_panel():
    return html.div(
        Text(f"All systems operational · refreshed {sim_utc()}"),
        id=status.id,
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Hello from hedron-sim"),
            status_panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh status"),
        ),
        title="Demo",
    )


@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())


print(embed_demo(app))
```

Ship the JS/CSS assets into your static docs tree:

```python
from pathlib import Path
from hedron_sim.assets import copy_assets

copy_assets(Path("docs/javascript"), Path("docs/stylesheets"))
```

Then load `hedron-sim.js` (and optionally `hedron-sim.css`) from MkDocs
`extra_javascript` / `extra_css`.
