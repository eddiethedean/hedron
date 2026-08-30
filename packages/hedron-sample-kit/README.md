# hedron-sample-kit

[![PyPI](https://img.shields.io/pypi/v/hedron-sample-kit.svg)](https://pypi.org/project/hedron-sample-kit/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-sample-kit.svg)](https://pypi.org/project/hedron-sample-kit/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Third-party-shaped sample Hedron plugin package.

Demonstrates a component (`Callout`), styles, asset, named example, Explorer
panel, and diagnostic owner via the `hedron.plugins` entry point. Use it as a
reference when authoring your own plugin distribution.

**Package maturity:** Beta tooling-grade · **compatible release:** `0.1.10`

## Install

```bash
pip install "hedron-sample-kit>=0.2.3,<0.3"
```

Versions through `0.2.2` target older plugin contracts; keep the `>=0.2.3` floor. See
[Compatibility](https://hedron.readthedocs.io/en/latest/COMPATIBILITY/#charts-and-sample-kit-compatibility-floor).

Enable the plugin in your app’s `pyproject.toml`:

```toml
[tool.hedron]
plugins = ["sample_kit"]
```

## Usage

After install and enablement, import and render the sample component:

```python
from hedron_sample_kit.components.Callout import Callout

callout = Callout(message="Plugin components load via entry points.")
```

Or discover it through the Component Explorer when `hedron[dev]` is installed.

## What this package demonstrates

- `hedron.plugins` entry-point registration
- Component folder layout (Python + CSS + assets + examples)
- Explorer panel registration
- Diagnostic owner metadata

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-sample-kit/)
- [Plugin authoring](https://hedron.readthedocs.io/en/latest/guides/plugin-authoring/)
- [Plugins API](https://hedron.readthedocs.io/en/latest/api/PLUGINS/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-sample-kit/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-sample-kit)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron-core`](https://pypi.org/project/hedron-core/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
