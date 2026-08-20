# hedron-sample-kit

Third-party-shaped sample Hedron plugin package.

**Package maturity:** Beta tooling-grade · **Current compatible release:** `0.2.0`
**Flagship extra:** none — install directly · **Import:** `hedron_sample_kit`  
The repository source targets living Hedron train `0.54.x` (checkout tip `v0.54.0`;
PyPI consumers stay on `hedron-core>=0.52.0,<0.53` while deferred). Reference / demo
only — not an app framework.

## Install

```bash
pip install "hedron-sample-kit>=0.2.0,<0.3"
```

Versions through `0.1.6` target older Hedron cores; keep the `>=0.1.10` floor. Details:
[Compatibility](../COMPATIBILITY.md#charts-and-sample-kit-compatibility-floor).

Enable the plugin in your app’s `pyproject.toml`:

```toml
[tool.hedron]
plugins = ["sample_kit"]
```

## When to use

- Learning the `hedron.plugins` entry-point layout
- Copying a known-good component folder shape (Python + CSS + assets + examples)

For real plugins, follow [Plugin authoring](../guides/plugin-authoring.md) and study
this package’s source as the reference shape.

## Quick start

```python
from hedron_sample_kit.components.Callout import Callout

callout = Callout(message="Plugin components load via entry points.")
```

Or discover `Callout` in the Component Explorer when `hedron[dev]` is installed and
the plugin is enabled.

## Surfaces

| Surface | Role |
|---|---|
| `hedron.plugins` entry point `sample_kit` | Registers component, styles, assets, Explorer panel |
| `Callout` / `CalloutProps` | Sample component |
| `EXAMPLES` / `default` | Named Explorer examples |
| Diagnostic owner metadata | Demonstrates ownership hooks |

Package `__init__` exports `__version__` only; import components from their modules.

## Layout reference

```text
hedron_sample_kit/
  plugin.py                 # register(ctx)
  components/Callout/
    __init__.py             # Callout + CalloutProps
    styles.css
    examples.py
```

## Errors and failure modes

| Condition | Behavior |
|---|---|
| Plugin not listed in `[tool.hedron].plugins` | Sample components not registered |
| Treating as production UI kit | Out of scope — reference shape only |

## Related docs

- [Plugin authoring](../guides/plugin-authoring.md)
- [Plugins API](../api/PLUGINS.md)
- [Using plugins](../guides/plugin-consumer.md)

## Links

- [PyPI](https://pypi.org/project/hedron-sample-kit/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-sample-kit/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-sample-kit)
