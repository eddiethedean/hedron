# hedron-sim

[![PyPI](https://img.shields.io/pypi/v/hedron-sim.svg)](https://pypi.org/project/hedron-sim/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-sim.svg)](https://pypi.org/project/hedron-sim/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Offline HTMX simulation for Hedron docs and demos.

Author demos with ordinary Hedron components (`Page`, `RefreshButton`, `swap`,
regions), then embed them in static docs. A small JavaScript runtime intercepts
`hx-*` attributes and serves pre-rendered fragment HTML — no FastAPI process
required.

**Package maturity:** Beta tooling-grade (`0.2.x`) · pin `>=0.2.0,<0.3`

## Install

```bash
pip install "hedron-sim>=0.2.0,<0.3"
# or
uv add "hedron-sim>=0.2.0,<0.3"
```

Requires Python 3.10–3.14 and `hedron` (for component imports used in demos).

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


@app.fragment("/status", region=status)  # SimApp package-native simulator route
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

Then load `hedron-sim.js` (and optionally `hedron-sim.css`) from MkDocs
`extra_javascript` / `extra_css`.

## Public API

| Symbol | Role |
|---|---|
| `SimApp` | Offline app with `@page` / `@fragment` and regions |
| `embed_demo(app)` | HTML snippet for static docs |
| `sim_utc` / `sim_local_time` | Deterministic clock helpers for demos |
| `hedron_sim.assets.copy_assets` | Copy JS/CSS into a docs tree |

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-sim/)
- [Documentation](https://hedron.readthedocs.io/en/latest/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-sim/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-sim)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron`](https://pypi.org/project/hedron/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
