---
status: shipped
---

# Plugins API

**Status:** Accepted · **Shipped in 0.4**

Plugins declare an entry point in group `hedron.plugins` pointing at a callable that
receives a `PluginContext`.

```toml
# pyproject.toml of the plugin distribution
[project.entry-points."hedron.plugins"]
sample_kit = "hedron_sample_kit.plugin:register"
```

```python
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta

PLUGIN_META = PluginMeta(
    name="sample_kit",
    version="0.4.0",
    distribution="hedron-sample-kit",
    hedron_version=">=0.4,<0.5",
    capabilities=PluginCapabilities(python=True, styles=True, explorer_panels=True),
)


def register(ctx: PluginContext) -> None:
    ctx.register_component(
        logical_id="hedron-sample-kit:callout.Callout",
        name="Callout",
        module="hedron_sample_kit.components.Callout",
        distribution="hedron-sample-kit",
    )
    ctx.register_explorer_panel(panel_id="sample-kit-callout", title="Sample Callout")
    ctx.on_startup(lambda: None)
    ctx.on_shutdown(lambda: None)


register.PLUGIN_META = PLUGIN_META
```

## `PluginContext` helpers

| Method | Purpose |
|---|---|
| `register_component(**kwargs)` | Contribute a component to the registry |
| `register_browser_module(**kwargs)` | Contribute a browser module |
| `register_explorer_panel(**kwargs)` | Contribute an Explorer panel |
| `register_diagnostic_owner(prefix)` | Own a diagnostic code prefix |
| `on_startup(hook)` / `on_shutdown(hook)` | Lifespan hooks |

`PluginContext` never grants private globals.

## Enablement

`[tool.hedron].plugins`:

- **omit / `null`**: discover and load all entry points
- **`[]`**: load none
- **name list**: load only those names; missing names raise `HED-PLUGIN-MISSING`

Failed compatibility or contribution validation rolls back the registry builder and
Explorer panels. `start()` failures also roll back contributions.

See `hedron-sample-kit` for a complete third-party-shaped example.
