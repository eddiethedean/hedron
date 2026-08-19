---
status: beta
---

# Curated extras (0.51)

Phase 0.51 (D-087 / D-088 / RFC-0078) is **Stage 0 only**: contracts and
inventories. It does **not** ship runtime. Planning baseline is Published
in-tree `v0.50.3`. Tracking
[#507](https://github.com/eddiethedean/hedron/issues/507). Related authoring
[#504](https://github.com/eddiethedean/hedron/issues/504)–[#506](https://github.com/eddiethedean/hedron/issues/506)
is flagship HTMX, not extras gates. Living tip remains `v0.50.3`.

Shipped 0.50 extras install remains
[hedron-extras](../packages/hedron-extras.md). This page is the 0.51
lifecycle contract.

## Example (0.50.3, unchanged)

```python
from hedron_extras import MetricCard

card = MetricCard(label="Active users", value="1,284", hint="+12% WoW")
```

Install `hedron[extras]`. Experimental UI requires
`hedron[experimental-ui]` plus `HEDRON_EXPERIMENTAL_UI=1` or an explicit
plugin enable. Import landmines from `hedron_extras.experimental`.

## Descriptor

`ExtrasFeature` is additive in `hedron-extras`. It is the package inventory
authority (component tag, facade, schemas, events, assets, optional
dependencies, fallback, limits, maturity, accessibility contract,
Explorer/Jinja/conformance projections). It consumes today's
`PluginContext.register_feature` / `feature_specs`. It does **not** replace
`FeatureBundle` or `InteractionCatalog` and is not a `hedron-core` catalog.

## Dispositions

| Surface | 0.51 lock |
|---|---|
| Composition, workbench, editors, image tools, display | Supported *targets* after evidence |
| Recipes (`AvatarProfile`, `BadgeLink`, `MetricCard`, `TodoList`) | Stay `recipe` unless promoted |
| `BrowserPythonSandbox` | **Experimental**; not in Supported `hedron[extras]`; Stage 1 opt-in registration |
| `CodeEditor` | **Experimental** host stub; no CodeMirror 6 graduation |
| `TerminalView`, `Joystick`, `DeviceBridge` | **Experimental**; remain `hedron[experimental-ui]` |

## Companion authoring

Password visibility (#504), swap reveal (#505), and generic HTMX busy
(#506) belong to the flagship. They do not graduate Experimental UI.

## Errors

Reserve `HED-EXTRAS-FEATURE-*` in docs only at Stage 0. Keep existing
`HED-EXTRAS-` / `HED-ASSET-MISSING`. No new runtime codes in this refine.

## See also

[RFC-0078](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0078-CURATED-EXTRAS-LIFECYCLE.md) ·
[implementation](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EXTRAS_051.md) ·
[What’s ready](../guides/whats-ready.md) ·
[Plugins](PLUGINS.md)
