---
status: beta
---

# Curated extras (0.51)

Phase 0.51 (D-087 / D-088 / RFC-0078) shipped in-tree as **`v0.51.0`**.
PyPI remains **`v0.50.1`** until upload. Tracking
[#507](https://github.com/eddiethedean/hedron/issues/507). Companion authoring
[#504](https://github.com/eddiethedean/hedron/issues/504)–[#506](https://github.com/eddiethedean/hedron/issues/506)
is flagship HTMX, not extras gates.

Shipped extras install remains
[hedron-extras](../packages/hedron-extras.md).

## Example

```python
from hedron_extras import MetricCard, ExtrasFeature

card = MetricCard(label="Active users", value="1,284", hint="+12% WoW")
```

Install `hedron[extras]`. Experimental UI requires
`hedron[experimental-ui]` plus `HEDRON_EXPERIMENTAL_UI=1` or an explicit
plugin enable. Import landmines from `hedron_extras.experimental`.

The browser-Python sandbox is Experimental. Default discovery skips
`hedron_extras_sandbox` unless `HEDRON_EXTRAS_SANDBOX=1` or the plugin is
explicitly enabled. Keep `from hedron_extras.sandbox import BrowserPythonSandbox`.

## Descriptor

`ExtrasFeature` is additive in `hedron-extras`. It is the package inventory
authority (component tag, facade, schemas, events, assets, optional
dependencies, fallback, limits, maturity, accessibility contract,
Explorer/Jinja/conformance projections). It consumes
`PluginContext.register_feature`. It does **not** replace
`FeatureBundle` or `InteractionCatalog` and is not a `hedron-core` catalog.

## Dispositions

| Surface | 0.51 lock |
|---|---|
| Composition, workbench, editors, image tools, display | Supported after evidence |
| Recipes (`AvatarProfile`, `BadgeLink`, `MetricCard`, `TodoList`) | Stay `recipe` unless promoted |
| `BrowserPythonSandbox` | **Experimental**; not in Supported `hedron[extras]`; opt-in `hedron_extras_sandbox` |
| `CodeEditor` | **Experimental** host stub; no CodeMirror 6 graduation |
| `TerminalView`, `Joystick`, `DeviceBridge` | **Experimental**; remain `hedron[experimental-ui]` |

## Companion authoring

Password visibility (#504) is built into `TextInput(type="password")` (and
generated password Controls). Swap reveal (#505) is `SwapReveal` — first paint
stays visible; after-swap replay honors `prefers-reduced-motion`. Generic HTMX
busy (#506) is opt-in via `BusyRegion` / `Hx(busy=...)` and does not mark
`document.body` busy for unmarked requests.

## Errors

Keep existing `HED-EXTRAS-` / `HED-ASSET-MISSING`. Reserved docs-only
`HED-EXTRAS-FEATURE-*`.

## See also

[RFC-0078](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0078-CURATED-EXTRAS-LIFECYCLE.md) ·
[implementation](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EXTRAS_051.md) ·
[What’s ready](../guides/whats-ready.md) ·
[Plugins](PLUGINS.md)
