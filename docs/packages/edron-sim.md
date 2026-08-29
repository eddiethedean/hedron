# edron-sim

Static simulations for real Edron applications.

**Package maturity:** Beta tooling-grade · **Repository package version:** `0.1.0` ·
pin `>=0.1.0,<0.2`
**Import:** `edron_sim` · **Flagship extra:** none — install directly

`edron-sim` invokes the registered callbacks of an `edron.App` through the
public `App.simulation()` boundary. It does not inspect private Edron state from
the satellite package and does not require a second UI-authoring DSL.

## Install

```bash
pip install "edron-sim>=0.1.0,<0.2"
```

## Quick start

```python
from edron_sim import Simulation

artifact = Simulation.from_app(
    app,
    fixtures={"current_user": demo_user},
).build()

html = artifact.embed()
manifest = artifact.manifest
```

The generated HTML is intended for static documentation and showcase pages. It
uses the existing `hedron-sim` browser runtime, so the documentation site must
load that package's JavaScript and optional CSS assets.

## Supported boundary

- real Edron page, fragment, and action callbacks
- page/component/theme rendering through Edron and Hedron
- explicit fixture injection for app-owned dependencies
- bounded route and HTML output sizes
- deterministic `refresh` outcome effects for rendered Edron fragments
- a JSON-serializable route/source manifest for inspection and tests

## Deliberate non-goals

This is not a server emulator. It does not provision or impersonate a database,
authentication provider, cache, job worker, network, websocket/SSE transport, or
arbitrary browser JavaScript runtime. Build callbacks should be deterministic and
side-effect free; live production behavior remains authoritative in the Edron
ASGI application.

## API

| Symbol | Role |
|---|---|
| `Simulation.from_app(app)` | Build from a real Edron app |
| `Simulation.build()` / `.build_async()` | Produce a static artifact |
| `SimulationArtifact.embed()` | Return the HTML island |
| `SimulationArtifact.manifest` | Inspect bounded route/source metadata |
| `SimulationConfig` | Configure entrypoint and bounds |

See also [the package catalog](index.md), [Edron's API](../api/EDRON.md), and
[`hedron-sim`](hedron-sim.md).
