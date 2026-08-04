# Plugin authoring

First-party and third-party plugins register components, assets, and optional Explorer
panels through the portable plugin protocol. Study
[`hedron-sample-kit`](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-sample-kit)
alongside this guide.

## 1. Package layout

```text
my_hedron_plugin/
  pyproject.toml
  src/my_hedron_plugin/
    __init__.py
    plugin.py
    components/Callout/
      __init__.py          # Callout component + CalloutProps
      styles.css
      examples.py
```

## 2. Entry point

In `pyproject.toml`:

```toml
[project.entry-points."hedron.plugins"]
my_plugin = "my_hedron_plugin.plugin:register"
```

## 3. Register

```python
# plugin.py
from __future__ import annotations

from pathlib import Path

from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta

_ROOT = Path(__file__).resolve().parent
_COMPONENT = _ROOT / "components" / "Callout"

PLUGIN_META = PluginMeta(
    name="my_plugin",
    version="0.10.0",  # keep aligned with your distribution version
    distribution="my-hedron-plugin",
    hedron_version=">=0.10,<0.11",
    capabilities=PluginCapabilities(python=True, styles=True, assets=True),
)


def register(ctx: PluginContext) -> None:
    ctx.register_component(
        logical_id="my-hedron-plugin:callout.Callout",
        name="Callout",
        module="my_hedron_plugin.components.Callout",
        distribution="my-hedron-plugin",
        props_model="CalloutProps",
        styles_path=str(_COMPONENT / "styles.css"),
        folder_path=str(_COMPONENT),
        asset_roots=(str(_COMPONENT),),
        examples=("default",),
    )


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
```

## 4. Version gates

- `PLUGIN_META.version` should match the published package version
- `hedron_version` constrains which Hedron trains load the plugin
- Incompatible plugins fail at load with `HED-PLUGIN-0002` — do not silently no-op

## 5. Assets, CSP, and Explorer

- Prefer package resources for assets; avoid remote asset URLs unless policy allows
- Do not ship active script / dangerous URL schemes in registered SVG icons
- Optional: `ctx.register_explorer_panel(...)` for Explorer UI (see sample kit)
- Optional: `ctx.register_diagnostic_owner("HED-MINE-")` for plugin-owned codes

## 6. Test without FastAPI

```python
from hedron_core.plugins import PluginContext
from my_hedron_plugin.plugin import PLUGIN_META, register

def test_registers() -> None:
    ctx = PluginContext(PLUGIN_META)
    register(ctx)
    # assert registry contains your logical_id / assets
```

Load the plugin in CI via the same entry-point path production uses.

## See also

- [Plugins API](../api/PLUGINS.md) · [Error codes](error-codes.md) · [STABILITY](../api/STABILITY.md)
- Sample kit: `packages/hedron-sample-kit`
