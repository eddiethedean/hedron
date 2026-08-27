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
    hedron_version=">=1.0,<2.0",
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
    ctx.register_explorer_provider(
        panel_id="sample-kit-callout",
        title="Sample Callout",
        description="Isolated 0.50 panel",
    )
    ctx.on_startup(lambda: None)
    ctx.on_shutdown(lambda: None)


register.PLUGIN_META = PLUGIN_META
```

## Parameters

| Symbol | Key inputs | Role |
|---|---|---|
| `PluginMeta` | `name`, `version`, `distribution`, `hedron_version`, `capabilities` | Declares plugin identity and train pin |
| `PluginContext` | (injected) | Registration surface for components, assets, panels, hooks |
| `[tool.hedron].plugins` | omit / `[]` / name list | Discovery enablement |

Field-level tables for each `PluginContext` helper are below.

## Returns

Plugin `register(ctx)` callables return `None`. Registration mutates the application
registry for the current load; failed loads roll back contributions (see Errors).

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

### `register_asset` (0.40)

Register a packaged asset for element modules/CSS without private registry imports.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `logical_id` | `str` | required | Stable asset id |
| `kind` | `str` | required | Asset kind (`module`, `style`, …) |
| `path` | `str` | required | Packaged path relative to the plugin |
| `digest` | `str` | required | Content digest |
| `content_type` | `str` | required | MIME type |
| `attributes` | mapping | `None` | Optional HTML attributes |

### `register_element_definition` (0.40)

Register a portable custom-element definition. Defaults to `first_party=False` for third-party
authors.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `logical_id` | `str` | required | Stable definition id |
| `tag_name` | `str` | required | Hyphenated custom-element tag |
| `abi_version` | `int` | required | Element ABI major |
| `module_asset_id` | `str` | required | Registered module asset id |
| `attributes` / `properties` / `methods` / `events` | iterable | `()` | Declared surfaces |
| `parts` | iterable of `str` | `()` | CSS parts |
| `slots` | mapping | `None` | Slot name → description |
| `tokens` | iterable of `str` | `()` | Theme token names |
| `first_party` | `bool` | `False` | Require `hedron-*` naming when true |

Guide: [Plugin authoring — custom elements](../guides/plugin-authoring.md#5-custom-elements-040).

### `register_explorer_panel`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `panel_id` | `str` | required | Unique panel id |
| `title` | `str` | required | Panel title |
| `description` | `str` | `""` | Short description |
| `path` | `str` | `""` | Optional panel path; does **not** add Explorer nav |

### `register_explorer_provider` (0.50)

Additive `ExplorerProvider` beside `ExplorerPanelMeta`. Explorer runs the panel on
`/packages` inside `run_isolated` (`HED-EXPLORER-0002` / `0003`).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `panel_id` | `str` | required | Unique panel id |
| `title` | `str` | required | Panel title |
| `description` | `str` | `""` | Short description |
| `path` | `str` | `""` | Optional panel path (no nav) |
| `timeout_ms` | `int` | `250` | Isolation timeout |
| `max_payload_bytes` | `int` | `65536` | Payload ceiling |

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

## See also

[Plugin authoring](../guides/plugin-authoring.md) · [Using plugins](../guides/plugin-consumer.md) ·
[`hedron-sample-kit`](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-sample-kit)
