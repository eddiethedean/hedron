# hedron-sample-kit

[![PyPI](https://img.shields.io/pypi/v/hedron-sample-kit.svg)](https://pypi.org/project/hedron-sample-kit/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Third-party-shaped sample Hedron plugin package (Alpha; independent **`0.1.x`**,
compatible with `hedron-core>=0.12.0,<0.12`; first released with the 0.4 developer
platform). Demonstrates a component (`Callout`),
styles, asset, named example, Explorer panel, and diagnostic owner via the
`hedron.plugins` entry point.

## Install

```bash
pip install hedron-sample-kit
```

Enable in `[tool.hedron]`:

```toml
[tool.hedron]
plugins = ["sample_kit"]
```

## Links

- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-sample-kit/CHANGELOG.md)
- [Plugins acceptance](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/PLUGINS.md)
- [Source](https://github.com/eddiethedean/hedron)

## License

MIT. See [LICENSE](LICENSE).
