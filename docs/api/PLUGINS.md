---
status: shipped
---

# Plugins API


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).
    Package maturity (Beta/Alpha) is separate from API level
    (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted · **Shipped in 0.4**

Plugins declare an entry point in group `hedron.plugins` pointing at a callable that
receives a `PluginContext`. Discovery and loading live in `hedron_core.plugin_loader`
(`load_plugins`); the FastAPI package re-exports the same API as `hedron.plugins`.

```toml
# pyproject.toml of the plugin distribution
[project.entry-points."hedron.plugins"]
sample_kit = "hedron_sample_kit.plugin:register"
```

```python
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta

PLUGIN_META = PluginMeta(
    name="sample_kit",
    version="0.1.0",
    distribution="hedron-sample-kit",
    hedron_version=">=0.25,<0.26",
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

### `register_component`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `logical_id` | `str` | required | Stable registry id |
| `name` | `str` | required | Display / catalog name |
| `module` | `str` | required | Import path of the component class |
| `distribution` | `str` | `"hedron-core"` | Owning distribution name |
| `props_model` | `str \| None` | `None` | Optional props model path |
| `slots` | mapping | `None` | Slot name → type hints |
| `examples` | iterable of `str` | `()` | Example snippets |
| `docs` | `str \| None` | `None` | Docs URL or text |
| `accessibility_notes` | `str \| None` | `None` | A11y notes for Explorer |
| `styles_path` | `str \| None` | `None` | Scoped CSS path |
| `browser_modules` | iterable of `str` | `()` | Linked browser module ids |
| `asset_roots` | iterable of `str` | `()` | Static asset roots |
| `style_symbols` | mapping | `None` | Style symbol map |
| `folder_path` | `str \| None` | `None` | Optional component folder |

**Returns:** `None` (registers into the global registry).

### `register_browser_module`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `logical_id` | `str` | required | Registry id |
| `tag_name` | `str` | required | Custom element tag |
| `module_path` | `str` | required | JS module path |
| `observed_attributes` | iterable of `str` | `()` | Observed attrs |
| `events` | iterable of `str` | `()` | Emitted event names |
| `shadow_dom` | `bool` | `False` | Use shadow DOM |
| `htmx_lifecycle` | `bool` | `True` | Participate in HTMX lifecycle |

### `register_explorer_panel`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `panel_id` | `str` | required | Unique panel id |
| `title` | `str` | required | Panel title |
| `description` | `str` | `""` | Short description |
| `path` | `str` | `""` | Optional panel path |

### Lifecycle

| Method | Purpose |
|---|---|
| `on_startup(hook)` / `on_shutdown(hook)` | Lifespan hooks (`Callable[[], None]`) |
| `register_diagnostic_owner(prefix)` | Own a diagnostic code prefix |

`PluginContext` never grants private globals.

## Enablement

`[tool.hedron].plugins`:

- **omit / `null`**: discover and load all entry points
- **`[]`**: load none
- **name list**: load only those names; missing names raise `HED-PLUGIN-0001`

Failed compatibility or contribution validation rolls back the registry builder and
Explorer panels. `start()` failures also roll back contributions.

Adopter walkthrough (install / review / deny-by-default):
[Using plugins](../guides/plugin-consumer.md) · [Plugin authoring](../guides/plugin-authoring.md).

## Errors

| Situation | Behavior |
|---|---|
| Missing named plugin in `[tool.hedron].plugins` | `HED-PLUGIN-0001` |
| Incompatible `hedron_version` range | `HED-PLUGIN-0002`; contributions rolled back |
| Duplicate entry point / invalid contribution | `HED-PLUGIN-0004` + rollback |
| `start()` hook failure | `HED-PLUGIN-0005`; contributions rolled back |

See `hedron-sample-kit` for a complete third-party-shaped example.
