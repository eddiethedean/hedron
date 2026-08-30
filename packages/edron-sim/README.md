# edron-sim

[![PyPI](https://img.shields.io/pypi/v/edron-sim.svg)](https://pypi.org/project/edron-sim/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Build a static, interactive preview from a real Edron application. `edron-sim`
executes the app's registered pages, fragments, and actions through Edron's
public simulation boundary and renders the result into the existing offline
HTMX runtime.

**Package maturity:** Beta tooling-grade (`0.1.x`) · pin `>=0.1.0,<0.2`

## Install

```bash
pip install "edron-sim>=0.1.0,<0.2"
```

## Quick start

```python
from edron_sim import Simulation

# `app` is the real edron.App from your application module.
artifact = Simulation.from_app(app, fixtures={"current_user": demo_user}).build()
print(artifact.embed())
```

The output is a static HTML island. Load the `hedron-sim` JavaScript and CSS
assets in the documentation site, as described in the `hedron-sim` package
documentation.

The application source remains ordinary Edron code:

```python
import edron as ed

app = ed.App(title="Operations")


@app.page("/", title="Home")
class Home(ed.Page):
    def render(self) -> None:
        self.heading("Hello from Edron")
```

`edron-sim` does not introduce a component DSL, fake database, fake identity
provider, browser JavaScript engine, or live server. Supply bounded fixtures for
application-owned dependencies and keep side effects out of build-time render
callbacks.

## Public API

| Symbol | Role |
|---|---|
| `Simulation.from_app(app)` | Create a builder around a real `edron.App` |
| `Simulation.build()` | Synchronously build a static artifact |
| `Simulation.build_async()` | Async equivalent for async build pipelines |
| `SimulationArtifact.embed()` | Return the generated HTML island |
| `SimulationArtifact.manifest` | Bounded route and source manifest |
| `SimulationConfig` | Entrypoint and resource bounds |

## Scope

The supported surface is intentionally narrow: Edron pages, fragments, actions,
themes, deterministic fixtures, and bounded refresh effects. Authentication,
databases, queues, network calls, websockets, server-sent events, arbitrary
browser JavaScript, and pixel-perfect execution of arbitrary CSS remain live-app
concerns.

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/edron-sim/)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/edron-sim)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/edron-sim/CHANGELOG.md)
- [`hedron-sim`](https://pypi.org/project/hedron-sim/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
