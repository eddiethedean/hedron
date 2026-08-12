# hedron-native

[![PyPI](https://img.shields.io/pypi/v/hedron-native.svg)](https://pypi.org/project/hedron-native/)
[![crates.io](https://img.shields.io/crates/v/hedron-native.svg)](https://crates.io/crates/hedron-native)
[![Python](https://img.shields.io/pypi/pyversions/hedron-native.svg)](https://pypi.org/project/hedron-native/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Optional Rust acceleration for Hedron bulk HTML escaping.

Pure Python remains the semantic reference and Supported fallback. Absence of
the extension never changes public rendering semantics — `hedron-core` uses these
helpers when the package is installed and falls back otherwise.

Also available as the flagship extra `hedron[native]`.

**Package maturity:** Beta (`0.1.x`) · pin `>=0.1.2,<0.2` and expect churn

## Install

```bash
pip install "hedron-native>=0.1.2,<0.2"
# or
uv add "hedron-native>=0.1.2,<0.2"
# via flagship:
pip install "hedron[native]>=0.30.0,<0.31"
```

Requires Python 3.11–3.14. Prebuilt wheels for the Supported matrix are built by `native-wheels.yml` (confirm Supported tags on PyPI);
if a wheel is unavailable, pip may build from the Rust source (requires a Rust
toolchain) or you can rely on the pure-Python path without this package.

## Quick start

```python
from hedron_native import (
    escape_attr,
    escape_attr_python,
    escape_text,
    escape_text_python,
    native_available,
)

assert escape_text("<x>") == "&lt;x&gt;"
assert escape_attr('"') == "&quot;"

# Always available, even when the extension did not load:
assert escape_text_python("<x>") == "&lt;x&gt;"
assert escape_attr_python('"') == "&quot;"

print("native extension loaded:", native_available())
```

## Public API

| Symbol | Role |
|---|---|
| `escape_text` / `escape_attr` | Prefer native when loaded; else Python |
| `escape_text_python` / `escape_attr_python` | Pure-Python reference |
| `native_available` | `True` when the Rust extension loaded |
| `__version__` | Package version string |

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-native/)
- [PyPI](https://pypi.org/project/hedron-native/)
- [crates.io](https://crates.io/crates/hedron-native)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-native/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-native)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron-core`](https://pypi.org/project/hedron-core/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
