# hedron-native

Optional Rust acceleration for Hedron bulk HTML escaping.

**Package maturity:** Beta (`0.1.x`) · pin `>=0.1.2,<0.2`
**Flagship extra:** `hedron[native]` · **Import:** `hedron_native`
Pure Python remains the **Supported** semantic fallback. Absence never changes
public rendering semantics.

!!! warning "Not the desktop shell"

    This package accelerates HTML escaping. The
    [native desktop shell recipe](../guides/native-desktop-shell.md) is a separate
    docs-only guide under `hedron-extras` / packaging recipes.

## Install

```bash
pip install "hedron[native]>=0.66.2,<0.67"
# or
pip install "hedron-native>=0.1.2,<0.2"
```

Supported wheel tags cover **manylinux x86_64 + aarch64**, **macOS arm64**, and
**Windows amd64** (CPython 3.11–3.14) via `native-wheels.yml` — confirm Supported
tags on PyPI. If a wheel is unavailable, pip may build from
Rust source (requires a Rust toolchain) — or omit the package and rely on pure Python.

## Disable native acceleration

Set `HEDRON_NATIVE_DISABLE=1` (also accepts `true` / `yes` / `on`) before process
start to force the pure-Python escape path even when the Rust extension is installed.
Use this for ops drills, parity checks, and `NATIVE-028` fallback evidence.
`hedron accel-status` reports when disable is active.

## When to use

- Hot paths that escape large volumes of HTML text/attributes
- Optional performance win without changing escape semantics

Do **not** require this package for correctness. `hedron-core` uses these helpers
when present and falls back otherwise.

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
print("native extension loaded:", native_available())
```

## Surfaces

| Symbol | Role |
|---|---|
| `escape_text` / `escape_attr` | Prefer native when loaded; else Python |
| `escape_text_python` / `escape_attr_python` | Pure-Python reference |
| `native_available()` | `True` when the Rust extension loaded |
| `__version__` | Package version string |

## Errors and failure modes

| Condition | Behavior |
|---|---|
| Extension not built / not installed | Pure-Python path; semantics unchanged |
| Expecting different escape rules vs Python | Out of scope — native must match reference |

## Related docs

- [Stability](../api/STABILITY.md)
- [Conformance kit](hedron-conformance.md) (portable escaping fixtures)
- Do not confuse with [Native desktop shell](../guides/native-desktop-shell.md)

## Links

- [PyPI](https://pypi.org/project/hedron-native/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-native/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-native)
