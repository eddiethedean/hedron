---
status: shipped
---

# Testing API


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Shipped in `0.4` · import from `hedron.testing`

| Helper | Signature (summary) | Returns | Purpose |
|---|---|---|---|
| `render_html` | `(node, *, mode=FRAGMENT)` | `str` | Render HTML string |
| `assert_renders` | `(node, *, contains, mode=FRAGMENT)` | `str` | Assert substring; return HTML |
| `assert_render_result` | `(result, *, contains)` | `None` | Assert against `RenderResult` |
| `fragment_client` | `(app)` | context manager | `TestClient` with HTMX fragment headers |
| `override_dependencies` | `(app, overrides)` | context manager | Temporary FastAPI `dependency_overrides` |
| `named_example` / `iter_named_examples` | registry helpers | examples | Named component examples |
| `normalize_snapshot_html` | `(html)` | `str` | Normalize fingerprinted asset hashes only |

```python
from hedron.testing import assert_renders, fragment_client, render_html
from hedron_core import Text

html = render_html(Text("hello"))
assert_renders(Text("world"), contains="world")

with fragment_client(app) as client:
    response = client.get("/status")
    assert response.status_code == 200
```

Optional browser extras live under `hedron.testing.browser` (`playwright()` context
manager; `axe_scan`) and require `hedron[browser]`.

## Errors

| Condition | Behavior |
|---|---|
| `assert_renders` miss | AssertionError with rendered HTML context |
| Browser extras missing | Import/install error pointing at `hedron[browser]` |

## See also

[Testing guide](../guides/testing.md)
