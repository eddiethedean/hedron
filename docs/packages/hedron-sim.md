# hedron-sim

Offline HTMX simulation for Hedron docs and demos.

**Package maturity:** Beta tooling-grade (`0.2.x`) · pin `>=0.2.0,<0.3`
**Flagship extra:** none — install directly · **Import:** `hedron_sim`  
Compatible with published Hedron train `0.60.x` (`v0.60.0` in-tree; PyPI `v0.59.0` until upload). Author demos
with ordinary Hedron components, then
embed them in **static** docs — no FastAPI process required.

## Install

```bash
pip install "hedron-sim>=0.2.0,<0.3"
```

Requires `hedron` / `hedron-core` for the component imports used in demos.

## When to use

- MkDocs / static documentation demos that need HTMX-like fragment swaps
- Capturing real Hedron component HTML without running a live server

This is **docs/demo tooling**, not an application server. Live apps should use
`Hedron` + uvicorn (or Flask / Django adapters).

## Quick start

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

### Ship static assets

```python
from pathlib import Path
from hedron_sim.assets import copy_assets

copy_assets(Path("docs/javascript"), Path("docs/stylesheets"))
```

Load `hedron-sim.js` (and optionally `hedron-sim.css`) from MkDocs
`extra_javascript` / `extra_css`. This documentation site already does so.

## Surfaces

| Symbol | Role |
|---|---|
| `SimApp` | Offline app with `@page` / `@fragment` and regions |
| `SimRoute` | Route metadata for the sim runtime |
| `embed_demo(app)` | HTML snippet for static docs |
| `render_handler_html` / `wrap_browser_chrome` | Lower-level embed helpers |
| `sim_utc` / `sim_local_time` | Deterministic clock helpers for demos |
| `sim_form` | Form helpers for offline demos |
| `hedron_sim.assets.copy_assets` | Copy JS/CSS into a docs tree |

A small JavaScript runtime intercepts `hx-*` attributes and serves pre-rendered
fragment HTML from the embed.

## Errors and failure modes

| Condition | Behavior |
|---|---|
| Missing JS/CSS in the docs site | Swaps will not run in the browser |
| Expecting a live ASGI server | Use `hedron` + uvicorn instead |
| Non-deterministic clocks in golden HTML | Prefer `sim_utc` / `sim_local_time` |

## Related docs

- Site assets: bundled via MkDocs `extra_javascript` / `extra_css`
- Runnable demos under Examples and Guides that embed sims
- [Optional packages overview](index.md)

## Links

- [PyPI](https://pypi.org/project/hedron-sim/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-sim/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-sim)
