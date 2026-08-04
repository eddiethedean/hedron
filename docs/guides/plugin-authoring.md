# Plugin authoring

First-party and third-party plugins register components, assets, and optional Explorer
panels through the portable plugin protocol.

## Entry point

Declare a setuptools/importlib entry point that points at a `register(ctx)` callable
exposing `PLUGIN_META`:

```python
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta

PLUGIN_META = PluginMeta(
    name="my_plugin",
    version="0.8.0",  # keep aligned with your distribution version
    distribution="my-hedron-plugin",
    hedron_version=">=0.8,<0.9",
    capabilities=PluginCapabilities(python=True, styles=True, assets=True),
)


def register(ctx: PluginContext) -> None:
    # register_component / register_asset / ...
    ...


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
```

## Version gates

- `PLUGIN_META.version` should match the published package version for first-party plugins.
- `hedron_version` constrains which Hedron trains load the plugin.
- Incompatible plugins fail at load with a clear diagnostic—do not silently no-op.

## Security

- Do not ship active script / dangerous URL schemes in registered SVG icons.
- Prefer package resources for assets; avoid remote asset URLs unless policy allows.

## Testing

- Load the plugin in a unit test via the same entry-point path CI uses.
- Assert registration side effects (component ids, assets) without FastAPI when possible.

## See also

- [Plugins API](../api/PLUGINS.md)
- Sample kit: `packages/hedron-sample-kit`
- [STABILITY](../api/STABILITY.md)
