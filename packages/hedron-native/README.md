# hedron-native

**Maturity:** Alpha (phase 0.14)

Optional Rust acceleration for Hedron bulk HTML escaping. Pure Python remains the
semantic reference and Supported fallback (D-001 / D-048). Absence of the extension
never changes public semantics.

```bash
pip install "hedron-native>=0.1.0"
# or from the monorepo:
uv sync
```

```python
from hedron_native import escape_text, escape_attr, native_available

assert escape_text("<x>") == "&lt;x&gt;"
```

`hedron-core` optionally uses these helpers when the package is installed.
